import os
from datetime import date
from kanban_manager import load_data, save_data, add_task, get_board, move_task, filter_overdue, edit_task, delete_task, STATUSES, PRIORITIES

DATA_FILE = os.path.join(os.path.dirname(__file__), "kanban_data.json")


def prompt(msg: str):
    try:
        return input(msg)
    except EOFError:
        return ""


def show_board(data):
    board = get_board(data)
    print("\n=== Kanban Board ===")
    for status in STATUSES:
        print(f"\n-- {status} --")
        tasks = board.get(status, [])
        if not tasks:
            print("  (no tasks)")
            continue
        for t in tasks:
            dl = t.get('deadline') or '-' 
            pr = t.get('priority')
            print(f"  [{t['id']}] {t['title']} (prio: {pr}, dl: {dl})")


def cmd_add(data):
    title = prompt("Title: ").strip()
    if not title:
        print("Title cannot be empty")
        return
    desc = prompt("Description (optional): ").strip()
    deadline = prompt("Deadline YYYY-MM-DD (optional): ").strip()
    if deadline == "":
        deadline = None
    priority = prompt("Priority (low/medium/high) [medium]: ").strip() or "medium"
    try:
        task = add_task(data, title, desc, deadline, priority)
        save_data(DATA_FILE, data)
        print(f"Added task [{task['id']}] {task['title']}")
    except Exception as e:
        print("Error adding task:", e)


def cmd_move(data):
    try:
        tid = int(prompt("Task ID to move: ").strip())
    except Exception:
        print("Invalid id")
        return
    print("Choose status:")
    for i, s in enumerate(STATUSES, 1):
        print(f"  {i}. {s}")
    try:
        choice = int(prompt("Status number: ").strip())
        ns = STATUSES[choice - 1]
    except Exception:
        print("Invalid choice")
        return
    ok = move_task(data, tid, ns)
    if ok:
        save_data(DATA_FILE, data)
        print("Moved")
    else:
        print("Task not found")


def cmd_overdue(data):
    ov = filter_overdue(data, today=date.today())
    if not ov:
        print("No overdue tasks")
        return
    print("Overdue tasks:")
    for t in ov:
        print(f"  [{t['id']}] {t['title']} (dl: {t.get('deadline')}, prio: {t.get('priority')})")


def cmd_edit(data):
    try:
        tid = int(prompt("Task ID to edit: ").strip())
    except Exception:
        print("Invalid id")
        return
    t = next((x for x in data.get('tasks', []) if x['id'] == tid), None)
    if not t:
        print("Task not found")
        return
    print("Leave blank to keep")
    title = prompt(f"Title [{t['title']}]: ").strip() or None
    desc = prompt(f"Description [{t.get('description','')}]: ").strip() or None
    dl = prompt(f"Deadline YYYY-MM-DD [{t.get('deadline') or ''}]: ").strip() or None
    pr = prompt(f"Priority (low/medium/high) [{t.get('priority','medium')}]: ").strip() or None
    try:
        edit_task(data, tid, title=title, description=desc, deadline=dl, priority=pr)
        save_data(DATA_FILE, data)
        print("Updated")
    except Exception as e:
        print("Error updating:", e)


def cmd_delete(data):
    try:
        tid = int(prompt("Task ID to delete: ").strip())
    except Exception:
        print("Invalid id")
        return
    ok = delete_task(data, tid)
    if ok:
        save_data(DATA_FILE, data)
        print("Deleted")
    else:
        print("Task not found")


def main():
    data = load_data(DATA_FILE)
    actions = {
        "1": ("Show board", lambda: show_board(data)),
        "2": ("Add task", lambda: cmd_add(data)),
        "3": ("Move task", lambda: cmd_move(data)),
        "4": ("Edit task", lambda: cmd_edit(data)),
        "5": ("Delete task", lambda: cmd_delete(data)),
        "6": ("Show overdue", lambda: cmd_overdue(data)),
        "q": ("Quit", None),
    }
    while True:
        print("\nKanban — choose:")
        for k, v in actions.items():
            print(f"  {k}. {v[0]}")
        choice = prompt("> ").strip()
        if choice == "q":
            break
        act = actions.get(choice)
        if not act:
            print("Invalid choice")
            continue
        try:
            act[1]()
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
