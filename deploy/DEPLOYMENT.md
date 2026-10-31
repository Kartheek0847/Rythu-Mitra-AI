# Deployment checklist

1. Configure a unique `JWT_SECRET` and production `DATABASE_URL`.
2. Set `CORS_ORIGINS` to exact deployed frontend domains.
3. Put the application behind HTTPS/TLS and a reverse proxy.
4. Use managed PostgreSQL and backups for production; SQLite is convenient for single-instance evaluation.
5. Configure monitoring, request limits, database migrations, logs and incident alerts.
6. Integrate and test weather/market/scheme sources, AI models, regional language support, secure file storage and IoT credentials before enabling them for farmers.
7. Verify all scheme links, rules and current deadlines directly with official departments.
