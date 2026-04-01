# LLM Tools API

Minimal FastAPI backend with two deployable endpoints:

- `POST /question/evaluate`
- `POST /question/transcribe`

This project does not use a database.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`.

## Run locally

```bash
uvicorn app.main:app --reload
```

Server URLs:

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Endpoints

### Evaluate

```bash
curl -X POST http://127.0.0.1:8000/question/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "studentName": "Aarav",
    "studentClass": 6,
    "questions": [
      {
        "id": 1,
        "section": "Reading",
        "type": "MCQ",
        "question": "What is the main idea of the passage?",
        "options": [
          {"label": "A", "text": "Option A"},
          {"label": "B", "text": "Option B"}
        ],
        "correctAnswer": "A"
      }
    ],
    "answers": {
      "1": "B"
    }
  }'
```

### Transcribe

```bash
curl -X POST http://127.0.0.1:8000/question/transcribe \
  -F "audio=@sample.webm"
```

## Deploy

Any platform that supports FastAPI/Uvicorn can run this app. A typical start command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
