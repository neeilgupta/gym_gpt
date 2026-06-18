import os
import sys
import copy
import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from models.plans import GeneratePlanRequest, GeneratePlanResponse, DayPlan, ExerciseItem
from routes.rules.engine import apply_rules_v1


def _make_plan(days_per_week=4, session_minutes=60, equipment="full_gym",
               focus_muscles=None, constraints=""):
    base = GeneratePlanResponse(
        title="Stub",
        summary="",
        weekly_split=[
            DayPlan(
                day="Day 1",
                focus="",
                warmup=[],
                main=[
                    ExerciseItem(name="Bench Press", sets=3, reps="8-12", rest_seconds=180)
                ],
                accessories=[],
            )
        ],
    )
    req = GeneratePlanRequest(
        days_per_week=days_per_week,
        session_minutes=session_minutes,
        equipment=equipment,
        focus_muscles=focus_muscles,
        constraints=constraints,
    )
    return base, req


IDEMPOTENT_CASES = [
    _make_plan(days_per_week=3, session_minutes=45, equipment="full_gym", focus_muscles=["chest"]),
    _make_plan(days_per_week=4, session_minutes=60, equipment="full_gym"),
    _make_plan(days_per_week=5, session_minutes=60, equipment="dumbbells", focus_muscles=["arms"]),
    _make_plan(days_per_week=6, session_minutes=75, equipment="full_gym", focus_muscles=["legs"]),
    _make_plan(days_per_week=3, session_minutes=30, equipment="bodyweight"),
    _make_plan(days_per_week=4, session_minutes=45, equipment="dumbbells", constraints="no barbells"),
    _make_plan(days_per_week=5, session_minutes=60, equipment="full_gym", focus_muscles=["back"]),
    _make_plan(days_per_week=4, session_minutes=75, equipment="full_gym", focus_muscles=["shoulders"]),
]


@pytest.mark.parametrize("base_plan,req", IDEMPOTENT_CASES)
def test_apply_rules_v1_idempotent(base_plan, req):
    run1 = apply_rules_v1(plan=base_plan, req=req)
    run2 = apply_rules_v1(plan=copy.deepcopy(run1), req=req)
    assert run1.model_dump_json() == run2.model_dump_json(), \
        "apply_rules_v1 is not idempotent for this input"
