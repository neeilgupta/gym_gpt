# apps/backend/routes/logs.py
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.db import init_db, add_log, get_logs

router = APIRouter()
init_db()  # ensure table + index exist once on import

# Request model (what clients send)
class Log(BaseModel):
    name: str
    reps: int
    weight_kg: float
    rir: int
    focus: Optional[str] = None

# Response model (what we return from DB)
class LogRow(BaseModel):
    id: int
    name: str
    reps: int
    weight_kg: float
    rir: int
    focus: Optional[str] = None
    timestamp: str  # stored by SQLite as text

@router.post("/", response_model=Dict[str, LogRow])
def add(log: Log):
    """Insert a log row and return it."""
    added = add_log(log.name, log.reps, log.weight_kg, log.rir, log.focus)
    # 'added' is a dict from services.db; validate to LogRow on the way out
    return {"added": LogRow(**added)}

@router.get("/", response_model=List[LogRow])
def all_logs(focus: Optional[str] = Query(None, description="Filter by focus (upper/lower/full)")):
    """Return logs, newest first. Optional focus filter."""
    rows = get_logs(focus)
    return [LogRow(**r) for r in rows]
