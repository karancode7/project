# AI Interview Coach — Complete Project Documentation

## 1. Project Overview

**AI Interview Coach** is a web-based interview practice platform that uses AI (Ollama/LLaMA) to simulate realistic interviews. Users upload a resume and job description, then face AI-generated questions tailored to their profile. The system evaluates answers in real-time, conducts a coding test, and produces a comprehensive performance report.

### Key Capabilities
- **Resume-aware question generation** — Questions are custom-generated based on the candidate's resume and job description
- **Speech recognition** — Candidates can answer via browser speech-to-text (Web Speech API)
- **Real-time scoring** — Each answer is scored for grammar, relevance, confidence, and STAR method usage
- **Coding sandbox** — A secure Python execution environment for coding challenges
- **AI-powered evaluation** — Ollama LLaMA 3.2 evaluates both interview answers and code
- **PDF report generation** — Final performance report with detailed analysis

---

## 2. System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     BROWSER (Frontend)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ HTML/CSS/JS  │  │ Web Speech   │  │   Camera Feed        │   │
│  │ Tailwind CSS │  │ API          │  │   (camera.js)        │   │
│  │ + Jinja2     │  │ (speech.js)  │  │                      │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘   │
│         │                 │                                      │
│  ┌──────┴─────────────────┴──────────────────────────────────┐   │
│  │              Interview Manager (interview.js)             │   │
│  └──────────────────────────┬────────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────────┘
                              │ HTTP (fetch API)
┌─────────────────────────────┼────────────────────────────────────┐
│                     FLASK BACKEND                                │
│  ┌──────────────────────────┴────────────────────────────────┐   │
│  │                   app.py (Route Controller)               │   │
│  └───┬──────────┬──────────┬──────────┬──────────┬───────────┘   │
│      │          │          │          │          │                │
│  ┌───┴───┐  ┌──┴───┐  ┌──┴───┐  ┌──┴────┐  ┌──┴──────────┐    │
│  │  AI   │  │ Code │  │  DB  │  │Report │  │   config.py  │    │
│  │Proc.  │  │Sand- │  │Layer │  │ Gen.  │  │              │    │
│  │       │  │box   │  │      │  │       │  │              │    │
│  └───┬───┘  └──────┘  └──┬───┘  └───────┘  └──────────────┘    │
│      │                    │                                      │
└──────┼────────────────────┼──────────────────────────────────────┘
       │                    │
┌──────┴──────┐    ┌───────┴────────┐
│  Ollama API │    │ database.sqlite│
│ LLaMA 3.2  │    │   (SQLite)     │
└─────────────┘    └────────────────┘
```

### Data Flow Summary
1. **User uploads resume** → PyPDF2 extracts text → stored in Flask session
2. **User configures interview** → domain + experience level saved in session
3. **Interview starts** → AI generates 8 questions from resume+JD → stored in DB + session
4. **User answers** → answer sent to AI for scoring → scores saved to DB
5. **Coding test** → AI generates problem → user writes code → sandbox executes → AI evaluates
6. **Report** → AI generates final report from all collected data → displayed + PDF download

---

## 3. Technical Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, Tailwind CSS (CDN), JavaScript | UI rendering and styling |
| **Icons** | Font Awesome 6.4 | UI icons |
| **Templating** | Jinja2 | Server-side HTML templating |
| **Backend** | Flask (Python) | Web framework, routing, session management |
| **AI Engine** | Ollama + LLaMA 3.2:1b | Question generation, answer analysis, code evaluation |
| **NLP** | TextBlob, NLTK | Sentiment analysis, text tokenization |
| **Database** | SQLite3 | Persistent storage |
| **Sessions** | Flask-Session (filesystem) | Server-side session state |
| **File Parsing** | PyPDF2 | Resume PDF extraction |
| **PDF Reports** | pdfkit / xhtml2pdf | Report generation |
| **Speech** | Web Speech API | Browser-based speech recognition |
| **Camera** | MediaDevices API | Webcam preview during interview |

---

## 4. Complete User Workflow

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. Home │───>│ 2. Upload    │───>│ 3. Setup     │───>│ 4. Interview │
│  Page    │    │  Resume & JD │    │  Domain &    │    │  (8 Q&A)     │
│          │    │              │    │  Level       │    │              │
└──────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                               │
                                                               ▼
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 7. PDF   │<───│ 6. Final     │<───│ 5. Feedback  │<───│ Coding Test  │
│ Download │    │  Report      │    │  Summary     │    │ (optional)   │
└──────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### Step-by-Step Flow

| Step | Page | What Happens |
|------|------|-------------|
| 1 | **Home** (`index.html`) | Landing page with feature overview and "Start Practice Session" CTA |
| 2 | **Upload** (`upload.html`) | User uploads resume (PDF/TXT/DOCX) and provides JD (file or text). Text is extracted via PyPDF2 and stored in Flask session |
| 3 | **Setup** (`setup.html`) | User selects domain (10 options) and experience level (Intern/Entry/Mid/Senior). Optional: mic test, coding test toggle, cross-questions toggle |
| 4 | **Interview** (`interview.html`) | AI generates 8 questions. User answers via speech or typing. Each answer gets real-time AI scoring. Timer tracks time per question (2 min default) |
| 5 | **Coding** (`coding.html`) | AI generates a domain-specific coding problem. User writes Python in a textarea editor. Code executes in sandbox, then AI evaluates |
| 6 | **Feedback** (`feedback.html`) | Summary of all question scores with averages. Links to coding test or report |
| 7 | **Report** (`report.html`) | Final AI-generated report with overall score (0–100), strengths, weaknesses, improvement plan, and verdict. PDF download available |

---

## 5. Database Schema

The application uses **SQLite** with 6 tables:

### 5.1 Tables Overview

```
┌─────────────────────┐      ┌─────────────────────┐
│       users          │      │  performance_history │
│─────────────────────│      │─────────────────────│
│ id (PK)             │◄─────│ user_id (FK)        │
│ username (UNIQUE)   │      │ session_id (FK)     │
│ created_at          │      │ overall_score       │
└─────────┬───────────┘      │ communication_score │
          │                   │ technical_score     │
          │                   │ coding_score        │
          ▼                   │ confidence_score    │
┌─────────────────────┐      │ areas_to_improve    │
│ interview_sessions  │      └─────────────────────┘
│─────────────────────│
│ id (PK)             │
│ user_id (FK)        │
│ domain              │
│ experience_level    │
│ resume_text         │
│ job_description     │
│ start_time          │
│ end_time            │
│ total_score         │
│ feedback_summary    │
└──┬──────────┬───────┘
   │          │
   ▼          ▼
┌──────────┐ ┌──────────────┐
│questions │ │ coding_tests │
│──────────│ │──────────────│
│ id (PK)  │ │ id (PK)      │
│session_id│ │ session_id   │
│ q_text   │ │ problem_stmt │
│ q_type   │ │ language     │
│difficulty│ │ user_code    │
│ category │ │ test_passed  │
│time_alloc│ │ total_tests  │
└────┬─────┘ │ efficiency   │
     │       │ clarity      │
     ▼       │ logic_score  │
┌──────────┐ │ feedback     │
│ answers  │ │ time_taken   │
│──────────│ └──────────────┘
│ id (PK)  │
│ q_id(FK) │
│session_id│
│answer_txt│
│transcript│
│ duration │
│ grammar  │
│relevance │
│confidence│
│star_score│
│filler_cnt│
│ feedback │
│cross_q   │
│created_at│
└──────────┘
```

### 5.2 Table Details

#### `users`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment user ID |
| username | TEXT UNIQUE | Username |
| created_at | TIMESTAMP | Account creation time |

#### `interview_sessions`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Session ID |
| user_id | INTEGER FK | Links to users |
| domain | TEXT | e.g., "Software Engineering" |
| experience_level | TEXT | "Intern", "Entry", "Mid", "Senior" |
| resume_text | TEXT | Extracted resume content |
| job_description | TEXT | Job description text |
| start_time / end_time | TIMESTAMP | Session duration |
| total_score | REAL | Overall session score |
| feedback_summary | TEXT | Session feedback |

#### `questions`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Question ID |
| session_id | INTEGER FK | Links to session |
| question_text | TEXT | The question |
| question_type | TEXT | "technical", "behavioral", "situational", "advanced" |
| difficulty | TEXT | "easy", "medium", "hard" |
| category | TEXT | e.g., "Python", "System Design" |
| time_allocated | INTEGER | Seconds allowed |

#### `answers`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Answer ID |
| question_id | INTEGER FK | Links to question |
| session_id | INTEGER FK | Links to session |
| answer_text | TEXT | User's typed/spoken answer |
| transcript | TEXT | Speech transcript (legacy, now empty) |
| duration | INTEGER | Seconds spent answering |
| grammar_score | REAL | 0–10 |
| relevance_score | REAL | 0–10 |
| confidence_score | REAL | 0–10 (composite) |
| star_score | REAL | 0–10 |
| filler_words_count | INTEGER | Count of filler words |
| feedback | TEXT | AI feedback text |
| cross_question_asked | BOOLEAN | Whether follow-up was needed |

#### `coding_tests`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Test ID |
| session_id | INTEGER FK | Links to session |
| problem_statement | TEXT | The coding problem |
| language | TEXT | Default "python" |
| user_code | TEXT | Submitted code |
| test_cases_passed | INTEGER | 0–5 (estimated) |
| total_test_cases | INTEGER | Always 5 |
| efficiency_score | REAL | 0–10 |
| clarity_score | REAL | 0–10 |
| logic_score | REAL | 0–10 |
| feedback | TEXT | AI evaluation feedback |
| time_taken | INTEGER | Seconds spent |

#### `performance_history`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | History entry ID |
| user_id | INTEGER FK | Links to user |
| session_id | INTEGER FK | Links to session |
| date | DATE | Session date |
| overall_score | REAL | 0–100 |
| communication_score | REAL | 0–10 |
| technical_score | REAL | 0–10 |
| coding_score | REAL | 0–10 |
| confidence_score | REAL | 0–10 |
| areas_to_improve | TEXT | Improvement notes |

---

## 6. API Architecture & Request/Response Flow

All APIs use JSON request/response. Session state is maintained server-side via Flask-Session.

### 6.1 Page Routes

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/` | `index()` | Home page |
| GET | `/mic-test` | `mic_test()` | Microphone test page |
| GET/POST | `/upload` | `upload()` | Resume & JD upload |
| GET/POST | `/setup` | `setup_interview()` | Domain & level selection |
| GET | `/start-interview` | `start_interview()` | Generates questions, starts session |
| GET | `/coding-test` | `coding_test()` | Generates coding problem |
| GET | `/feedback` | `feedback()` | Score summary page |
| GET | `/generate-report` | `generate_report()` | Final AI report |
| GET | `/download-report` | `download_report()` | PDF download |

### 6.2 API Endpoints

#### `POST /api/next-question`
Returns the next interview question from the server's question queue.

**Request:** `{}` (empty body, session-based)

**Response:**
```json
{
    "status": "success",
    "question": {
        "id": 1,
        "question_text": "Tell me about your experience with Python...",
        "question_type": "technical",
        "difficulty": "medium",
        "category": "Python",
        "time_allocated": 120
    },
    "current_index": 0,
    "total_questions": 8
}
```

**Note:** Each call increments `session['current_question_index']` on the server. The frontend syncs its local index from `current_index` in the response.

---

#### `POST /api/analyze-answer`
Analyzes a submitted interview answer using AI.

**Request:**
```json
{
    "question_id": 1,
    "answer_text": "In my previous role at XYZ, I worked extensively with Python...",
    "transcript": "",
    "duration": 45
}
```

**Response:**
```json
{
    "status": "success",
    "analysis": {
        "grammar_score": 7,
        "relevance_score": 8,
        "confidence_score": 6.5,
        "star_score": 5,
        "filler_words_count": 3,
        "feedback": "Good technical knowledge demonstrated...",
        "suggested_answer": "A stronger answer would include...",
        "needs_cross_question": true,
        "cross_question": "Can you give a specific example?"
    },
    "next_question_available": true
}
```

---

#### `POST /api/evaluate-code`
Evaluates submitted Python code — runs in sandbox, then AI evaluates.

**Request:**
```json
{
    "code": "def solve_problem():\n    return sorted(numbers)",
    "time_taken": 180
}
```

**Response:**
```json
{
    "status": "success",
    "evaluation": {
        "logic_score": 8,
        "efficiency_score": 7,
        "clarity_score": 6,
        "test_cases_passed": 4,
        "total_test_cases": 5,
        "detailed_feedback": "Good approach using built-in sort...",
        "suggested_improvements": "Consider edge cases...",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)"
    },
    "execution": {
        "output": "Solution ready!",
        "error": "",
        "success": true
    }
}
```

---

#### `POST /api/speech-status`
Updates server about speech recognition state.

**Request:** `{ "active": true }`
**Response:** `{ "status": "success" }`

---

## 7. Interview Flow — Detailed

```
User clicks           Browser sends          Flask calls AI
"Start Interview" ──> GET /start-interview ──> generate_questions()
                                               │
                      Questions stored in   <──┘
                      session + database
                                               
Browser auto-calls    Flask returns           
POST /api/next-q ──> question from session ──> Display Question 1 of 8
                                               
User speaks/types     Browser sends            Flask calls AI
answer, clicks     ──> POST /api/analyze  ──> analyze_answer()
"Submit Answer"        -answer                  │
                                               │
                      Scores + feedback     <──┘
                      saved to DB + shown
                                               
User clicks           Browser sends           
"Next Question"   ──> POST /api/next-q    ──> Display Question 2 of 8
                                               
        ... Repeat for all 8 questions ...
                                               
All done           ──> Redirect to /coding-test or /feedback
```

### Interview Page Features
- **Camera preview** — Webcam feed displayed for interview simulation
- **Timer** — 2-minute countdown per question (configurable)
- **Speech recognition** — Real-time speech-to-text into answer textarea
- **Question counter** — Shows "Question X of Y"
- **Question tags** — Type (Technical/Behavioral) and difficulty badges
- **Answer input** — Single textarea for both typed and spoken input
- **Feedback area** — Expandable section showing AI scores after submission
- **Cross-questions** — Follow-up questions when answers are too short/vague

---

## 8. Coding Test Flow — Detailed

```
User navigates to     Flask calls AI          
/coding-test      ──> generate_problem()   ──> Display problem + editor
                                               
User writes code      Browser displays         
in textarea           code in real-time
                                               
User clicks           Browser sends            Flask checks
"Run Code"        ──> POST /api/evaluate  ──> 1. Is code boilerplate?
                       -code                   │  YES → Return 0 scores
                                               │  NO  ↓
                                               2. Is code safe?
                                               │  NO → Return error
                                               │  YES ↓
                                               3. Execute in sandbox
                                               │  ↓
                                               4. AI evaluates code
                                               │  + execution result
                                               │  ↓
                                               5. If execution failed,
                                               │  cap scores at 2/10
                                               │  ↓
                      Display scores +      <──┘
                      output/errors
```

### Boilerplate Detection
If the user submits the default template code without modifications, the system returns **0 scores** immediately:
- Strips comments and whitespace from submitted code
- Checks if remaining lines are only `pass`, `def solve_problem():`, `if __name__...`, `print("Solution ready!")`
- If yes → returns zero scores without calling AI

### Code Safety Check
Before execution, `CodeSandbox.is_code_safe()` blocks these dangerous patterns:

| Blocked Pattern | Reason |
|----------------|--------|
| `import os` | File system access |
| `import sys` | System access |
| `__import__` | Dynamic imports |
| `eval(` / `exec(` | Arbitrary code execution |
| `open(` | File I/O |
| `subprocess` | Process spawning |
| `system(` | OS command execution |
| `shutil` | File operations |
| `socket` | Network access |
| `requests` / `urllib` | HTTP requests |
| `pickle` / `yaml` | Deserialization attacks |
| `compile` / `globals` / `locals` | Introspection |

### Execution Environment
- Code written to a temp `.py` file
- Executed via `subprocess.run()` with a **5-second timeout**
- `PYTHONPATH` is cleared to restrict imports
- Errors (timeout, crash) are captured and returned

### Score Capping
If code **fails to execute**, all AI scores are **capped at 2/10** and test cases passed is set to 0.

---

## 9. Scoring Logic — Complete Reference

### 9.1 Interview Answer Scores (per question)

Each answer receives **4 scores** on a 0–10 scale:

| Score | Source | Description |
|-------|--------|-------------|
| **Grammar** | Ollama AI | Language quality, sentence structure, grammar correctness |
| **Relevance** | Ollama AI | How well the answer addresses the specific question asked |
| **STAR Method** | Ollama AI | Usage of Situation-Task-Action-Result structure |
| **Confidence** | Composite formula | Calculated from 5 weighted factors (see §9.2) |

### 9.2 Confidence Score Calculation

The confidence score is **NOT** directly from the AI. It is a **composite metric** calculated from 5 factors in `ai_processor.py`:

```
confidence_score = (
    relevance_score     × 0.30    → 30% weight
  + star_score          × 0.20    → 20% weight
  + sentiment_component × 0.20    → 20% weight
  + filler_penalty      × 0.15    → 15% weight
  + length_score        × 0.15    → 15% weight
)
```

#### Factor Breakdown

| # | Factor | Weight | How It's Calculated | Range |
|---|--------|--------|-------------------|-------|
| 1 | **Relevance** | 30% | Direct from AI's `relevance_score` | 0–10 |
| 2 | **STAR Method** | 20% | Direct from AI's `star_score` | 0–10 |
| 3 | **Sentiment** | 20% | `(1 + TextBlob.polarity) × 5` — converts polarity [-1, +1] to [0, 10]. Positive/assertive tone scores higher | 0–10 |
| 4 | **Filler Words** | 15% | `max(0, 10 - filler_count × 1.0)` — each filler word costs exactly 1 point. 10+ fillers = 0 | 0–10 |
| 5 | **Answer Length** | 15% | `min(10, word_count / 5)` — 50+ words = full 10 marks. Shorter answers get proportionally less | 0–10 |

#### Detected Filler Words
`um`, `uh`, `ah`, `er`, `like`, `you know`, `so`, `well`

#### Worked Example
An answer with: relevance=8, STAR=6, neutral sentiment (polarity=0), 2 filler words, 60 words:

```
Sentiment component = (1 + 0.0) × 5 = 5.0
Filler penalty      = max(0, 10 - 2×1.0) = 8.0
Length score         = min(10, 60/5) = 10.0

Confidence = (8 × 0.30) + (6 × 0.20) + (5.0 × 0.20) + (8.0 × 0.15) + (10.0 × 0.15)
           = 2.4 + 1.2 + 1.0 + 1.2 + 1.5
           = 7.3
```

**Important:** The analysis always uses the **answer text** (which contains both typed and spoken content). Sentiment analysis and filler detection operate on the actual answer, not a separate transcript.

### 9.3 Coding Test Scores

| Score | Source | Range | Description |
|-------|--------|-------|-------------|
| **Logic** | Ollama AI | 0–10 | Correctness of the algorithm and approach |
| **Efficiency** | Ollama AI | 0–10 | Optimal time/space complexity |
| **Clarity** | Ollama AI | 0–10 | Code readability, naming, structure |
| **Test Cases** | Ollama AI (estimated) | 0–5 | How many test cases would pass |
| **Time Complexity** | Ollama AI | Big O | e.g., O(n), O(n²) |
| **Space Complexity** | Ollama AI | Big O | e.g., O(1), O(n) |

### 9.4 Final Report Scores

Generated by AI from all collected session data:

| Score | Range | Description |
|-------|-------|-------------|
| **Overall** | 0–100 | Holistic performance rating |
| **Communication** | 0–10 | Overall communication quality |
| **Technical** | 0–10 | Technical knowledge demonstrated |
| **Confidence** | 0–10 | Overall interview confidence impression |
| **Final Verdict** | Category | "Strong Candidate", "Needs Improvement", or "Not Ready" |

Plus: lists of strengths, weaknesses, improvement plan items, and a detailed analysis paragraph.

### 9.5 Fallback Scores (When AI Unavailable)

| Context | Fallback Scores | Rationale |
|---------|----------------|-----------|
| Interview answer | Grammar: 3, Relevance: 3, STAR: 2, Confidence: 3 | Low to avoid inflating unanalyzed answers |
| Coding test | Logic: 0, Efficiency: 0, Clarity: 0, Tests: 0/5 | Cannot evaluate without AI |
| Final report | Overall: 70, Communication: 7, Technical: 6, Confidence: 6 | Moderate default |

---

## 10. Module-by-Module Explanation

### 10.1 `app.py` — Route Controller (436 lines)
The main Flask application. Handles all HTTP routes, manages session state, coordinates between all other modules.

**Key Responsibilities:**
- File upload handling and PDF text extraction via PyPDF2
- Session initialization (questions, answers, indices stored server-side)
- API endpoints for question delivery, answer analysis, code evaluation
- Boilerplate code detection (returns 0 before calling AI)
- Report generation coordination
- Database writes for all session data

### 10.2 `ai_processor.py` — AI Logic Engine (425 lines)
Interfaces with the Ollama API for all AI operations.

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `_generate_content()` | Low-level Ollama API call (POST to `/api/generate`) |
| `extract_text_from_resume()` | Parses resume into structured JSON (name, skills, experience, projects, certifications) |
| `generate_questions()` | Creates domain-specific interview questions (technical, behavioral, situational) |
| `analyze_answer()` | Scores answers for grammar/relevance/STAR, calculates confidence |
| `evaluate_code()` | Evaluates code solutions with execution context, caps scores for failures |
| `generate_problem_statement()` | Creates coding challenges with examples and constraints |
| `generate_cross_question()` | Generates follow-up questions for vague answers |
| `generate_final_report()` | Produces comprehensive performance report with verdict |

### 10.3 `database.py` — Data Layer (284 lines)
SQLite interface with 6 tables.

**Functions:**
| Function | Purpose |
|----------|---------|
| `init_db()` | Creates all 6 tables if they don't exist |
| `save_interview_session()` | Records new interview session |
| `save_question()` | Saves a generated question |
| `save_answer()` | Records answer with all 4 scores + feedback |
| `save_coding_test()` | Records coding test results |
| `get_session_performance()` | Retrieves all data for a session (answers + coding + session info) |
| `get_user_history()` | Gets user's performance history across sessions |

### 10.4 `code_sandbox.py` — Secure Execution (131 lines)
Sandboxed Python code execution.

**Classes & Methods:**
| Method | Purpose |
|--------|---------|
| `is_code_safe()` | Pattern-matching safety check against 16 dangerous patterns |
| `execute_python_code()` | Writes to temp file, runs via `subprocess.run()` with 5s timeout |
| `run_test_cases()` | Wraps user code with test assertions and runs each individually |

### 10.5 `report_generator.py` — PDF Reports (587 lines)
Generates styled HTML reports and converts to PDF.

| Method | Purpose |
|--------|---------|
| `generate_html_report()` | Full HTML template with inline CSS, scores, charts, recommendations |
| `generate_pdf()` | Converts HTML to PDF using `pdfkit` (requires wkhtmltopdf installed) |
| `generate_pdf_simple()` | Fallback PDF generation using `xhtml2pdf` |

### 10.6 `config.py` — Configuration (25 lines)
Central configuration class.

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | `dev-key-123-...` | Flask session encryption key |
| `UPLOAD_FOLDER` | `uploads` | Resume upload directory |
| `MAX_CONTENT_LENGTH` | 16 MB | Maximum upload file size |
| `SESSION_TYPE` | `filesystem` | Server-side session storage |
| `ALLOWED_EXTENSIONS` | `pdf, txt, docx` | Accepted resume file types |
| `QUESTION_TIME_LIMIT` | 120 seconds | Per-question time limit |
| `CODING_TIME_LIMIT` | 600 seconds | Coding test time limit |
| `DATABASE` | `database.sqlite` | SQLite database file path |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2:1b` | AI model to use |

### 10.7 Frontend JavaScript

| File | Class | Lines | Purpose |
|------|-------|-------|---------|
| `interview.js` | `InterviewManager` | 339 | Question loading, answer submission, feedback display, timer, "next question" navigation |
| `speech.js` | `SpeechRecognitionManager` | ~280 | Web Speech API integration, real-time transcription directly into the answer textarea |
| `camera.js` | `CameraManager` | ~290 | Webcam/mic toggle, MediaDevices API, video preview element |

---

## 11. Security Considerations

| Area | Implementation |
|------|---------------|
| **Code Execution** | Sandboxed via subprocess with 5-second timeout. 16 dangerous patterns blocked before execution |
| **File Uploads** | Limited to PDF/TXT/DOCX, max 16MB. Filenames sanitized via `werkzeug.secure_filename` |
| **Session Security** | Server-side filesystem sessions (not client-side cookies). Secret key configurable via environment variable |
| **Input Sanitization** | Jinja2 auto-escapes all HTML in templates by default |
| **PYTHONPATH** | Cleared during sandbox execution to restrict import paths |

### Security Limitations
- Code sandbox is basic pattern-matching, not a true container/jail — sophisticated attacks could bypass it
- No user authentication system (runs in demo mode with `user_id=1`)
- Ollama API runs locally without authentication
- No CSRF protection on forms
- No rate limiting on API endpoints
- Secret key hardcoded as fallback (should always use environment variable in production)

---

## 12. Error Handling Strategy

| Scenario | How It's Handled |
|----------|-----------------|
| **Ollama API down/unreachable** | Every AI function has a `try/except` block with fallback return values (default questions, low scores, generic feedback) |
| **AI returns invalid JSON** | Multiple parsing strategies tried in sequence: regex extraction `{...}` → direct `json.loads()` → substring extraction |
| **Resume parse fails** | Returns empty dict; questions fall back to 3 generic defaults |
| **Code execution timeout** | `subprocess.TimeoutExpired` caught; returns "possible infinite loop" error |
| **Code execution crash** | General `Exception` caught; error message returned to UI |
| **Speech API not supported** | Browser capability check disables speech button; shows warning banner |
| **Microphone permission denied** | Explicit error messages per error type (no-speech, audio-capture, not-allowed) |
| **File type not allowed** | Validated against `ALLOWED_EXTENSIONS` set; rejected with flash message |
| **Empty answer submitted** | Alert prevents submission: "Please provide an answer" |

---

## 13. Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|-----------------|
| Empty answer submitted | Alert blocks submission: "Please provide an answer before submitting" |
| Default boilerplate code submitted | Returns 0 scores immediately without calling AI |
| Code with syntax errors | Sandbox captures stderr, AI receives failure context, scores capped at 2/10 |
| Very short answer (<30 words) | Triggers cross-question flag; confidence penalized via length score |
| Filler words in answer | Counted and penalized in confidence calculation (1 point per filler word) |
| Speech recognition active during submit | Speech auto-stops before submitting; 300ms flush delay for final words |
| All questions completed | Shows completion message; redirects to coding test or feedback |
| No questions generated (AI failure) | 3 default fallback questions provided |
| Browser doesn't support Speech API | Speech button disabled, warning banner shown; typing still fully functional |
| Code execution infinite loop | 5-second timeout kills the process; returns timeout error |
| Very long code submission | No explicit limit, but Ollama has context limits |

---

## 14. Known Limitations

1. **Single user mode** — No authentication system; all sessions default to `user_id=1`
2. **Python only** — Coding test only supports Python; no JavaScript, Java, C++, etc.
3. **No real test cases** — Test case pass count is AI-estimated, not actually executed against test suites
4. **Basic code sandbox** — Pattern matching only, not a true isolated container environment
5. **Ollama dependency** — Requires local Ollama installation with the specific `llama3.2:1b` model pre-downloaded
6. **No session persistence across restarts** — Flask filesystem sessions may be lost on server restart
7. **PDF download** — The `download_report` route returns the generated PDF but requires `pdfkit`/`wkhtmltopdf` to be installed
8. **Record session checkbox** — UI checkbox exists on setup page but actual video recording is not implemented
9. **STAR score always shown** — Even for technical questions where STAR method isn't relevant
10. **Single language** — All UI text is in English only

---

## 15. Future Improvements

1. **User authentication** — Login/signup system with hashed passwords and per-user session history
2. **Multi-language coding** — Support JavaScript, Java, C++, Go in the sandbox
3. **Real test case execution** — Run user code against actual predefined test suites with proper pass/fail tracking
4. **Docker sandbox** — Containerized code execution for true OS-level isolation
5. **WebSocket communication** — Replace HTTP polling with WebSocket for real-time streaming feedback
6. **Video recording** — Record interview sessions (webcam + audio) for later playback and review
7. **Analytics dashboard** — Track performance trends across multiple sessions with charts
8. **Custom question pools** — Allow users/admins to upload and manage custom question banks
9. **Collaborative mock interviews** — Pair two users for realistic mock interview practice
10. **Mobile responsiveness** — Full responsive design for tablets and smartphones
11. **Interview timer customization** — Allow users to set their own time limits
12. **Export history** — Export all session data as CSV/Excel for analysis

---

## 16. Setup & Installation Guide

### Prerequisites
- **Python 3.9+** installed
- **Ollama** installed and running locally ([ollama.ai](https://ollama.ai/))
- (Optional) **wkhtmltopdf** for PDF report generation

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd AI-Interview-Platform

# 2. Create a Python virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Download required NLTK data (auto-downloads on first run too)
python -c "import nltk; nltk.download('punkt')"

# 6. Pull the AI model via Ollama
ollama pull llama3.2:1b

# 7. Start Ollama server (if not already running)
ollama serve

# 8. Run the application
flask run
# OR
python app.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-key-123-change-in-production` | Flask session secret key (CHANGE IN PRODUCTION) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint URL |

### Verify Installation
1. Open `http://127.0.0.1:5000` in **Chrome or Edge** (required for speech recognition — Firefox/Safari have limited support)
2. Click "Start Practice Session"
3. Upload any PDF resume and enter a job description
4. Select a domain and experience level, then click "Start Interview"
5. AI-generated questions should appear — you're ready to practice!

### Dependencies (from requirements.txt)
| Package | Purpose |
|---------|---------|
| Flask | Web framework |
| Flask-Session | Server-side session support |
| requests | HTTP client for Ollama API |
| textblob | Sentiment analysis |
| nltk | Natural language processing |
| PyPDF2 | PDF text extraction |
| python-dotenv | Environment variable loading |
| pdfkit | HTML to PDF conversion |

---

## 17. File Structure Reference

```
AI-Interview-Platform/
│
├── app.py                    # Flask routes & main controller (436 lines)
├── ai_processor.py           # AI logic, scoring & Ollama integration (425 lines)
├── code_sandbox.py           # Secure Python code execution (131 lines)
├── config.py                 # Central configuration (25 lines)
├── database.py               # SQLite data access layer (284 lines)
├── report_generator.py       # HTML/PDF report generation (587 lines)
├── requirements.txt          # Python package dependencies
├── database.sqlite           # SQLite database file (auto-created)
├── PROJECT_DOCUMENTATION.md  # This document
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Base layout (nav, footer, shared scripts)
│   ├── index.html            # Home/landing page
│   ├── upload.html           # Resume & JD upload page
│   ├── setup.html            # Interview configuration page
│   ├── mic_test.html         # Microphone & speech test page
│   ├── interview.html        # Live interview session page
│   ├── coding.html           # Coding test editor page
│   ├── feedback.html         # Score summary & feedback page
│   └── report.html           # Final performance report page
│
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css         # Custom CSS styles
│   └── js/
│       ├── interview.js      # Interview flow management (339 lines)
│       ├── speech.js          # Speech recognition integration (~280 lines)
│       └── camera.js         # Webcam & microphone management (~290 lines)
│
├── uploads/                  # User-uploaded files
│   ├── resumes/              # Uploaded resume PDFs
│   └── job_descriptions/     # Uploaded JD files
│
└── flask_session/            # Server-side session storage (auto-created)
```

---

*Document generated on February 2026. Based on the current implementation of the AI Interview Coach platform.*
