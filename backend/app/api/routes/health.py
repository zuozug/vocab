from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.core.database import ping_database

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.app_env,
    }


@router.get("/health/db")
def database_health_check() -> dict[str, str]:
    try:
        version = ping_database()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc

    return {
        "status": "ok",
        "database": version,
    }
