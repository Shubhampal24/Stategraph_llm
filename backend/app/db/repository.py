from typing import List, Dict, Any, Optional
from datetime import datetime
from .connection import get_connection

class ThreadRepository:
    @staticmethod
    async def create_thread(thread_id: str, title: str) -> None:
        async with get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO threads (thread_id, title) VALUES (%s, %s) ON CONFLICT (thread_id) DO NOTHING",
                    (thread_id, title)
                )

    @staticmethod
    async def list_threads() -> List[Dict[str, Any]]:
        async with get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT thread_id, title, created_at, updated_at FROM threads ORDER BY updated_at DESC"
                )
                rows = await cur.fetchall()
                return [
                    {
                        "thread_id": row[0],
                        "title": row[1],
                        "created_at": row[2].isoformat() if row[2] else None,
                        "updated_at": row[3].isoformat() if row[3] else None
                    }
                    for row in rows
                ]

    @staticmethod
    async def get_thread(thread_id: str) -> Optional[Dict[str, Any]]:
        async with get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT thread_id, title, created_at, updated_at FROM threads WHERE thread_id = %s",
                    (thread_id,)
                )
                row = await cur.fetchone()
                if not row:
                    return None
                return {
                    "thread_id": row[0],
                    "title": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "updated_at": row[3].isoformat() if row[3] else None
                }

    @staticmethod
    async def add_message(thread_id: str, role: str, content: str) -> None:
        async with get_connection() as conn:
            async with conn.cursor() as cur:
                # Update thread's updated_at
                await cur.execute(
                    "UPDATE threads SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = %s",
                    (thread_id,)
                )
                
                # We need to make sure we don't store duplicate adjacent messages if LangGraph retries/resumes.
                # Actually, the user says "Store the user message exactly once. Store the assistant response exactly once."
                # We can check the last message to avoid exact duplicates for the same role and content, or just trust the application layer to call this exactly once per turn.
                # The assignment says "Do not create duplicate application messages."
                await cur.execute(
                    """
                    SELECT role, content FROM messages 
                    WHERE thread_id = %s 
                    ORDER BY id DESC LIMIT 1
                    """,
                    (thread_id,)
                )
                last_msg = await cur.fetchone()
                if last_msg and last_msg[0] == role and last_msg[1] == content:
                    return # Duplicate
                
                await cur.execute(
                    "INSERT INTO messages (thread_id, role, content) VALUES (%s, %s, %s)",
                    (thread_id, role, content)
                )

    @staticmethod
    async def get_messages(thread_id: str) -> List[Dict[str, Any]]:
        async with get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT role, content, created_at FROM messages WHERE thread_id = %s ORDER BY id ASC",
                    (thread_id,)
                )
                rows = await cur.fetchall()
                return [
                    {
                        "role": row[0],
                        "content": row[1],
                        "created_at": row[2].isoformat() if row[2] else None
                    }
                    for row in rows
                ]
