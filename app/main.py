import json

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from app.db import engine
from app.cache import r

app = FastAPI()

ANALYTICS_CACHE_TTL = 600


def get_cached_data(cache_key):
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    return None


def set_cached_data(cache_key, data):
    r.set(cache_key, json.dumps(jsonable_encoder(data)), ex=ANALYTICS_CACHE_TTL)

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

    r.set("error_count", result, ex=ANALYTICS_CACHE_TTL)

    return {"source": "database", "count": result}

@app.get("/errors_per_hour")
def errors_per_hour():
    cached = get_cached_data("errors_per_hour")
    if cached:
        return cached

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

    set_cached_data("errors_per_hour", data)
    return data

@app.get("/server_failure_rate")
def server_failure_rate():
    cached = get_cached_data("server_failure_rate")
    if cached:
        return cached

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

    set_cached_data("server_failure_rate", data)
    return data

@app.get("/top_failing_services")
def top_failing_services():
    cached = get_cached_data("top_failing_services")
    if cached:
        return cached

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

    set_cached_data("top_failing_services", data)
    return data
