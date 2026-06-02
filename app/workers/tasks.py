from app.workers.celery_app import celery_app


@celery_app.task(name="ai.generate_insights")
def generate_ai_insights(user_id: str) -> dict[str, str]:
    return {"user_id": user_id, "status": "queued"}


@celery_app.task(name="goals.process_daily")
def process_daily_goals() -> dict[str, str]:
    return {"status": "queued"}


@celery_app.task(name="summaries.generate_weekly")
def generate_weekly_summaries() -> dict[str, str]:
    return {"status": "queued"}


@celery_app.task(name="notifications.process")
def process_notifications() -> dict[str, str]:
    return {"status": "queued"}


@celery_app.task(name="cleanup.expired_cache")
def cleanup_expired_cache() -> dict[str, str]:
    return {"status": "queued"}

