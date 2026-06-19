Kanban CLI


Simple Kanban manager with GUI (Tkinter) and JSON persistence.

Run

1. Start the app (opens a window):

```bash
python kanban_cli.py
```

2. If you prefer the console UI, run:

```bash
python kanban_cli.py --cli
```

3. Tests (requires `pytest`):

```bash
pip install pytest
pytest -q
```

Notes

- Data file `kanban_data.json` is created next to the scripts.
- Deadlines use `YYYY-MM-DD` format.
- Priorities: `low`, `medium`, `high`.
- UI language default is Ukrainian; you can switch to English in the GUI.
