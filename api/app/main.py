import os
import time
import random
from typing import Optional

import psycopg2
from fastapi import FastAPI, Response
from pydantic import BaseModel

# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

APP_VERSION = os.getenv("APP_VERSION", "0.0.0")
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g., postgresql+psycopg2://user:pass@db:5432/appdb

app = FastAPI(title="YouAreBot API (Sprint 1)", version=APP_VERSION)

# Simple metrics
REQ_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQ_LATENCY = Histogram("http_request_duration_seconds", "Latency (s) per endpoint", ["endpoint"])

class PredictIn(BaseModel):
    text: str
    conversation_id: Optional[str] = None

def _connect_db():
    # DATABASE_URL is sqlalchemy-style; psycopg2 wants a different form
    # Accept both: if it startswith postgresql+psycopg2, strip the driver
    if not DATABASE_URL:
        return None
    url = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
    return psycopg2.connect(url)

@app.middleware("http")
async def add_metrics(request, call_next):
    start = time.perf_counter()
    resp = await call_next(request)
    elapsed = time.perf_counter() - start
    endpoint = request.url.path
    REQ_COUNT.labels(request.method, endpoint, resp.status_code).inc()
    REQ_LATENCY.labels(endpoint).observe(elapsed)
    return resp

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "api", "version": APP_VERSION}

@app.get("/version")
def version():
    return {"version": APP_VERSION}

@app.get("/db-health")
def db_health():
    try:
        conn = _connect_db()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
            conn.close()
            return {"db": "ok"}
        else:
            return {"db": "not-configured"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict")
def predict(inp: PredictIn):
    """
    Sprint 1 placeholder: randomly guess 'bot' or 'human'.
    We'll replace this with a real model in later sprints.
    """
    label = random.choice(["bot", "human"])
    proba = random.random()
    return {
        "label": label,
        "confidence": round(proba, 4),
        "version": APP_VERSION,
        "note": "Placeholder prediction (Sprint 1)."
    }
