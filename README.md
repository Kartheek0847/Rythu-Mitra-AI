# Rythu Mitra — AI-Powered Agricultural Assistant

Full-stack agriculture workspace with a React + Vite frontend and FastAPI backend. It provides authenticated farm records, dashboard summaries, a starter schemes catalogue, and a safety-first rule-based farm advisor.

## Repository layout
- `apps/api/main.py` — FastAPI authentication, records, dashboard, schemes and advisor endpoints.
- `apps/api/requirements.txt` — API dependencies, including the bcrypt compatibility pin.
- `apps/api/Dockerfile` and `docker-compose.yml` — container configuration.
- `source/Rythu-Mitra-Web.zip` — React frontend source; extract at repository root to restore `apps/web/`.
- `docs/ARCHITECTURE.md` and `deploy/DEPLOYMENT.md` — architecture and deployment notes.

## Run locally
1. Install Docker Desktop.
2. Copy `.env.example` to `.env` and set a strong, unique `JWT_SECRET`.
3. Extract `source/Rythu-Mitra-Web.zip` at the repository root.
4. Run `docker compose up --build`.
5. Open the frontend at http://localhost:8080 and API docs at http://localhost:8000/docs.

## Authentication dependency compatibility
The API pins `passlib==1.7.4` and `bcrypt==4.0.1`. This avoids the Passlib/bcrypt 5.x compatibility problem that caused registration to fail with the bcrypt 72-byte password error. Do not upgrade bcrypt independently without changing the hashing implementation and testing registration and login.

## Production notes
Use a strong `JWT_SECRET`, persistent PostgreSQL `DATABASE_URL`, and explicit `CORS_ORIGINS`. The advisor is rule-based, not a trained diagnostic model. Verify scheme details against official sources. Configure private object storage and malware scanning before enabling document uploads.
