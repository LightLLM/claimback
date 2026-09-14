"""SQLite demo persistence with compare-and-swap updates across processes."""
import json
import os
import sqlite3
from pathlib import Path
from .domain import initial_state


class Store:
    def __init__(self, path=None):
        self.path = Path(path or os.getenv("CLAIMBACK_DB", "runtime/claimback.db"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, version INTEGER NOT NULL, data TEXT NOT NULL)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def load(self, session):
        with self.connect() as db:
            state = initial_state()
            db.execute("INSERT OR IGNORE INTO sessions VALUES (?, 0, ?)", (session, json.dumps(state)))
            row = db.execute("SELECT data FROM sessions WHERE id = ?", (session,)).fetchone()
            return json.loads(row[0])

    def save(self, session, state):
        version = state["revision"]
        state["revision"] += 1
        with self.connect() as db:
            result = db.execute("UPDATE sessions SET data=?, version=? WHERE id=? AND version=?", (json.dumps(state), state["revision"], session, version))
            if result.rowcount != 1:
                raise ValueError("Case changed in another tab. Refresh before retrying.")

