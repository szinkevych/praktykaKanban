import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date
from kanban_manager import load_data, save_data, add_task, get_board, move_task, edit_task, delete_task, STATUSES, PRIORITIES

DATA_FILE = os.path.join(os.path.dirname(__file__), "kanban_data.json")

TRANSLATIONS = {
    "en": {
        "title": "Kanban Manager",
        "add": "Add",
        "delete": "Delete",
        "move": "Move",
        "edit": "Edit",
        "overdue": "Overdue",
        "lang": "Language",
    },
    "uk": {
        "title": "Канбан Менеджер",
        "add": "Додати",
        "delete": "Видалити",
        "move": "Перемістити",
        "edit": "Редагувати",
        "overdue": "Прострочені",
        "lang": "Мова",
    }
}


class KanbanGUI:
    def __init__(self, root, lang="uk"):
        self.root = root
        self.lang = lang if lang in TRANSLATIONS else "en"
        self.t = TRANSLATIONS[self.lang]
        root.title(self.t["title"])
        self.data = load_data(DATA_FILE)
        self._build()
        self.refresh()

    def _build(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=tk.BOTH, expand=True)
        self.frames = {}
        for i, status in enumerate(STATUSES):
            f = ttk.LabelFrame(top, text=status, padding=8)
            f.grid(row=0, column=i, padx=5, sticky="nsew")
            top.columnconfigure(i, weight=1)
            lb = tk.Listbox(f, height=15)
            lb.pack(fill=tk.BOTH, expand=True)
            self.frames[status] = lb

        ctrl = ttk.Frame(self.root, padding=8)
        ctrl.pack(fill=tk.X)
        ttk.Button(ctrl, text=self.t["add"], command=self.add).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text=self.t["edit"], command=self.edit).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text=self.t["move"], command=self.move).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text=self.t["delete"], command=self.delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text=self.t["overdue"], command=self.show_overdue).pack(side=tk.LEFT, padx=4)

        lang_menu = ttk.Combobox(ctrl, values=["en", "uk"], width=4)
        lang_menu.set(self.lang)
        lang_menu.bind("<<ComboboxSelected>>", self.change_lang)
        ttk.Label(ctrl, text=self.t["lang"] + ":").pack(side=tk.RIGHT)
        lang_menu.pack(side=tk.RIGHT, padx=4)

    def refresh(self):
        self.data = load_data(DATA_FILE)
        board = get_board(self.data)
        for status, lb in self.frames.items():
            lb.delete(0, tk.END)
            for t in board.get(status, []):
                dl = t.get("deadline") or "-"
                lb.insert(tk.END, f"[{t['id']}] {t['title']} (prio:{t.get('priority')}, dl:{dl})")

    def _get_selected_task(self):
        for status, lb in self.frames.items():
            sel = lb.curselection()
            if sel:
                idx = sel[0]
                text = lb.get(idx)
                # parse id
                try:
                    tid = int(text.split(']')[0].lstrip('['))
                    return tid
                except Exception:
                    return None
        return None

    def add(self):
        title = simpledialog.askstring(self.t["add"], "Title:")
        if not title:
            return
        desc = simpledialog.askstring(self.t["add"], "Description:") or ""
        dl = simpledialog.askstring(self.t["add"], "Deadline YYYY-MM-DD (optional):") or None
        pr = simpledialog.askstring(self.t["add"], f"Priority ({'/'.join(PRIORITIES)}) [medium]:") or "medium"
        try:
            add_task(self.data, title, desc, dl, pr)
            save_data(DATA_FILE, self.data)
            self.refresh()
        except Exception as e:
            messagebox.showerror(self.t["add"], str(e))

    def edit(self):
        tid = self._get_selected_task()
        if not tid:
            return
        t = next((x for x in self.data.get('tasks', []) if x['id'] == tid), None)
        if not t:
            return
        title = simpledialog.askstring(self.t["edit"], "Title:", initialvalue=t.get('title')) or None
        desc = simpledialog.askstring(self.t["edit"], "Description:", initialvalue=t.get('description','')) or None
        dl = simpledialog.askstring(self.t["edit"], "Deadline YYYY-MM-DD:", initialvalue=t.get('deadline') or '') or None
        pr = simpledialog.askstring(self.t["edit"], f"Priority ({'/'.join(PRIORITIES)}):", initialvalue=t.get('priority','medium')) or None
        try:
            edit_task(self.data, tid, title=title, description=desc, deadline=dl, priority=pr)
            save_data(DATA_FILE, self.data)
            self.refresh()
        except Exception as e:
            messagebox.showerror(self.t["edit"], str(e))

    def move(self):
        tid = self._get_selected_task()
        if not tid:
            return
        choice = simpledialog.askstring(self.t["move"], f"Target status ({'/'.join(STATUSES)}):")
        if not choice or choice not in STATUSES:
            messagebox.showinfo(self.t["move"], "Invalid status")
            return
        try:
            move_task(self.data, tid, choice)
            save_data(DATA_FILE, self.data)
            self.refresh()
        except Exception as e:
            messagebox.showerror(self.t["move"], str(e))

    def delete(self):
        tid = self._get_selected_task()
        if not tid:
            return
        if not messagebox.askyesno(self.t["delete"], "Confirm delete?"):
            return
        delete_task(self.data, tid)
        save_data(DATA_FILE, self.data)
        self.refresh()

    def show_overdue(self):
        from kanban_manager import filter_overdue
        ov = filter_overdue(self.data, today=date.today())
        if not ov:
            messagebox.showinfo(self.t["overdue"], "No overdue tasks")
            return
        txt = "\n".join([f"[{t['id']}] {t['title']} (dl:{t.get('deadline')})" for t in ov])
        messagebox.showinfo(self.t["overdue"], txt)

    def change_lang(self, ev=None):
        widget = ev.widget if ev else None
        if widget:
            val = widget.get()
            if val in TRANSLATIONS:
                self.lang = val
                self.t = TRANSLATIONS[self.lang]
                self.root.title(self.t["title"])


def run_gui():
    root = tk.Tk()
    app = KanbanGUI(root, lang="uk")
    root.mainloop()


if __name__ == "__main__":
    run_gui()
