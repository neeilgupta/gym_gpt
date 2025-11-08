from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class ExerciseLog(BaseModel):
    name: str
    reps: int
    weight_kg: float
    rir: int
    timestamp: datetime = None
    focus: str = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bench Press",
                "reps": 8,
                "weight_kg": 70,
                "rir": 2,
                "focus": "upper"
            }
        }

LOGS: List[ExerciseLog] = []

@router.get("/")
def get_logs():
    """Retrieve all stored exercise logs."""
    return LOGS

from fastapi import APIRouter, Query
from pydantic import BaseModel
from ..services.db import add_log, get_logs, init_db
from typing import Optional

router = APIRouter()
init_db()

class Log(BaseModel):
    name: str
    reps: int
    weight_kg: float
    rir: int
    focus: Optional[str] = None

class LogResponse(Log):
    id: int
    timestamp: str

@router.post("/", response_model=dict)
def add(log: Log):
    added = add_log(log.name, log.reps, log.weight_kg, log.rir, log.focus)
    return {"added": added}

@router.get("/")
def all_logs(focus: Optional[str] = Query(None, description="Filter logs by focus (upper/lower/full)")):
    return get_logs(focus)
