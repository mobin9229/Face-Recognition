import tkinter as tk
from tkinter import messagebox
from task_data import load_tasks, save_tasks
from notification import start_notifier   # <-- renamed file to notification.py

class TaskSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler")

        # In-memory source of truth
        self.tasks = load_tasks()

        self.listbox = tk.Listbox(root, width=80, height=20, font=("Arial", 18))
        self.listbox.pack(pady=10)

        self.load_tasks_to_listbox()

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        add_btn = tk.Button(
            btn_frame, text="Add Task", font=("Arial", 14),
            width=14, height=2, command=self.open_add_task_window
        )
        add_btn.grid(row=0, column=0, padx=5)

        edit_btn = tk.Button(
            btn_frame, text="Edit Task", font=("Arial", 14),
            width=14, height=2, command=self.edit_task
        )
        edit_btn.grid(row=0, column=1, padx=5)

        delete_btn = tk.Button(
            btn_frame, text="Delete Task", font=("Arial", 14),
            width=14, height=2, command=self.delete_task
        )
        delete_btn.grid(row=0, column=2, padx=5)

        # Start the notifier and give it live access to self.tasks
        start_notifier(self.root, get_tasks=lambda: self.tasks)

    def load_tasks_to_listbox(self):
        self.listbox.delete(0, tk.END)
        # Optional: sort by time if you like (keeps UI tidy)
        def _key(t): return t.get("time", "")
        for task in sorted(self.tasks, key=_key):
            self.listbox.insert(tk.END, f"{task.get('time','--:--')} - {task.get('task','')}")

    def open_add_task_window(self):
        self.open_task_window()

    def open_task_window(self, task_index=None):
        def save():
            time_val = time_entry.get().strip()
            task_val = task_entry.get().strip()
            if not time_val or not task_val:
                messagebox.showerror("Error", "Please enter time and task description.")
                return
            # very light validation: HH:MM
            if len(time_val) != 5 or time_val[2] != ":" or not time_val.replace(":", "").isdigit():
                messagebox.showerror("Error", "Time must be in HH:MM format (24-hour).")
                return

            if task_index is None:
                self.tasks.append({"time": time_val, "task": task_val})
            else:
                self.tasks[task_index] = {"time": time_val, "task": task_val}

            save_tasks(self.tasks)
            self.load_tasks_to_listbox()
            win.destroy()

        win = tk.Toplevel(self.root)
        win.title("Add Task" if task_index is None else "Edit Task")

        tk.Label(win, width=40, text="Time (HH:MM):").pack(pady=(10, 0))
        time_entry = tk.Entry(win)
        time_entry.pack(pady=5)

        tk.Label(win, text="Task Description:").pack(pady=(10, 0))
        task_entry = tk.Entry(win, width=40)
        task_entry.pack(pady=5)

        if task_index is not None:
            time_entry.insert(0, self.tasks[task_index].get('time', ''))
            task_entry.insert(0, self.tasks[task_index].get('task', ''))

        tk.Button(win, text="Save", font=("Arial", 12), command=save).pack(pady=10)

    def edit_task(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to edit.")
            return
        index = selected[0]
        # Map selection back to the right task (because we sorted for display)
        # Rebuild sorted index mapping:
        sorted_tasks = sorted(self.tasks, key=lambda t: t.get("time", ""))
        selected_task = sorted_tasks[index]
        # find its original index to edit in-place
        original_idx = self.tasks.index(selected_task)
        self.open_task_window(task_index=original_idx)

    def delete_task(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        index = selected[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?")
        if confirm:
            # Keep delete consistent with sorted display:
            sorted_tasks = sorted(self.tasks, key=lambda t: t.get("time", ""))
            selected_task = sorted_tasks[index]
            original_idx = self.tasks.index(selected_task)

            self.tasks.pop(original_idx)
            save_tasks(self.tasks)
            self.load_tasks_to_listbox()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskSchedulerApp(root)
    root.mainloop()
