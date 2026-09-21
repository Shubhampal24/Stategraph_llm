from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from ..core.config import settings

_checkpoint_pool = None

def get_checkpoint_pool(db_url: str | None = None) -> ConnectionPool:
    global _checkpoint_pool
    if _checkpoint_pool is None:
        url = db_url or settings.database_url
        _checkpoint_pool = ConnectionPool(
            conninfo=url,
            max_size=20,
            kwargs={
                "autocommit": True,
            }
        )
    return _checkpoint_pool

def close_checkpoint_pool():
    global _checkpoint_pool
    if _checkpoint_pool is not None:
        _checkpoint_pool.close()
        _checkpoint_pool = None

def create_checkpointer(db_url: str | None = None) -> PostgresSaver:
    pool = get_checkpoint_pool(db_url)
    saver = PostgresSaver(pool)
    saver.setup()
    return saver
