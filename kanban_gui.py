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
        "view": "View",
        "delete": "Delete",
        "move": "Move",
        "edit": "Edit",
        "overdue": "Overdue",
    },
    "uk": {
        "title": "Канбан Менеджер",
        "add": "Додати",
        "view": "Переглянути",
        "delete": "Видалити",
        "move": "Перемістити",
        "edit": "Редагувати",
        "overdue": "Прострочені",
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
        self.style = ttk.Style(self.root)
        self.style.configure("Treeview", rowheight=26, font=(None, 10))
        self.style.configure("Header.TLabel", font=(None, 11, "bold"))

        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=tk.BOTH, expand=True)
        self.trees = {}

        for i, status in enumerate(STATUSES):
            f = ttk.LabelFrame(top, text=status, padding=8)
            f.grid(row=0, column=i, padx=6, sticky="nsew")
            top.columnconfigure(i, weight=1)
            cols = ("id", "title", "priority", "deadline")
            tv = ttk.Treeview(f, columns=cols, show="headings", selectmode="browse")
            tv.heading("id", text="#")
            tv.heading("title", text="Title")
            tv.heading("priority", text="Priority")
            tv.heading("deadline", text="Deadline")
            tv.column("id", width=40, anchor="center")
            tv.column("title", width=200)
            tv.column("priority", width=80, anchor="center")
            tv.column("deadline", width=100, anchor="center")
            tv.pack(fill=tk.BOTH, expand=True)
            # tags for priority coloring
            tv.tag_configure("high", background="#ffe6e6")
            tv.tag_configure("medium", background="#fff4e6")
            tv.tag_configure("low", background="#e8f8e8")
            # single-click toggles selection (select/deselect)
            tv.bind("<Button-1>", lambda e, tree=tv: self.on_tree_click(e, tree))
            self.trees[status] = tv

        ctrl = ttk.Frame(self.root, padding=8)
        ctrl.pack(fill=tk.X)
        ttk.Button(ctrl, text=self.t["add"], command=self.add).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctrl, text=self.t["view"], command=self.view).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctrl, text=self.t["edit"], command=self.edit).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctrl, text=self.t["move"], command=self.move).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctrl, text=self.t["delete"], command=self.delete).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctrl, text=self.t["overdue"], command=self.show_overdue).pack(side=tk.LEFT, padx=6)

    def refresh(self):
        self.data = load_data(DATA_FILE)
        board = get_board(self.data)
        for status, tv in self.trees.items():
            for row in tv.get_children():
                tv.delete(row)
            for t in board.get(status, []):
                dl = t.get("deadline") or "-"
                pr = t.get("priority") or "medium"
                tv.insert("", tk.END, values=(t["id"], t["title"], pr, dl), tags=(pr,))

    def _get_selected_task(self):
        for status, tv in self.trees.items():
            sel = tv.selection()
            if sel:
                item = tv.item(sel[0])
                try:
                    tid = int(item["values"][0])
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
            messagebox.showinfo(self.t["edit"], "Select a task first")
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

    def view(self):
        tid = self._get_selected_task()
        if not tid:
            messagebox.showinfo(self.t.get("view", "View"), "Select a task first")
            return
        t = next((x for x in self.data.get('tasks', []) if x['id'] == tid), None)
        if not t:
            return
        win = tk.Toplevel(self.root)
        win.title(f"{self.t.get('view','View')} - [{t['id']}] {t.get('title')}")
        win.transient(self.root)
        win.grab_set()
        frm = ttk.Frame(win, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Title:", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(frm, text=t.get('title','')).grid(row=0, column=1, sticky="w")
        ttk.Label(frm, text="Description:", style="Header.TLabel").grid(row=1, column=0, sticky="nw")
        txt = tk.Text(frm, width=50, height=6, wrap="word")
        txt.insert("1.0", t.get('description',''))
        txt.config(state=tk.DISABLED)
        txt.grid(row=1, column=1, sticky="we", pady=4)
        ttk.Label(frm, text="Status:", style="Header.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(frm, text=t.get('status','')).grid(row=2, column=1, sticky="w")
        ttk.Label(frm, text="Priority:", style="Header.TLabel").grid(row=3, column=0, sticky="w")
        ttk.Label(frm, text=t.get('priority','')).grid(row=3, column=1, sticky="w")
        ttk.Label(frm, text="Deadline:", style="Header.TLabel").grid(row=4, column=0, sticky="w")
        ttk.Label(frm, text=t.get('deadline','-')).grid(row=4, column=1, sticky="w")
        ttk.Label(frm, text="Created:", style="Header.TLabel").grid(row=5, column=0, sticky="w")
        ttk.Label(frm, text=t.get('created','-')).grid(row=5, column=1, sticky="w")
        btn = ttk.Button(frm, text="Close", command=win.destroy)
        btn.grid(row=6, column=0, columnspan=2, pady=8)
        for c in range(2):
            frm.columnconfigure(c, weight=1)

    def on_tree_click(self, event, tree):
        # Toggle selection on single click: click selected -> deselect, click another -> select it
        item = tree.identify_row(event.y)
        if not item:
            # click outside any row -> clear all selections
            for tv in self.trees.values():
                for s in tv.selection():
                    tv.selection_remove(s)
            return
        sel = tree.selection()
        if item in sel:
            tree.selection_remove(item)
            return
        # select item and clear other trees' selections
        for tv in self.trees.values():
            if tv is not tree:
                for s in tv.selection():
                    tv.selection_remove(s)
        tree.selection_set(item)

    def move(self):
        tid = self._get_selected_task()
        if not tid:
            messagebox.showinfo(self.t["move"], "Select a task first")
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
            messagebox.showinfo(self.t["delete"], "Select a task first")
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


def run_gui():
    root = tk.Tk()
    root.minsize(800, 400)
    app = KanbanGUI(root, lang="uk")
    root.mainloop()


if __name__ == "__main__":
    run_gui()
