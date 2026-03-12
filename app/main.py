from fastapi import FastAPI
from sqlalchemy import text
from app.db import engine
from app.cache import r
import pandas as pd

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Log Analytics API"}

@app.get("/error_count")
def error_count():

    cached = r.get("error_count")

    if cached:
        return {"source": "cache", "count": int(cached)}

    query = """
    SELECT COUNT(*) FROM server_logs
    WHERE status='ERROR'
    """

    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()[0]

    r.set("error_count", result, ex=60)

    return {"source": "database", "count": result}

@app.get("/errors_per_hour")
def errors_per_hour():

    query = """
    SELECT
    DATE_TRUNC('hour', timestamp) AS hour,
    COUNT(*) AS errors
    FROM server_logs
    WHERE status='ERROR'
    GROUP BY hour
    ORDER BY hour
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        data = [dict(row._mapping) for row in result]

    return data

@app.get("/server_failure_rate")
def server_failure_rate():

    query = """
    SELECT
    server_name,
    COUNT(*) FILTER (WHERE status='ERROR') * 100.0 / COUNT(*) AS failure_rate
    FROM server_logs
    GROUP BY server_name
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        data = [dict(row._mapping) for row in result]

    return data

@app.get("/top_failing_services")
def top_failing_services():

    query = """
    SELECT
    process_name,
    COUNT(*) AS errors
    FROM server_logs
    WHERE status='ERROR'
    GROUP BY process_name
    ORDER BY errors DESC
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        data = [dict(row._mapping) for row in result]

    return data