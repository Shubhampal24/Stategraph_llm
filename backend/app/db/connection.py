import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection

from ..core.config import settings

_pool: AsyncConnectionPool | None = None

def get_db_pool() -> AsyncConnectionPool:
    if _pool is None:
        raise RuntimeError("Database pool has not been initialized.")
    return _pool

async def init_db_pool():
    global _pool
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL must be configured.")
    
    # We use AsyncConnectionPool since FastAPI is async
    _pool = AsyncConnectionPool(
        settings.database_url,
        min_size=1,
        max_size=10,
        open=False,
        timeout=3,
        kwargs={"autocommit": True}
    )
    await _pool.open()

async def close_db_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

@asynccontextmanager
async def get_connection() -> AsyncGenerator[AsyncConnection, None]:
    pool = get_db_pool()
    async with pool.connection() as conn:
        yield conn
