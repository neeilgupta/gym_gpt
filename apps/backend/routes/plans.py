from __future__ import annotations

import json
import os
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, conint, ConfigDict

from openai import OpenAI

router = APIRouter(prefix="/plans", tags=["plans"])
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------- Request / Response Schemas ----------

class GeneratePlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goal: Literal["strength", "hypertrophy", "fat_loss", "endurance"] = "hypertrophy"
    experience: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    days_per_week: conint(ge=1, le=6) = 4
    session_minutes: conint(ge=20, le=120) = 60

    soreness_notes: str = Field(default="", description="Free-text soreness/recovery notes.")
    equipment: Literal["full_gym", "dumbbells", "bodyweight"] = "full_gym"
    constraints: Optional[str] = Field(default="", description="Any injuries, preferences, dislikes.")


class ExerciseItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    sets: conint(ge=1, le=10)
    reps: str = Field(description='e.g. "6-8" or "10-12"')
    rpe: Optional[conint(ge=6, le=10)] = None
    rest_seconds: Optional[conint(ge=30, le=300)] = None
    notes: Optional[str] = ""


class DayPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day: str = Field(description='e.g. "Day 1"')
    focus: str = Field(description='e.g. "Upper (push emphasis)"')
    warmup: list[str] = []
    main: list[ExerciseItem]
    accessories: list[ExerciseItem] = []
    finisher: list[str] = []
    cooldown: list[str] = []


class GeneratePlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    summary: str
    weekly_split: list[DayPlan]
    progression_notes: list[str] = []
    safety_notes: list[str] = []


# ---------- Prompting ----------

SYSTEM_PROMPT = """You are GymGPT, a strength & conditioning coach.
Return ONLY valid JSON that matches the provided schema. No markdown. No extra keys.
Be realistic, safe, and adjust for soreness/constraints. Use common exercise names.
If soreness suggests avoiding a pattern, substitute accordingly (e.g., sore elbows -> reduce heavy pressing).
If the user prefers machines, avoid barbell/Smith movements unless explicitly requested."""

def build_user_prompt(req: GeneratePlanRequest) -> str:
    return f"""
Generate a {req.days_per_week}-day workout plan.

User details:
- Goal: {req.goal}
- Experience: {req.experience}
- Days/week: {req.days_per_week}
- Session length: {req.session_minutes} minutes
- Equipment: {req.equipment}
- Soreness notes: {req.soreness_notes}
- Constraints: {req.constraints}

Rules:
- Keep it within {req.session_minutes} minutes per session.
- Include warmup, main lifts, accessories, and brief cooldown.
- Use rep ranges appropriate for goal and experience.
- Prefer compound lifts if equipment allows.
- Provide short progression notes for weeks 1-4.
- Output must validate against the JSON schema exactly.
""".strip()


@router.post("/generate", response_model=GeneratePlanResponse)
def generate_plan(req: GeneratePlanRequest):
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    # Use JSON schema guidance via response_format with strict JSON
    schema = GeneratePlanResponse.model_json_schema()
    schema["additionalProperties"] = False

    def normalize_openai_json_schema(node):
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                props = node["properties"]
                node["additionalProperties"] = False
                node["required"] = list(props.keys())
            for v in node.values():
                normalize_openai_json_schema(v)
        elif isinstance(node, list):
            for item in node:
                normalize_openai_json_schema(item)

    normalize_openai_json_schema(schema)

    


    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(req)},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "GeneratePlanResponse",
                    "schema": schema,
                    "strict": True,
                },
            },
            temperature=0.4,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)  # strict JSON expected
        return GeneratePlanResponse(**data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {e}")
