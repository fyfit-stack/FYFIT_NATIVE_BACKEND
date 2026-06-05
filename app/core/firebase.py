import json
from functools import lru_cache

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings
from app.core.logger import get_logger

bearer_scheme = HTTPBearer(auto_error=False)
logger = get_logger(__name__)


@lru_cache
def init_firebase() -> firebase_admin.App:
    if firebase_admin._apps:
        return firebase_admin.get_app()

    if settings.firebase_credentials_json:
        cred = credentials.Certificate(json.loads(settings.firebase_credentials_json))
        return firebase_admin.initialize_app(cred)

    return firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})


def verify_firebase_token_without_admin(token: str) -> dict:
    if not settings.firebase_project_id:
        raise ValueError("FIREBASE_PROJECT_ID is required")

    claims = id_token.verify_firebase_token(
        token,
        requests.Request(),
        audience=settings.firebase_project_id,
    )
    if claims.get("iss") != f"https://securetoken.google.com/{settings.firebase_project_id}":
        raise ValueError("Invalid Firebase token issuer")
    if "uid" not in claims and "sub" in claims:
        claims["uid"] = claims["sub"]
    return claims


async def verify_firebase_token(
    credentials_: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials_ is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    try:
        if settings.firebase_credentials_json:
            init_firebase()
            return auth.verify_id_token(credentials_.credentials)
        return verify_firebase_token_without_admin(credentials_.credentials)
    except Exception as exc:
        logger.exception("Firebase token verification failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase token") from exc

