# TicketWorkflowTracker

A lightweight backlog / request tracker that mirrors how teams manage intake, prioritization, and weekly status reporting.

## What it does
- Stores requests in SQLite
- Supports a simple status lifecycle
- Computes aging (days open)
- Exports a weekly status report

## Run
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt

python app/main.py seed
python app/main.py list
python app/main.py export
```

