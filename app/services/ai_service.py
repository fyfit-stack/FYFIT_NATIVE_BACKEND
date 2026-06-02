import hashlib
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai import AISuggestion
from app.models.user import User
from app.repositories.health_repository import HealthRepository


class AIInsightService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.health = HealthRepository(db)

    async def generate(self, user: User, suggestion_type: str) -> AISuggestion:
        evidence = await self.health.summary(user.id)
        input_hash = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
        suggestion = AISuggestion(
            user_id=user.id,
            suggestion_type=suggestion_type,
            title=f"{suggestion_type.replace('_', ' ').title()} Insight",
            body=self._template_body(suggestion_type, evidence),
            model_provider="local-template",
            model_name="fyfit-cost-safe-v1",
            input_hash=input_hash,
            evidence=evidence,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=12),
        )
        self.db.add(suggestion)
        await self.db.commit()
        await self.db.refresh(suggestion)
        return suggestion

    @staticmethod
    def _template_body(suggestion_type: str, evidence: dict) -> str:
        return (
            f"Generated {suggestion_type} from latest FYFIT signals. "
            f"HR={evidence.get('latest_heart_rate')}, SpO2={evidence.get('latest_spo2')}, "
            f"stress={evidence.get('stress_latest')}. Configure OpenAI/Claude providers for LLM output."
        )

