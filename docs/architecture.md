# FYFIT Backend Architecture

FYFIT uses a modular monolith with Clean Architecture boundaries:

- Routers only perform HTTP concerns and dependency injection.
- Services contain business workflows.
- Repositories isolate database access.
- Device integrations normalize vendor-specific payloads into FYFIT internal readings.
- TimescaleDB hypertables store high-volume sensor streams.
- Redis supports API cache, AI cache, rate limiting, and Celery queues.

## Scaling To 1M+ Users

- Partition sensor data by Timescale hypertables and keep indexes aligned to `user_id`, `device_id`, and time.
- Ingest mobile syncs with batch inserts and idempotency constraints on `device_id + recorded_at`.
- Move heavy AI, goal, notification, and cleanup jobs to Celery workers.
- Cache repeated AI inputs by stable input hash to control LLM cost.
- Deploy MVP on Railway; migrate to AWS ECS, RDS Postgres/Timescale, ElastiCache, and S3/R2 for production scale.

## Coding Standards

- Keep routes thin.
- Never access the database directly from route handlers.
- Add new wearable models by implementing `DevicePayloadParser` and registering it in `DEVICE_REGISTRY`.
- Prefer explicit schemas at API boundaries.
- Use UUID primary keys, foreign keys, timestamps, and soft deletes where lifecycle matters.

