from fastapi import APIRouter, Body
from services import planner, nlp

router = APIRouter()

@router.post("/workout")
def create_workout(payload: dict = Body(...)):
    focus = payload.get("focus", "upper")
    last = payload.get("last_log", {})  # {"Bench Press":[{"reps":6,"weight_kg":80,"rir":2}]}
    soreness_text = payload.get("soreness_text", "")
    soreness = nlp.parse_soreness(soreness_text) if soreness_text else None
    equipment = payload.get("equipment", "gym")
    plan = planner.build_workout_plan(focus, last, soreness, equipment = equipment)
    return {"plan": plan}

@router.post("/week")
def create_weekly_plan(payload: dict = Body(...)):
    days = int(payload.get("days_per_week", 4))
    last = payload.get("last_log", {})
    soreness_text = payload.get("soreness_text", "")
    soreness = nlp.parse_soreness(soreness_text) if soreness_text else None
    equipment = payload.get("equipment", "gym")
    weekly_plan = planner.build_week_plan(days, last, soreness, equipment=equipment)
    return {"weekly_plan": weekly_plan}