from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.chat import router as chat_router
from .api.health import router as health_router
from .api.state import router as state_router
from .api.threads import router as threads_router
from .core.config import settings
from .graph.checkpoint import create_checkpointer
from .graph.graph import build_graph
from .services.conversation_service import create_conversation_service


from .db.connection import init_db_pool, close_db_pool
from .db.init_db import init_db

checkpointer = create_checkpointer()
graph = build_graph(checkpointer)
conversation_service = create_conversation_service(graph)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database pool
    try:
        await init_db_pool()
        # Create tables if they do not exist
        await init_db()
    except Exception as e:
        print(f"Warning: PostgreSQL database initialization failed: {e}")
    yield
    # Close the database pool on shutdown
    try:
        await close_db_pool()
    except Exception:
        pass
    try:
        from .graph.checkpoint import close_checkpoint_pool
        close_checkpoint_pool()
    except Exception:
        pass


app = FastAPI(
    title="StateFlow",
    version="1.0.0",
    description="OS3 L2-05 LangGraph Stateful Conversational Agent",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(state_router)
app.include_router(threads_router)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "assignment": "L2-05",
        "status": "ok",
        "docs": "/docs",
    }
