import requests
import json
import re
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize
from config import Config

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class AIProcessor:
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
    
    def _generate_content(self, prompt, json_mode=False):
        """Helper to call Ollama API"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        if json_mode:
            payload["format"] = "json"
            
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get('response', '')
        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama API: {e}")
            raise

    def extract_text_from_resume(self, resume_text):
        """Extract key information from resume text"""
        prompt = f"""
        Extract the following information from this resume text:
        
        {resume_text[:2000]}
        
        Provide as JSON with these keys:
        - name: person's name (if available)
        - skills: list of technical skills
        - experience_years: total years of experience (as float)
        - education: list of educational qualifications
        - projects: list of key projects
        - certifications: list of certifications
        
        Return only JSON object.
        """
        
        try:
            response_text = self._generate_content(prompt, json_mode=True)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            # Or try parsing directly if mode worked well
            return json.loads(response_text)
        except Exception as e:
            print(f"Error extracting resume text: {e}")
            # Fallback for parsing error
            try:
                # Cleaner retry if mixed output
                return json.loads(response_text[response_text.find('{'):response_text.rfind('}')+1])
            except:
                return {}
    
    def generate_questions(self, resume_data, job_description, domain, experience_level, count=10):
        """Generate interview questions based on resume and JD"""
        prompt = f"""
        You are an technical interviewer. Generate {count} interview questions for a {experience_level} level {domain} position.
        
        Resume Information:
        {json.dumps(resume_data, indent=2)}
        
        Job Description:
        {job_description[:1000]}
        
        Generate a list of questions including:
        1. Technical questions specific to {domain}
        2. Behavioral questions (STAR method)
        3. Situational questions
        
        Return a JSON ARRAY of objects. Each object must have:
        - question_text: The question string
        - question_type: "technical", "behavioral", "situational", or "advanced"
        - difficulty: "easy", "medium", or "hard"
        - category: e.g., "Python", "System Design"
        - time_allocated: Time in seconds (e.g. 120)
        
        Return ONLY valid JSON.
        """
        
        try:
            response_text = self._generate_content(prompt, json_mode=True)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                return questions[:count]
            # Try direct parse
            return json.loads(response_text)[:count]
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_default_questions(domain, experience_level, count)
    
    def _get_default_questions(self, domain, experience_level, count):
        """Provide default questions if AI fails"""
        default_questions = [
            {
                "question_text": f"Tell me about your experience with {domain}.",
                "question_type": "behavioral",
                "difficulty": "easy",
                "category": domain,
                "time_allocated": 120
            },
            {
                "question_text": "Describe a challenging project you worked on and how you overcame obstacles.",
                "question_type": "behavioral",
                "difficulty": "medium",
                "category": "Project Management",
                "time_allocated": 180
            },
            {
                "question_text": "What are your strengths and weaknesses?",
                "question_type": "behavioral",
                "difficulty": "easy",
                "category": "Self Assessment",
                "time_allocated": 120
            }
        ]
        return default_questions[:count]
    
    def analyze_answer(self, question, answer, transcript):
        """Analyze candidate's answer"""
        # Use answer text for filler word and sentiment analysis
        # (transcript may be empty since speech text is merged into answer)
        analysis_text = answer if answer.strip() else transcript
        
        filler_words = ['um', 'uh', 'ah', 'er', 'like', 'you know', 'so', 'well']
        filler_count = sum(analysis_text.lower().count(word) for word in filler_words)
        
        # Calculate sentiment using TextBlob
        blob = TextBlob(analysis_text)
        sentiment_score = blob.sentiment.polarity  # -1 to 1
        
        # Check answer length for quality assessment
        word_count = len(analysis_text.split())
        
        # Generate AI feedback
        prompt = f"""
        Analyze this interview answer:

        Question: {question}
        Candidate's Answer: {answer}

        Provide detailed analysis as JSON with these keys:
        - grammar_score: 0-10 score
        - relevance_score: 0-10 score
        - star_score: 0-10 score for STAR method usage
        - detailed_feedback: Specific feedback text
        - suggested_better_answer: A better version of the answer
        - needs_cross_question: boolean (true if answer is vague/short)
        - cross_question: Follow-up question if needed (string)

        Return ONLY JSON.
        """
        
        try:
            response_text = self._generate_content(prompt, json_mode=True)
            
            # clean potential markdown
            response_text = response_text.replace('```json', '').replace('```', '')
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = json.loads(response_text)
                
            # Calculate confidence score (0-10)
            # Components:
            #   - 30% from AI relevance score (how on-topic the answer is)
            #   - 20% from AI STAR method score (structured answering)
            #   - 20% from sentiment analysis (positive/assertive tone)
            #   - 15% from filler word penalty (fewer fillers = more confident)
            #   - 15% from answer length adequacy (too short = not confident)
            length_score = min(10, word_count / 5)  # 50+ words = full marks
            sentiment_component = (1 + sentiment_score) * 5  # Convert -1..1 to 0..10
            filler_penalty = max(0, 10 - (filler_count * 1.0))  # Stronger penalty per filler
            
            confidence_score = (
                analysis.get('relevance_score', 0) * 0.30 +
                analysis.get('star_score', 0) * 0.20 +
                sentiment_component * 0.20 +
                filler_penalty * 0.15 +
                length_score * 0.15
            )
            
            # Round to 1 decimal place
            confidence_score = round(min(10, max(0, confidence_score)), 1)
            
            return {
                'grammar_score': analysis.get('grammar_score', 0),
                'relevance_score': analysis.get('relevance_score', 0),
                'star_score': analysis.get('star_score', 0),
                'confidence_score': confidence_score,
                'filler_words_count': filler_count,
                'feedback': analysis.get('detailed_feedback', 'No specific feedback available.'),
                'suggested_answer': analysis.get('suggested_better_answer', ''),
                'needs_cross_question': analysis.get('needs_cross_question', False),
                'cross_question': analysis.get('cross_question', '')
            }
        except Exception as e:
            print(f"Error analyzing answer: {e}")
        
        # Fallback analysis - low scores since we couldn't properly analyze
        return {
            'grammar_score': 3,
            'relevance_score': 3,
            'star_score': 2,
            'confidence_score': 3,
            'filler_words_count': filler_count,
            'feedback': 'Basic analysis only. AI service unavailable.',
            'suggested_answer': 'Try to provide more specific examples and structure your answer using the STAR method.',
            'needs_cross_question': len(answer.split()) < 30,
            'cross_question': 'Could you elaborate more on that point?' if len(answer.split()) < 30 else ''
        }
    
    def generate_cross_question(self, question, answer):
        """Generate a cross-question when answer is insufficient"""
        prompt = f"""
        Original Question: {question}
        Answer: {answer}
        
        The answer was too short/vague. Generate ONE follow-up question.
        Return just the question text.
        """
        
        try:
            return self._generate_content(prompt).strip()
        except:
            return "Could you provide a more detailed example or elaborate on that point?"
    
    def evaluate_code(self, problem_statement, user_code, language='python', execution_success=None, execution_error=None):
        """Evaluate submitted code"""
        # Build execution context for the AI prompt
        execution_info = ""
        if execution_success is not None:
            if execution_success:
                execution_info = "\nExecution Result: Code ran successfully without errors."
            else:
                execution_info = f"\nExecution Result: Code FAILED to run. Error: {execution_error or 'Unknown error'}"
        
        prompt = f"""
        Evaluate this coding solution:
        
        Problem: {problem_statement}
        Language: {language}
        Code:
        {user_code}
        {execution_info}
        
        IMPORTANT: Score strictly based on whether the code actually solves the problem.
        - If the code is just a template/boilerplate with no real logic, ALL scores should be 0.
        - If the code has syntax errors or fails to run, scores should be very low (0-2).
        - Only give high scores if the code actually implements a correct solution.
        
        Provide evaluation as JSON with:
        - logic_score: 0-10
        - efficiency_score: 0-10
        - clarity_score: 0-10
        - test_cases_passed: estimated test cases passed (0-5)
        - total_test_cases: 5
        - detailed_feedback: Specific feedback
        - suggested_improvements: How to improve
        - time_complexity: Big O
        - space_complexity: Big O
        
        Return ONLY JSON.
        """
        
        try:
            response_text = self._generate_content(prompt, json_mode=True)
             # clean potential markdown
            response_text = response_text.replace('```json', '').replace('```', '')

            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
            else:
                evaluation = json.loads(response_text)
            
            # If code failed to execute, cap scores at maximum 2
            if execution_success is False:
                for key in ['logic_score', 'efficiency_score', 'clarity_score']:
                    if key in evaluation:
                        evaluation[key] = min(evaluation[key], 2)
                evaluation['test_cases_passed'] = 0
            
            return evaluation
        except Exception as e:
            print(f"Error evaluating code: {e}")
        
        # Fallback evaluation - low scores since we couldn't evaluate
        return {
            'logic_score': 0,
            'efficiency_score': 0,
            'clarity_score': 0,
            'test_cases_passed': 0,
            'total_test_cases': 5,
            'detailed_feedback': 'Could not evaluate code. AI service unavailable.',
            'suggested_improvements': 'Ensure your code compiles and runs correctly.',
            'time_complexity': 'N/A',
            'space_complexity': 'N/A'
        }
    
    def generate_problem_statement(self, domain, difficulty='medium'):
        """Generate a coding problem statement"""
        prompt = f"""
        Generate a {difficulty} level coding problem for {domain} domain.
        
        Provide as JSON with:
        - problem_statement: Clear description
        - example_input: Example input
        - example_output: Expected output
        - constraints: Any constraints
        - hints: list of hints
        
        Return ONLY JSON.
        """
        
        try:
            response_text = self._generate_content(prompt, json_mode=True)
            # clean potential markdown
            response_text = response_text.replace('```json', '').replace('```', '')

            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response_text)
        except:
            pass
        
        # Default problem
        return {
            'problem_statement': 'Write a function to find the maximum element in a list.',
            'example_input': '[1, 5, 3, 9, 2]',
            'example_output': '9',
            'constraints': 'Time complexity should be O(n)',
            'hints': ['Iterate through the list while keeping track of maximum']
        }
    
    def generate_final_report(self, session_data, answers_data, coding_data):
        """Generate final performance report"""
        prompt = f"""
        Generate an interview performance report.
        
        Domain: {session_data.get('domain')}
        Level: {session_data.get('experience_level')}
        
        Performance:
        {json.dumps(answers_data, indent=2)}
        
        Coding:
        {json.dumps(coding_data, indent=2) if coding_data else 'No coding test'}
        
        Provide detailed report as JSON with:
        - overall_score: 0-100
        - strengths: list of 3-5 items
        - weaknesses: list of 3-5 items
        - communication_score: 0-10
        - technical_score: 0-10
        - confidence_score: 0-10
        - improvement_plan: list of 5-7 items
        - final_verdict: "Strong Candidate", "Needs Improvement", or "Not Ready"
        - detailed_analysis: a paragraph
        
        Return ONLY JSON.
        """
        
        try:
            response_text = self._generate_content(prompt, json_mode=True)
            # clean potential markdown
            response_text = response_text.replace('```json', '').replace('```', '')

            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response_text)
        except Exception as e:
            print(f"Error generating report: {e}")
        
        # Fallback report
        return {
            'overall_score': 70,
            'strengths': ['Basic technical knowledge', 'Clear communication'],
            'weaknesses': ['Need more examples', 'Improve STAR method usage'],
            'communication_score': 7,
            'technical_score': 6,
            'confidence_score': 6,
            'improvement_plan': [
                'Practice more behavioral questions',
                'Use STAR method consistently',
                'Reduce filler words',
                'Prepare specific examples'
            ],
            'final_verdict': 'Needs Improvement',
            'detailed_analysis': 'Basic performance with room for improvement.'
        }