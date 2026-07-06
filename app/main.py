from contextlib import asynccontextmanager
import traceback
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.redis import close_redis, init_redis
from app.core.security import SecureHeadersMiddleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_redis()
    yield
    await close_redis()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"Internal Server Error: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecureHeadersMiddleware)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


