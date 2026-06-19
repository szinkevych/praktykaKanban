from dataclasses import dataclass, asdict
from datetime import datetime, date
import json
from typing import List, Dict, Optional

STATUSES = ["Todo", "In Progress", "Done"]
PRIORITIES = ["low", "medium", "high"]


def _today_date():
    return date.today()


def load_data(path: str) -> Dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"tasks": [], "next_id": 1}
    except json.JSONDecodeError:
        return {"tasks": [], "next_id": 1}


def save_data(path: str, data: Dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _parse_date(s: Optional[str]) -> Optional[str]:
    if s is None or s.strip() == "":
        return None
    try:
        d = datetime.strptime(s.strip(), "%Y-%m-%d").date()
        return d.isoformat()
    except ValueError:
        raise ValueError("Invalid date format, use YYYY-MM-DD")


def add_task(data: Dict, title: str, description: str = "", deadline: Optional[str] = None, priority: str = "medium") -> Dict:
    if priority not in PRIORITIES:
        raise ValueError(f"priority must be one of {PRIORITIES}")
    deadline_iso = _parse_date(deadline)
    task = {
        "id": data.get("next_id", 1),
        "title": title,
        "description": description,
        "status": "Todo",
        "deadline": deadline_iso,
        "priority": priority,
        "created": datetime.utcnow().isoformat(),
    }
    data.setdefault("tasks", []).append(task)
    data["next_id"] = task["id"] + 1
    return task


def find_task(data: Dict, task_id: int) -> Optional[Dict]:
    for t in data.get("tasks", []):
        if t.get("id") == task_id:
            return t
    return None


def move_task(data: Dict, task_id: int, new_status: str) -> bool:
    if new_status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    t = find_task(data, task_id)
    if not t:
        return False
    t["status"] = new_status
    return True


def edit_task(data: Dict, task_id: int, **fields) -> bool:
    t = find_task(data, task_id)
    if not t:
        return False
    if "deadline" in fields:
        t["deadline"] = _parse_date(fields.get("deadline"))
    if "priority" in fields:
        if fields["priority"] not in PRIORITIES:
            raise ValueError(f"priority must be one of {PRIORITIES}")
        t["priority"] = fields["priority"]
    for k in ("title", "description", "status"):
        if k in fields and fields[k] is not None:
            t[k] = fields[k]
    return True


def delete_task(data: Dict, task_id: int) -> bool:
    tasks = data.get("tasks", [])
    for i, t in enumerate(tasks):
        if t.get("id") == task_id:
            tasks.pop(i)
            return True
    return False


def get_board(data: Dict) -> Dict[str, List[Dict]]:
    board = {s: [] for s in STATUSES}
    for t in data.get("tasks", []):
        board.setdefault(t.get("status", "Todo"), []).append(t)
    # sort by priority then deadline
    def sort_key(task):
        p = PRIORITIES.index(task.get("priority", "medium")) if task.get("priority") in PRIORITIES else 1
        dl = task.get("deadline") or "9999-12-31"
        return (p, dl)

    for s in board:
        board[s].sort(key=sort_key)
    return board


def filter_overdue(data: Dict, today: Optional[date] = None) -> List[Dict]:
    if today is None:
        today = _today_date()
    out = []
    for t in data.get("tasks", []):
        if t.get("status") == "Done":
            continue
        dl = t.get("deadline")
        if not dl:
            continue
        try:
            d = datetime.strptime(dl, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < today:
            out.append(t)
    return out


if __name__ == "__main__":
    print("This module provides core Kanban functions. Use kanban_cli.py to run the app.")
