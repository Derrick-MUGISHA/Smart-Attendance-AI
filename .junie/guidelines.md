# Smart Attendance AI Project Overview

AI-powered attendance automation built entirely in Python. It extracts student names from attendance screenshots via OCR, corrects them using fuzzy matching, routes uncertain entries through Telegram for human approval, and syncs final reports to Google Drive.

## Core Tech Stack
- **API Framework:** FastAPI
- **Telegram Bot:** python-telegram-bot v20+
- **OCR:** Google Cloud Vision (Primary), Pytesseract (Fallback)
- **Image Preprocessing:** Pillow + OpenCV
- **Fuzzy Matching:** RapidFuzz
- **Task Queue:** Celery + Redis
- **ORM:** SQLAlchemy 2 + Alembic
- **Database:** PostgreSQL
- **Storage:** Google Drive API v3
- **PDF Generation:** WeasyPrint / ReportLab

## Key Features
- **Mobile-First:** Teachers upload screenshots via Telegram.
- **Automated Processing:** Asynchronous OCR and validation using Celery.
- **Human-in-the-Loop:** Unsure matches are sent back to Telegram for manual confirmation.
- **Cloud Sync:** Raw images and PDF reports are automatically organized in Google Drive.
- **Audit Trail:** Full attendance history stored in PostgreSQL.

## Workflow
1. **Upload:** Screenshot sent to Telegram Bot.
2. **Preprocess:** Image sharpened and denoised (Pillow/OpenCV).
3. **OCR:** Google Cloud Vision extracts text.
4. **Match:** RapidFuzz compares extracted names against the student roster.
5. **Review:** Auto-approve high-confidence matches; request review for low-confidence ones.
6. **Report:** Generate PDF and sync to Google Drive.

---

# Project Guidelines
    
# Smart Attendance AI — Python + Google Drive Edition

> Full-Python cloud attendance automation: FastAPI · python-telegram-bot · RapidFuzz ·
> Google Cloud Vision · Google Drive API · PostgreSQL · Celery · Redis

---

## Why Full Python Is The Right Call

Switching to Python collapses what was a two-service architecture (NestJS + Python microservice)
into a single unified codebase. Every core dependency lives natively in Python:

- `google-cloud-vision` — OCR
- `rapidfuzz` — fuzzy name matching
- `google-api-python-client` — Google Drive sync
- `python-telegram-bot` — Telegram bot
- `Pillow` / `opencv-python` — image preprocessing
- `celery` — async job queues (replaces BullMQ)
- `weasyprint` / `reportlab` — PDF generation
- `SQLAlchemy` + `alembic` — database ORM and migrations

No language boundary. No HTTP calls between services. One repo, one runtime.

---

## Architecture (Python-native)

```
Mobile Screenshot
      ↓
Telegram Bot (python-telegram-bot)
      ↓
Image Preprocessing (Pillow + OpenCV)
      ↓
Google Drive Upload (raw + processed)
      ↓
OCR Queue (Celery → Google Cloud Vision AI)
      ↓
AI Name Matching (RapidFuzz + confidence scoring)
      ↓
Attendance Validation (vs PostgreSQL via SQLAlchemy)
      ↓
Human Confirmation (Telegram inline keyboard)
      ↓
PDF Report (WeasyPrint)
      ↓
Google Drive Sync (final reports folder)
      ↓
PostgreSQL (full audit trail)
```

**Redis** backs Celery as the message broker and caches student/class lists.

---

## Monorepo Structure

```
smart-attendance-ai/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # env vars, settings
│   ├── database.py              # SQLAlchemy engine + session
│   │
│   ├── api/                     # REST API routes (dashboard)
│   │   ├── routes/
│   │   │   ├── sessions.py
│   │   │   ├── students.py
│   │   │   ├── reports.py
│   │   │   └── health.py
│   │
│   ├── bot/                     # Telegram bot handlers
│   │   ├── bot.py               # Application setup
│   │   ├── handlers/
│   │   │   ├── start.py
│   │   │   ├── upload.py
│   │   │   ├── confirm.py
│   │   │   ├── report.py
│   │   │   └── history.py
│   │   └── keyboards.py         # Inline keyboard builders
│   │
│   ├── services/
│   │   ├── ocr.py               # Google Cloud Vision wrapper
│   │   ├── preprocessing.py     # Pillow + OpenCV pipeline
│   │   ├── matching.py          # RapidFuzz name matcher
│   │   ├── validation.py        # Attendance validator
│   │   ├── drive.py             # Google Drive API wrapper
│   │   ├── pdf.py               # Report generator
│   │   └── cache.py             # Redis helpers
│   │
│   ├── tasks/                   # Celery task definitions
│   │   ├── celery_app.py
│   │   ├── ocr_tasks.py
│   │   ├── validation_tasks.py
│   │   └── export_tasks.py
│   │
│   └── models/                  # SQLAlchemy ORM models
│       ├── student.py
│       ├── class_.py
│       ├── session.py
│       ├── attendance_record.py
│       └── ocr_job.py
│
├── migrations/                  # Alembic migrations
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech Stack (Full Python)

| Layer | Technology | Why |
|---|---|---|
| API framework | FastAPI | Async, fast, auto OpenAPI docs |
| Telegram bot | python-telegram-bot v20+ | Native async, inline keyboards |
| OCR | google-cloud-vision | Best accuracy on screenshots |
| OCR fallback | pytesseract | Free local fallback |
| Image preprocessing | Pillow + opencv-python | Sharpen, denoise, crop, contrast |
| Fuzzy matching | rapidfuzz | Best-in-class, pure Python |
| Task queue | Celery + Redis | Async job processing |
| Cache | Redis (redis-py) | Class lists, student name cache |
| ORM | SQLAlchemy 2 + Alembic | Migrations, type-safe queries |
| Database | PostgreSQL (Supabase) | Hosted, managed |
| Storage + sync | Google Drive API v3 | Screenshots, reports, exports |
| PDF generation | WeasyPrint or ReportLab | HTML→PDF or programmatic PDF |
| Dashboard | FastAPI + Jinja2 (or separate Next.js) | Lightweight or full SPA |
| Deployment | Railway (API + bot + workers) | Python-native deploy |

---

## Google Drive Folder Structure

```
📁 Smart Attendance AI/
├── 📁 Raw Screenshots/
│   └── 📁 2026-05/
│       └── class-a1-2026-05-09-raw.jpg
├── 📁 Processed Images/
│   └── 📁 2026-05/
│       └── class-a1-2026-05-09-processed.jpg
├── 📁 Reports/
│   └── 📁 SheCanCODE A1/
│       └── attendance-2026-05-09.pdf
└── 📁 Exports/
    └── attendance-monthly-may-2026.xlsx
```

All folders are created programmatically on first run.
Teachers get view access; system service account has editor access.

---

## Phase 1 — Project Foundation (Week 1)

### 1.1 — Environment Setup

- [ ] Create virtual environment: `python -m venv .venv`
- [ ] Install core dependencies (see `requirements.txt` below)
- [ ] Set up Docker Compose for local PostgreSQL + Redis
- [ ] Configure `.env` with all service credentials
- [ ] Initialize Alembic for migrations
- [ ] Write `config.py` using Pydantic `BaseSettings`

**`requirements.txt`**
```
fastapi
uvicorn[standard]
python-telegram-bot[webhooks]>=20.0
google-cloud-vision
google-api-python-client
google-auth
google-auth-oauthlib
rapidfuzz
Pillow
opencv-python-headless
celery[redis]
redis
SQLAlchemy>=2.0
alembic
psycopg2-binary
weasyprint
reportlab
python-dotenv
pydantic-settings
httpx
pytest
pytest-asyncio
```

### 1.2 — Database Schema

```sql
-- students
CREATE TABLE students (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  student_code VARCHAR(50) UNIQUE NOT NULL,
  class_id UUID REFERENCES classes(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- classes
CREATE TABLE classes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  instructor_name VARCHAR(255),
  schedule JSONB,
  drive_folder_id VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- attendance_sessions
CREATE TABLE attendance_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  class_id UUID REFERENCES classes(id),
  date DATE NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ocr_jobs
CREATE TABLE ocr_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES attendance_sessions(id),
  raw_image_drive_id VARCHAR(255),
  processed_image_drive_id VARCHAR(255),
  raw_ocr_text TEXT,
  status VARCHAR(50) DEFAULT 'queued',
  engine VARCHAR(50),
  duration_ms INTEGER,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- attendance_records
CREATE TABLE attendance_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES attendance_sessions(id),
  student_id UUID REFERENCES students(id),
  ocr_raw_name VARCHAR(255) NOT NULL,
  matched_name VARCHAR(255),
  confidence_score FLOAT,
  status VARCHAR(50) DEFAULT 'pending',
  reviewed_by VARCHAR(255),
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

- [ ] Write Alembic migration for all tables
- [ ] Seed with test students and classes
- [ ] Add indexes on `class_id`, `session_id`, `student_id`

---

## Phase 2 — Google Drive Integration (Week 2)

### 2.1 — Service Account Setup

- [ ] Create Google Cloud project
- [ ] Enable Google Drive API + Google Cloud Vision API
- [ ] Create service account, download JSON key
- [ ] Share root Drive folder with service account email
- [ ] Store credentials path in `.env`

### 2.2 — Drive Service (`app/services/drive.py`)

```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
import io

SCOPES = ['https://www.googleapis.com/auth/drive']

class DriveService:
    def __init__(self, credentials_path: str):
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=creds)

    def get_or_create_folder(self, name: str, parent_id: str = None) -> str:
        """Return folder ID, creating it if it doesn't exist."""
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        results = self.service.files().list(q=query, fields='files(id)').execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else []
        }
        folder = self.service.files().create(body=metadata, fields='id').execute()
        return folder['id']

    def upload_file(self, local_path: str, filename: str, folder_id: str,
                    mime_type: str = 'image/jpeg') -> str:
        """Upload file to Drive folder, return file ID."""
        metadata = {'name': filename, 'parents': [folder_id]}
        media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
        file = self.service.files().create(
            body=metadata, media_body=media, fields='id'
        ).execute()
        return file['id']

    def upload_bytes(self, content: bytes, filename: str, folder_id: str,
                     mime_type: str = 'application/pdf') -> str:
        """Upload in-memory bytes to Drive, return file ID."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as f:
            f.write(content)
            tmp_path = f.name
        try:
            file_id = self.upload_file(tmp_path, filename, folder_id, mime_type)
        finally:
            os.unlink(tmp_path)
        return file_id

    def get_shareable_link(self, file_id: str) -> str:
        """Make file readable by anyone with the link and return the URL."""
        self.service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()
        return f"https://drive.google.com/file/d/{file_id}/view"
```

- [ ] Implement `get_or_create_folder`
- [ ] Implement `upload_file` and `upload_bytes`
- [ ] Implement `get_shareable_link`
- [ ] Write unit tests with mocked Drive API

---

## Phase 3 — Image Preprocessing + OCR (Week 2–3)

### 3.1 — Preprocessing Pipeline (`app/services/preprocessing.py`)

```python
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np
import io

def preprocess_image(image_bytes: bytes) -> bytes:
    """Sharpen, denoise, crop borders, boost contrast — return processed bytes."""
    # Load with OpenCV for denoising
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    denoised = cv2.fastNlMeansDenoisingColored(img_cv, None, 10, 10, 7, 21)
    img_pil = Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))

    # Sharpen
    img_pil = img_pil.filter(ImageFilter.SHARPEN)

    # Boost contrast
    enhancer = ImageEnhance.Contrast(img_pil)
    img_pil = enhancer.enhance(1.5)

    # Convert to grayscale for better OCR
    img_pil = img_pil.convert('L')

    # Auto-crop white borders
    img_pil = img_pil.crop(img_pil.getbbox())

    out = io.BytesIO()
    img_pil.save(out, format='JPEG', quality=95)
    return out.getvalue()
```

- [ ] Implement and test on real attendance screenshots
- [ ] Log preprocessing time per image
- [ ] Handle corrupted or very small images gracefully

### 3.2 — OCR Service (`app/services/ocr.py`)

```python
from google.cloud import vision
import pytesseract
from PIL import Image
import io

class OCRService:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def extract_text_vision(self, image_bytes: bytes) -> str:
        """Primary OCR using Google Cloud Vision."""
        image = vision.Image(content=image_bytes)
        response = self.client.text_detection(image=image)
        if response.error.message:
            raise RuntimeError(f"Vision API error: {response.error.message}")
        texts = response.text_annotations
        return texts[0].description if texts else ""

    def extract_text_tesseract(self, image_bytes: bytes) -> str:
        """Fallback OCR using Tesseract."""
        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(img, lang='eng')

    def extract(self, image_bytes: bytes) -> tuple[str, str]:
        """Try Vision first, fall back to Tesseract. Return (text, engine)."""
        try:
            return self.extract_text_vision(image_bytes), 'google_vision'
        except Exception:
            return self.extract_text_tesseract(image_bytes), 'tesseract'

    def normalize_names(self, raw_text: str) -> list[str]:
        """Parse OCR output into a clean list of candidate names."""
        lines = [line.strip() for line in raw_text.splitlines()]
        names = []
        for line in lines:
            # Skip blank lines, numbers-only lines, header patterns
            if not line or line.isdigit():
                continue
            if any(kw in line.lower() for kw in ['date', 'class', 'attendance', 'name', 'no.']):
                continue
            names.append(line)
        return names
```

- [ ] Test with at least 10 diverse screenshot samples
- [ ] Log engine used and duration per job in `ocr_jobs`
- [ ] Handle multilingual names (common in Rwanda: Kinyarwanda, French, English)

---

## Phase 4 — AI Name Matching (Week 3)

### 4.1 — Matching Service (`app/services/matching.py`)

```python
from rapidfuzz import process, fuzz
import re

CONFIDENCE_THRESHOLDS = {
    'auto_approve': 95,
    'needs_review': 75,
}

OCR_CORRECTIONS = {
    r'\b0\b': 'O',
    r'rn': 'm',
    r'\bl\b': 'I',
}

def normalize_name(name: str) -> str:
    """Clean a single name string for matching."""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)  # remove punctuation
    name = re.sub(r'\s+', ' ', name)     # collapse spaces
    for pattern, replacement in OCR_CORRECTIONS.items():
        name = re.sub(pattern, replacement, name)
    return name

def match_name(ocr_name: str, candidates: list[str]) -> dict:
    """
    Match one OCR name against official student list.
    Returns { matched, score, status }
    """
    normalized_ocr = normalize_name(ocr_name)
    normalized_candidates = {normalize_name(c): c for c in candidates}

    result = process.extractOne(
        normalized_ocr,
        list(normalized_candidates.keys()),
        scorer=fuzz.token_sort_ratio
    )

    if not result:
        return {'matched': None, 'score': 0, 'status': 'unrecognized'}

    matched_normalized, score, _ = result
    matched_original = normalized_candidates[matched_normalized]

    if score >= CONFIDENCE_THRESHOLDS['auto_approve']:
        status = 'auto_approved'
    elif score >= CONFIDENCE_THRESHOLDS['needs_review']:
        status = 'needs_review'
    else:
        status = 'unrecognized'

    return {'matched': matched_original, 'score': score, 'status': status}

def match_all(ocr_names: list[str], candidates: list[str]) -> list[dict]:
    """Match a full OCR name list against the official student roster."""
    return [
        {'ocr_raw': name, **match_name(name, candidates)}
        for name in ocr_names
    ]
```

- [ ] Test on real Rwandan name data (short names, French names, repeated family names)
- [ ] Add `token_set_ratio` as secondary scorer for names with swapped tokens
- [ ] Log all match results with scores in `attendance_records`

---

## Phase 5 — Celery Task Queues (Week 3–4)

### 5.1 — Celery Setup (`app/tasks/celery_app.py`)

```python
from celery import Celery
from app.config import settings

celery_app = Celery(
    'attendance',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.ocr_tasks',
        'app.tasks.validation_tasks',
        'app.tasks.export_tasks',
    ]
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Africa/Kigali',
    task_routes={
        'app.tasks.ocr_tasks.*': {'queue': 'ocr'},
        'app.tasks.validation_tasks.*': {'queue': 'validation'},
        'app.tasks.export_tasks.*': {'queue': 'export'},
    },
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
```

### 5.2 — OCR Task (`app/tasks/ocr_tasks.py`)

```python
from app.tasks.celery_app import celery_app
from app.services.preprocessing import preprocess_image
from app.services.ocr import OCRService
from app.services.drive import DriveService

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_screenshot(self, job_id: str, image_bytes_b64: str, session_id: str):
    import base64, time
    from app.database import get_session
    from app.models.ocr_job import OCRJob

    try:
        raw_bytes = base64.b64decode(image_bytes_b64)
        processed_bytes = preprocess_image(raw_bytes)

        drive = DriveService(settings.GOOGLE_CREDENTIALS_PATH)
        raw_folder = drive.get_or_create_folder('Raw Screenshots')
        proc_folder = drive.get_or_create_folder('Processed Images')

        raw_id = drive.upload_bytes(raw_bytes, f'{job_id}-raw.jpg', raw_folder)
        proc_id = drive.upload_bytes(processed_bytes, f'{job_id}-processed.jpg', proc_folder)

        ocr = OCRService()
        start = time.time()
        text, engine = ocr.extract(processed_bytes)
        duration_ms = int((time.time() - start) * 1000)

        names = ocr.normalize_names(text)

        with get_session() as db:
            job = db.get(OCRJob, job_id)
            job.raw_image_drive_id = raw_id
            job.processed_image_drive_id = proc_id
            job.raw_ocr_text = text
            job.engine = engine
            job.duration_ms = duration_ms
            job.status = 'completed'
            db.commit()

        validate_attendance.delay(session_id, names)

    except Exception as exc:
        raise self.retry(exc=exc)
```

- [ ] Create three queues: `ocr`, `validation`, `export`
- [ ] Set retry policies per queue
- [ ] Add Flower monitoring UI for queue visibility

---

## Phase 6 — Telegram Bot (Week 4–5)

### 6.1 — Bot Setup (`app/bot/bot.py`)

```python
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

def create_bot(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("upload", upload_handler))
    app.add_handler(CommandHandler("report", report_handler))
    app.add_handler(CommandHandler("history", history_handler))
    app.add_handler(CommandHandler("check", check_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(confirm_handler, pattern=r'^confirm_'))
    app.add_handler(CallbackQueryHandler(reject_handler, pattern=r'^reject_'))
    return app
```

### 6.2 — Confirmation Workflow

When `needs_review` records exist, bot sends:

```
⚠️ Review required — SheCanCODE A1 | 2026-05-09

1. "Jhon Doe"    →  John Doe      (82%)
2. "Alic Smth"   →  Alice Smith   (76%)
3. "Mugsh"       →  Mugisha       (71%)

[ ✅ Approve all ]   [ 📝 Review one by one ]
```

- [ ] Build `keyboards.py` with inline keyboard builders
- [ ] Implement approve-all and one-by-one review flows
- [ ] Allow teacher to type a corrected name inline
- [ ] Timeout: send reminder after 6 hours, escalate after 24
- [ ] Send final summary when all records are resolved

### 6.3 — Bot Commands

```
/start        — Register and show welcome
/upload       — Upload screenshot (or just send the photo)
/check        — Status of current pending jobs
/report       — Generate report for a class + date
/export       — Export to PDF, sync to Google Drive
/history      — View last 10 sessions
/help         — List all commands
```

---

## Phase 7 — PDF Reports + Drive Sync (Week 5–6)

### 7.1 — Report Generator (`app/services/pdf.py`)

```python
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

def generate_attendance_pdf(session_data: dict) -> bytes:
    """Render HTML template to PDF bytes."""
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('attendance_report.html')
    html_content = template.render(**session_data)
    return HTML(string=html_content).write_pdf()
```

**`templates/attendance_report.html`** should include:
- Class name, date, instructor
- Student list with status (present / absent / unrecognized)
- Confidence scores for auto-approved entries
- Human reviewer name for manually approved entries
- Summary stats: total, present, absent, % attendance

### 7.2 — Drive Sync Task (`app/tasks/export_tasks.py`)

```python
@celery_app.task
def export_report_to_drive(session_id: str, telegram_chat_id: int):
    from app.services.pdf import generate_attendance_pdf
    from app.services.drive import DriveService

    session = get_session_with_records(session_id)
    pdf_bytes = generate_attendance_pdf(session)

    drive = DriveService(settings.GOOGLE_CREDENTIALS_PATH)
    reports_folder = drive.get_or_create_folder('Reports')
    class_folder = drive.get_or_create_folder(session.class_name, reports_folder)

    filename = f"attendance-{session.date}.pdf"
    file_id = drive.upload_bytes(pdf_bytes, filename, class_folder, 'application/pdf')
    link = drive.get_shareable_link(file_id)

    send_telegram_message(telegram_chat_id, f"✅ Report ready:\n{link}")
```

- [ ] Store Drive file ID in database for deduplication
- [ ] Overwrite existing report if re-exported for same session
- [ ] Send shareable link to teacher via Telegram immediately after upload

---

## Phase 8 — Deployment (Week 7–8)

### 8.1 — Docker Setup

**`docker-compose.yml`** (local dev):
```yaml
version: '3.9'
services:
  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes: ['.:/app']
    env_file: .env
    depends_on: [postgres, redis]

  bot:
    build: .
    command: python -m app.bot.bot
    env_file: .env
    depends_on: [api, redis]

  worker-ocr:
    build: .
    command: celery -A app.tasks.celery_app worker -Q ocr -c 2
    env_file: .env
    depends_on: [redis, postgres]

  worker-validation:
    build: .
    command: celery -A app.tasks.celery_app worker -Q validation -c 4
    env_file: .env
    depends_on: [redis, postgres]

  worker-export:
    build: .
    command: celery -A app.tasks.celery_app worker -Q export -c 2
    env_file: .env
    depends_on: [redis, postgres]

  flower:
    build: .
    command: celery -A app.tasks.celery_app flower --port=5555
    ports: ['5555:5555']
    env_file: .env

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: attendance
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes: ['pgdata:/var/lib/postgresql/data']

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

### 8.2 — Railway Deployment

Deploy these as separate Railway services from the same repo:

| Service | Start command |
|---|---|
| API | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Telegram bot | `python -m app.bot.bot` |
| OCR worker | `celery -A app.tasks.celery_app worker -Q ocr -c 2` |
| Validation worker | `celery -A app.tasks.celery_app worker -Q validation -c 4` |
| Export worker | `celery -A app.tasks.celery_app worker -Q export -c 2` |
| Flower | `celery -A app.tasks.celery_app flower` |

- [ ] Set all env vars in Railway dashboard
- [ ] Configure Supabase PostgreSQL connection string
- [ ] Add Upstash Redis or Railway Redis plugin
- [ ] Set `GOOGLE_CREDENTIALS_JSON` as base64-encoded env var (no file upload needed)

---

## Environment Variables (`.env.example`)

```env
# Database
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/attendance

# Redis
REDIS_URL=redis://localhost:6379/0

# Google
GOOGLE_CREDENTIALS_PATH=./credentials.json
GOOGLE_DRIVE_ROOT_FOLDER_ID=your-folder-id-here

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# App
SECRET_KEY=your-secret-key
ENVIRONMENT=development
LOG_LEVEL=INFO

# OCR
OCR_PRIMARY_ENGINE=google_vision
OCR_FALLBACK_ENGINE=tesseract
```

---

## Confidence Scoring Reference

| Score | Status | Action |
|---|---|---|
| ≥ 95% | `auto_approved` | Saved immediately, no human needed |
| 75–94% | `needs_review` | Sent to Telegram for teacher confirmation |
| 50–74% | `low_confidence` | Flagged, teacher must type corrected name |
| < 50% | `unrecognized` | Treated as absent, teacher notified |

---

## Immediate Next Steps

1. `git init` and set up the folder structure above
2. Run `docker compose up` and confirm Postgres + Redis are healthy
3. Run the first Alembic migration
4. Implement `drive.py` and test upload with a dummy file
5. Wire up `/upload` in the Telegram bot end-to-end (no AI yet — just store the file)
6. Add preprocessing and OCR on top of the working upload flow
7. Add RapidFuzz matching once OCR output is confirmed clean
8. Only then build the confirmation keyboard and PDF export

---

## README

```md
# Smart Attendance AI

AI-powered attendance automation built entirely in Python.
Extracts student names from attendance screenshots via OCR,
corrects them using fuzzy matching, routes uncertain entries
through Telegram for human approval, and syncs final reports
to Google Drive.

## Stack

FastAPI · python-telegram-bot · Google Cloud Vision · RapidFuzz ·
Celery · Redis · PostgreSQL · Google Drive API · WeasyPrint · Railway

## Quickstart

git clone https://github.com/your-org/smart-attendance-ai
cd smart-attendance-ai
cp .env.example .env          # fill in your credentials
docker compose up             # starts api, bot, workers, postgres, redis
```