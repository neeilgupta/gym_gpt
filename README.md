# gym_gpt

## Logs API

### POST /logs
Add a new set entry:
```json
{
  "name": "Bench Press",
  "reps": 8,
  "weight_kg": 70,
  "rir": 2,
  "focus": "upper"  // optional
}
```

### GET /logs
Returns all stored logs (in-memory for now).

## Next Steps
Future versions will store logs in SQLite and automatically feed them into progressive overload logic.