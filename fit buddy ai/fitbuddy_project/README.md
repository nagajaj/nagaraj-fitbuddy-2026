# FitBuddy — AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite application based on the supplied project documentation. It generates personalized 7-day workout plans, nutrition/recovery tips, and feedback-based plan revisions using Google Gemini.

## Stack

- FastAPI + Uvicorn
- Jinja2 + HTML/CSS
- SQLAlchemy + SQLite
- Pydantic validation
- Google Gen AI Python SDK (`google-genai`)
- Pytest + FastAPI TestClient

## Features

- Home form for name, user ID, age, weight, goal, and intensity
- AI-generated 7-day workout plan
- AI-generated nutrition/recovery tip
- Feedback-driven workout revision
- SQLite persistence of original and updated plans
- Admin/demo dashboard at `/view-all-users`
- JSON API endpoints and automatic Swagger docs at `/docs`
- Local mock mode so the app can be tested without an API key

## Gemini configuration

The source documentation names Gemini 1.5 Pro and Gemini Flash. Those model names are outdated for a current implementation, so the project uses current model IDs through environment variables. The defaults are `gemini-3.1-pro-preview` for workout planning and `gemini-3.1-flash-lite` for fast tips. See the official Gemini model documentation for current availability.

Copy `.env.example` to `.env`, add `GEMINI_API_KEY`, and set `MOCK_AI=false` for live generation.

## Run

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env       # Windows cmd
# or: cp .env.example .env  # macOS/Linux

uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs.

## Test

```bash
pytest -q
```

The tests run in mock-AI mode and do not require a Gemini API key.

## Notes

The supplied documentation describes an admin dashboard but does not specify authentication. Accordingly, `/view-all-users` is a demo/admin view without authentication. Add authentication before deploying it publicly.

Generated fitness content is informational and should not be treated as medical advice.
