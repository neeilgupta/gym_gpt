# gym_gpt

## Logs API

### Persistent Logging

Logs are stored in `data/gymgpt.db` using SQLite for persistence between server restarts.

### POST /logs
Add a new set entry:
```json
{
  "name": "Bench Press",
  "reps": 8,
  "weight_kg": 70,
  "rir": 2,
  "focus": "upper"  // optional: upper/lower/full
}
```
Response:
```json
{
  "added": {
    "id": 1,
    "name": "Bench Press",
    "reps": 8,
    "weight_kg": 70,
    "rir": 2,
    "focus": "upper",
    "timestamp": "2025-11-07T23:01:54.749924"
  }
}
```

### GET /logs
Returns all stored logs.

Optional query parameter: `?focus=upper` to filter logs by focus (upper/lower/full).

## Backend Quickstart

### 1. Setup

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
