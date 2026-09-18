import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            event_type TEXT NOT NULL,
            user_identifier TEXT,
            status TEXT NOT NULL,
            details TEXT,
            source_service TEXT,
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def log_event(event_type, user_identifier, status, details=None, source_service=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (event_type, user_identifier, status, details, source_service, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        event_type,
        user_identifier,
        status,
        details,
        source_service,
        datetime.now(timezone.utc)
    ))
    event_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return event_id


def query_events(user_identifier=None, event_type=None, status=None, limit=100):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if user_identifier:
        query += " AND user_identifier = %s"
        params.append(user_identifier)
    if event_type:
        query += " AND event_type = %s"
        params.append(event_type)
    if status:
        query += " AND status = %s"
        params.append(status)

    query += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [dict(row) for row in rows]
