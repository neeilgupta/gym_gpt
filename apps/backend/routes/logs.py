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

@router.post("/")
def add_log(log: ExerciseLog):
    """Add a new exercise log entry.
    
    If timestamp is not provided, current time will be used.
    """
    if not log.timestamp:
        log.timestamp = datetime.now()
    LOGS.append(log)
    return {"added": log}
