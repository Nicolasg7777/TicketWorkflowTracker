"""
TicketWorkflowTracker

Why a CLI:
- It forces clear data modeling (fields, status, timestamps).
- It makes exporting status reports predictable.
- It's easy to demo quickly in an interview.
"""

import argparse
import sqlite3
from datetime import date
from pathlib import Path

from tabulate import tabulate

DB = Path("out") / "tickets.db"


def connect() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB)


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
          ticket_id INTEGER PRIMARY KEY,
          title TEXT NOT NULL,
          requester TEXT NOT NULL,
          owner TEXT,
          priority TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def seed(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM tickets")
    rows = [
        ("Fix reporting bug", "Ops", "Nicolas", "P1", "New", "2026-01-05"),
        ("Add export format", "Sales", "Nicolas", "P2", "Triaged", "2026-01-10"),
        ("Investigate anomaly", "QA", "Nicolas", "P2", "In Progress", "2026-01-15"),
    ]
    conn.executemany(
        "INSERT INTO tickets (title, requester, owner, priority, status, created_at) VALUES (?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def list_all(conn: sqlite3.Connection) -> None:
    cur = conn.execute(
        "SELECT ticket_id, title, owner, priority, status, created_at FROM tickets ORDER BY priority, ticket_id"
    )
    rows = cur.fetchall()
    print(tabulate(rows, headers=["id", "title", "owner", "priority", "status", "created_at"]))


def export_weekly(conn: sqlite3.Connection) -> None:
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)

    rows = conn.execute(
        "SELECT ticket_id, title, owner, priority, status, created_at FROM tickets ORDER BY priority, ticket_id"
    ).fetchall()

    # Compute aging in Python so the logic is explicit (easy to explain).
    enriched = []
    for tid, title, owner, priority, status, created_at in rows:
        y, m, d = map(int, created_at.split("-"))
        days_open = (date.today() - date(y, m, d)).days
        enriched.append((tid, title, owner, priority, status, created_at, days_open))

    csv_path = out_dir / "weekly_status.csv"
    csv_path.write_text("ticket_id,title,owner,priority,status,created_at,days_open\n", encoding="utf-8")
    with csv_path.open("a", encoding="utf-8") as f:
        for row in enriched:
            f.write(",".join(str(x) for x in row) + "\n")

    print(f"Wrote {csv_path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["seed", "list", "export"])
    args = ap.parse_args()

    with connect() as conn:
        ensure_schema(conn)
        if args.cmd == "seed":
            seed(conn)
        elif args.cmd == "list":
            list_all(conn)
        elif args.cmd == "export":
            export_weekly(conn)


if __name__ == "__main__":
    main()

