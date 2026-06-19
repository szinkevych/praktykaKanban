import json
from datetime import date, timedelta
from kanban_manager import load_data, save_data, add_task, move_task, filter_overdue


def test_add_and_move(tmp_path):
    p = tmp_path / "data.json"
    data = load_data(str(p))
    t = add_task(data, "Test task", "desc", (date.today() + timedelta(days=1)).isoformat(), "high")
    save_data(str(p), data)
    loaded = load_data(str(p))
    assert any(x['id'] == t['id'] for x in loaded['tasks'])
    moved = move_task(loaded, t['id'], "In Progress")
    assert moved
    assert next(x for x in loaded['tasks'] if x['id'] == t['id'])['status'] == "In Progress"


def test_overdue_filter(tmp_path):
    p = tmp_path / "data2.json"
    data = {"tasks": [], "next_id": 1}
    # overdue
    add_task(data, "Old", "", (date.today() - timedelta(days=2)).isoformat(), "low")
    # not overdue
    add_task(data, "Future", "", (date.today() + timedelta(days=2)).isoformat(), "low")
    res = filter_overdue(data, today=date.today())
    assert any(t['title'] == "Old" for t in res)
    assert not any(t['title'] == "Future" for t in res)


def test_persistence(tmp_path):
    p = tmp_path / "data3.json"
    data = {"tasks": [], "next_id": 1}
    add_task(data, "Persist", "", None, "medium")
    save_data(str(p), data)
    loaded = load_data(str(p))
    assert loaded['tasks'][0]['title'] == "Persist"
