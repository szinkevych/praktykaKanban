Kanban CLI

Simple console Kanban manager (Todo / In Progress / Done) with JSON persistence.

Run

1. Start the app:

```bash
python kanban_cli.py
```

2. Tests (requires `pytest`):

```bash
pip install pytest
pytest -q
```

Notes

- Data file `kanban_data.json` is created next to the scripts.
- Deadlines use `YYYY-MM-DD` format.
- Priorities: `low`, `medium`, `high`.
