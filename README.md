# Rythu Mitra — AI-Powered Agricultural Assistant

Rythu Mitra is a full-stack agriculture operations workspace for farmers. The project includes a React + Vite frontend and a FastAPI backend with authenticated farm records, dashboard summaries, starter government-scheme references, and a safety-first rule-based farm advisor.

## Project structure

The complete source package is included at `source/Rythu-Mitra-AI-Source.zip`. Extract it to access the original `rythu-mitra/` project directory. Key backend files are also published directly under `apps/api/`.

- `apps/api/main.py` — FastAPI application, authentication, records, dashboard and advisor endpoints.
- `apps/api/requirements.txt` — Python dependencies.
- `docker-compose.yml` — local API + frontend deployment.
- `source/Rythu-Mitra-AI-Source.zip` — complete frontend, backend, docs and deployment source package.

## Run locally

1. Install Docker Desktop.
2. Copy `.env.example` to `.env` and set a strong, unique `JWT_SECRET`.
3. Run `docker compose up --build`.
4. Open the frontend at http://localhost:8080 and API docs at http://localhost:8000/docs.

## Authentication dependency compatibility

The API pins `passlib==1.7.4` and `bcrypt==4.0.1`. This avoids the Passlib/bcrypt 5.x compatibility problem that caused registration to fail with the bcrypt 72-byte password error. Do not upgrade bcrypt independently without changing the password hashing implementation and testing registration and login.

## Production notes

Set a strong `JWT_SECRET`, a persistent PostgreSQL `DATABASE_URL`, and an explicit `CORS_ORIGINS`. The current advisor is rule-based, not a trained diagnostic model. Scheme details must be checked with official sources. Configure private object storage and malware scanning before enabling document uploads.
