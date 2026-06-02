import json
from functools import lru_cache

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def init_firebase() -> firebase_admin.App:
    if firebase_admin._apps:
        return firebase_admin.get_app()

    if settings.firebase_credentials_json:
        cred = credentials.Certificate(json.loads(settings.firebase_credentials_json))
        return firebase_admin.initialize_app(cred)

    return firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})


async def verify_firebase_token(
    credentials_: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials_ is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    init_firebase()
    try:
        return auth.verify_id_token(credentials_.credentials)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase token") from exc

