# Deployment Strategy

## Railway MVP

1. Provision PostgreSQL with TimescaleDB support and Redis.
2. Set environment variables from `.env.example`.
3. Deploy the API image and a separate Celery worker image.
4. Run `alembic upgrade head` during release.

## AWS Future

- API: ECS Fargate behind ALB.
- Database: RDS PostgreSQL 16 with TimescaleDB or Timescale Cloud.
- Cache/Queue: ElastiCache Redis.
- Storage: Cloudflare R2 or S3-compatible object storage.
- Observability: structured logs, metrics, tracing, and alerting.
- Secrets: AWS Secrets Manager or SSM Parameter Store.

