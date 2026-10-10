"""SQLite-backed job application tracker.

Schema is intentionally tiny: one table, no migrations. The database file
lives at <project>/data/applications.db and is created on first use.
"""

import os
import sqlite3
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "applications.db")

VALID_STATUSES = {"applied", "interviewing", "offer", "rejected", "withdrawn"}
VALID_ACTIONS = {"add", "update", "list", "get"}


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS applications (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               company TEXT NOT NULL,
               role TEXT NOT NULL,
               date_applied TEXT NOT NULL,
               status TEXT NOT NULL DEFAULT 'applied',
               link TEXT DEFAULT ''
           )"""
    )
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def track_application(action: str, company: str = "", role: str = "",
                      date_applied: str = "", status: str = "applied",
                      link: str = "", application_id: int = 0) -> dict:
    action = (action or "").strip().lower()
    if action not in VALID_ACTIONS:
        return {"ok": False,
                "error": f"Unknown action '{action}'. Use one of: {sorted(VALID_ACTIONS)}."}

    conn = _connect()
    try:
        if action == "add":
            if not company.strip() or not role.strip():
                return {"ok": False, "error": "add requires 'company' and 'role'."}
            status = (status or "applied").strip().lower()
            if status not in VALID_STATUSES:
                return {"ok": False,
                        "error": f"Invalid status '{status}'. Use one of: {sorted(VALID_STATUSES)}."}
            when = date_applied.strip() or date.today().isoformat()
            cur = conn.execute(
                "INSERT INTO applications (company, role, date_applied, status, link)"
                " VALUES (?, ?, ?, ?, ?)",
                (company.strip(), role.strip(), when, status, link.strip()),
            )
            conn.commit()
            app_id = cur.lastrowid
            return {"ok": True, "application": _row_to_dict(
                conn.execute("SELECT * FROM applications WHERE id = ?",
                             (app_id,)).fetchone())}

        if action == "update":
            if not application_id:
                return {"ok": False, "error": "update requires 'application_id'."}
            status = (status or "").strip().lower()
            if status not in VALID_STATUSES:
                return {"ok": False,
                        "error": f"Invalid status '{status}'. Use one of: {sorted(VALID_STATUSES)}."}
            cur = conn.execute("UPDATE applications SET status = ? WHERE id = ?",
                               (status, application_id))
            conn.commit()
            if cur.rowcount == 0:
                return {"ok": False,
                        "error": f"No application with id {application_id}."}
            return {"ok": True, "application": _row_to_dict(
                conn.execute("SELECT * FROM applications WHERE id = ?",
                             (application_id,)).fetchone())}

        if action == "get":
            if not application_id:
                return {"ok": False, "error": "get requires 'application_id'."}
            row = conn.execute("SELECT * FROM applications WHERE id = ?",
                               (application_id,)).fetchone()
            if row is None:
                return {"ok": False,
                        "error": f"No application with id {application_id}."}
            return {"ok": True, "application": _row_to_dict(row)}

        # action == "list"
        query = "SELECT * FROM applications WHERE 1=1"
        params: list = []
        status = (status or "").strip().lower()
        if status:
            if status not in VALID_STATUSES:
                return {"ok": False,
                        "error": f"Invalid status filter '{status}'. Use one of: {sorted(VALID_STATUSES)}."}
            query += " AND status = ?"
            params.append(status)
        if company.strip():
            query += " AND company LIKE ?"
            params.append(f"%{company.strip()}%")
        query += " ORDER BY date_applied DESC, id DESC"
        rows = conn.execute(query, params).fetchall()
        return {"ok": True, "count": len(rows),
                "applications": [_row_to_dict(r) for r in rows]}
    finally:
        conn.close()
