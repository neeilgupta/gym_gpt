import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/gymgpt.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        reps INTEGER,
        weight_kg REAL,
        rir INTEGER,
        focus TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def add_log(name: str, reps: int, weight_kg: float, rir: int, focus: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO logs(name, reps, weight_kg, rir, focus) VALUES (?,?,?,?,?)", 
        (name, reps, weight_kg, rir, focus)
    )
    id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute(
        "SELECT id, name, reps, weight_kg, rir, focus, timestamp FROM logs WHERE id = ?",
        (id,)
    ).fetchone()
    conn.commit()
    conn.close()
    return dict(zip(["id", "name", "reps", "weight_kg", "rir", "focus", "timestamp"], row))

def get_logs(focus: str = None):
    conn = sqlite3.connect(DB_PATH)
    if focus:
        cur = conn.execute(
            "SELECT id, name, reps, weight_kg, rir, focus, timestamp FROM logs WHERE focus = ? ORDER BY id DESC",
            (focus,)
        )
    else:
        cur = conn.execute(
            "SELECT id, name, reps, weight_kg, rir, focus, timestamp FROM logs ORDER BY id DESC"
        )
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "name", "reps", "weight_kg", "rir", "focus", "timestamp"], r)) for r in rows]
