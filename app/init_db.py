from sqlalchemy import text
from db import engine

create_table = """
CREATE TABLE IF NOT EXISTS server_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    server_name TEXT,
    process_name TEXT,
    status TEXT,
    response_time INT
);
"""

with engine.connect() as conn:
    conn.execute(text(create_table))
    conn.commit()