---
name: start
description: Start the development server with a fresh database. Resets the database, runs migrations and seeds, then starts uvicorn.
---

# Start Development Server

Run the following steps:

1. Ensure Docker Compose is running (postgres):
```bash
docker compose up -d
```

2. Wait a moment for postgres to be ready, then reset the database:
```bash
sleep 2 && ./scripts/reset_db.sh
```

3. Start the uvicorn server:
```bash
source .venv/bin/activate && uvicorn main:app --reload
```

4. In a separate terminal, start the frontend server:
```bash
cd frontend && python -m http.server 3000
```

After starting, the services will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Frontend: http://localhost:3000