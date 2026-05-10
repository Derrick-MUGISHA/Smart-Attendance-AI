# Smart Attendance AI

AI-powered attendance automation built entirely in Python.
Extracts student names from attendance screenshots via OCR,
corrects them using fuzzy matching, routes uncertain entries
through Telegram for human approval, and syncs final reports
to Google Drive.

## 🚀 Key Features

*   **Telegram Bot Integration**: Send images, PDFs, and documents directly to the system.
*   **Automatic Organization**: Files are renamed and sorted into folders by date.
*   **AI-Powered Processing**: Background tasks handle OCR and student matching.
*   **FastAPI Backend**: Robust API for dashboard and integration.
*   **Audit Trail**: Full history stored in PostgreSQL.

## 🛠 Project Architecture

```
app/
├── api/          # FastAPI Routes (APIRouter)
├── bot/          # Telegram Bot Handlers
├── services/     # Core Business Logic (FileManager, OCR, Matching)
├── tasks/        # Celery Background Tasks
├── models/       # SQLAlchemy (ORM) Models
├── templates/    # HTML Templates for PDF reports
├── config.py     # Pydantic Settings
├── database.py   # DB Engine & Session
└── main.py       # App Entry Point
```

## 📦 Installation Guide

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/smart-attendance-ai
    cd smart-attendance-ai
    ```

2.  **Environment Setup**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    pip install -r requirements.txt
    ```

3.  **Database Setup**:
    Ensure PostgreSQL and Redis are running (or use Docker Compose).
    ```bash
    alembic upgrade head
    ```

4.  **Telegram Bot Setup**:
    - Create a bot via @BotFather.
    - Copy the API Token to `.env`.

5.  **Run with Docker**:
    ```bash
    docker compose up
    ```

## 🤖 Telegram Commands

*   `/start` - Initialize bot and see instructions.
*   `/help` - Get detailed usage guide.
*   `/status` - Check backend and worker health.
*   `/today` - View summarized attendance for today.
*   `/process` - Manually trigger AI pipeline.
*   `/rename <old> <new>` - Rename uploaded files.
*   `/delete <filename>` - Remove an entry.

## 🔗 API Documentation

Once running, access Swagger docs at:
`http://localhost:8000/docs`

Key Endpoints:
- `GET /health`
- `POST /attendance/upload`
- `GET /attendance/today`
- `GET /attendance/history`
- `POST /attendance/process`

## 🛡 Security & Scaling

- **Admin Whitelist**: Restrict bot usage via `TELEGRAM_ADMIN_IDS` in `.env`.
- **Async Tasks**: Heavy OCR/AI processing is offloaded to Celery workers.
- **Validation**: Strict file type and size limits enforced.

## 📋 OCR & AI Pipeline Plan

1.  **Preprocess**: Enhance image contrast/sharpness.
2.  **Extract**: Use Google Cloud Vision (Primary) or Tesseract (Fallback).
3.  **Match**: Fuzzy string matching (RapidFuzz) against student roster.
4.  **Validate**: Human-in-the-loop verification via Telegram keyboards.
