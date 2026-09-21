from .connection import get_connection

async def init_db():
    async with get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    thread_id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    thread_id VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_thread
                        FOREIGN KEY(thread_id) 
                        REFERENCES threads(thread_id)
                        ON DELETE CASCADE
                )
            """)
            
            await cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id)
            """)
