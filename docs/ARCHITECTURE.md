# Architecture

- `apps/web`: React + Vite + Framer Motion + Lucide icons; responsive app shell, sign-in/register, dynamic module workspaces, record CRUD UI.
- `apps/api`: FastAPI, SQLAlchemy, JWT sessions, password hashing, per-user ownership on records, dashboard aggregation, scheme directory, safety-first rule-based advisor.
- `docker-compose.yml`: deploys web and API; persistent SQLite volume by default. `DATABASE_URL` can point at PostgreSQL.
- Data model: `users` and `records`; flexible `data_json` allows module-specific fields while common fields remain searchable.
- REST endpoints: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/records`, `/api/dashboard`, `/api/modules`, `/api/schemes`, `/api/advisor`.
- Production extensions: formal schema migrations, domain-specific validation, external provider adapters, validated AI inference, object storage, audit logging, observability and automated tests.
