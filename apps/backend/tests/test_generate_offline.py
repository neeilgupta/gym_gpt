import os
import json
import pytest
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
import sys
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from main import app
from models.plans import GeneratePlanResponse


def _base_payload():
    return {
        "goal": "hypertrophy",
        "experience": "intermediate",
        "days_per_week": 4,
        "session_minutes": 60,
        "equipment": "full_gym",
        "soreness_notes": "no soreness",
        "constraints": "",
    }


def test_generate_offline_no_api_key_returns_200():
    client = TestClient(app)

    api_key = os.environ.pop("OPENAI_API_KEY", None)
    narration = os.environ.pop("LLM_NARRATION_ENABLED", None)

    try:
        payload = _base_payload()
        r = client.post("/plans/generate", json=payload)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    finally:
        if api_key is not None:
            os.environ["OPENAI_API_KEY"] = api_key
        if narration is not None:
            os.environ["LLM_NARRATION_ENABLED"] = narration


def test_generate_offline_deterministic():
    client = TestClient(app)

    api_key = os.environ.pop("OPENAI_API_KEY", None)
    narration = os.environ.pop("LLM_NARRATION_ENABLED", None)

    try:
        payload = _base_payload()

        r1 = client.post("/plans/generate", json=payload)
        assert r1.status_code == 200, f"Run 1 failed: {r1.text}"

        r2 = client.post("/plans/generate", json=payload)
        assert r2.status_code == 200, f"Run 2 failed: {r2.text}"

        out1 = r1.json()["output"]
        out2 = r2.json()["output"]

        # strip timestamps/id fields that change between runs
        def _strip_volatile(o):
            if isinstance(o, dict):
                o.pop("plan_id", None)
                o.pop("version", None)
                o.pop("input", None)
                o.pop("estimated_minutes_total", None)
                o.pop("estimated_minutes_note", None)
                for v in o.values():
                    _strip_volatile(v)
            elif isinstance(o, list):
                for item in o:
                    _strip_volatile(item)

        _strip_volatile(out1)
        _strip_volatile(out2)

        assert out1 == out2, "Offline generation is not deterministic"
    finally:
        if api_key is not None:
            os.environ["OPENAI_API_KEY"] = api_key
        if narration is not None:
            os.environ["LLM_NARRATION_ENABLED"] = narration


def test_generate_offline_produces_exercises():
    client = TestClient(app)

    api_key = os.environ.pop("OPENAI_API_KEY", None)
    narration = os.environ.pop("LLM_NARRATION_ENABLED", None)

    try:
        payload = _base_payload()
        r = client.post("/plans/generate", json=payload)
        assert r.status_code == 200, r.text

        data = r.json()
        output = data["output"]
        assert "weekly_split" in output, "Missing weekly_split in output"

        has_exercises = False
        for day in output["weekly_split"]:
            if day.get("main") or day.get("accessories"):
                has_exercises = True
                break

        assert has_exercises, "Output has no exercises (apply_rules_v1 did not run)"
    finally:
        if api_key is not None:
            os.environ["OPENAI_API_KEY"] = api_key
        if narration is not None:
            os.environ["LLM_NARRATION_ENABLED"] = narration


def test_generate_offline_schema_valid():
    client = TestClient(app)

    api_key = os.environ.pop("OPENAI_API_KEY", None)
    narration = os.environ.pop("LLM_NARRATION_ENABLED", None)

    try:
        payload = _base_payload()
        r = client.post("/plans/generate", json=payload)
        assert r.status_code == 200, r.text

        data = r.json()
        output = data["output"]

        plan = GeneratePlanResponse(**output)
        assert plan.title
        assert plan.summary
        assert len(plan.weekly_split) > 0
        for day in plan.weekly_split:
            assert day.day
    finally:
        if api_key is not None:
            os.environ["OPENAI_API_KEY"] = api_key
        if narration is not None:
            os.environ["LLM_NARRATION_ENABLED"] = narration
