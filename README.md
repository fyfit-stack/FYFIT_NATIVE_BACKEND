# FYFIT Backend

Production-grade FastAPI backend scaffold for the FYFIT wearable ecosystem.

## Stack

- Python 3.12, FastAPI, Pydantic v2
- PostgreSQL 16 + TimescaleDB
- SQLAlchemy 2.0, Alembic
- Redis, Celery
- Firebase Auth as identity provider
- Device parser registry for future wearable payloads

## Development

```bash
cp .env.example .env
docker compose up -d
docker compose exec api alembic upgrade head
```

API docs are available at `http://localhost:8000/docs`.

# FYFIT_NATIVE_BACKEND
