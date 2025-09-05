# db_service.py
import os
import psycopg2
import psycopg2.pool
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# Prefer DATABASE_URL; else build from PG* vars
DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"postgresql://{os.getenv('PGUSER','postgres')}:{os.getenv('PGPASSWORD','postgres')}"
    f"@{os.getenv('PGHOST','localhost')}:{os.getenv('PGPORT','5432')}/{os.getenv('PGDATABASE','chatbot')}"
)

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=DATABASE_URL,
            sslmode=os.getenv("PGSSLMODE", "disable")
        )
    return _pool

@contextmanager
def get_conn():
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

def run_migrations():
    """
    Idempotent schema creation (safe to run many times).
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Ensure pgcrypto for gen_random_uuid()
            cur.execute("""CREATE EXTENSION IF NOT EXISTS pgcrypto;""")

            # Users table (consistent name with your earlier dumps)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            # Reset tokens for password reset
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reset_tokens (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMPTZ NOT NULL
                );
            """)

            # Conversations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES app_users(id) ON DELETE CASCADE,
                    title TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            # Messages table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

        conn.commit()
