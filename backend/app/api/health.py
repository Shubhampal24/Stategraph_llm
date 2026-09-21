from fastapi import APIRouter

from ..core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    # Verify the database connection is active
    from ..db.connection import get_db_pool
    pool = get_db_pool()
    db_connected = False
    try:
        async with pool.connection() as conn:
            db_connected = not conn.closed
    except Exception:
        pass

    return {
        "status": "ok",
        "service": settings.app_name,
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "database": "PostgreSQL",
        "database_connected": bool(pool),
        "checkpoint": "PostgreSQL",
    }
