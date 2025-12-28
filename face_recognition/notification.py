import time
import threading
import pyttsx3
import tkinter as tk
from tkinter import messagebox

# How often to poll for due tasks (seconds).
# 5 seconds avoids missing a minute flip and keeps CPU low.
POLL_SECONDS = 5

# Set up a single TTS engine used by a tiny worker thread per utterance.
_engine = pyttsx3.init()

def _speak_async(text: str):
    def _worker():
        try:
            _engine.say(text)
            _engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=_worker, daemon=True).start()

class Notifier:
    def __init__(self, root: tk.Tk, get_tasks):
        """
        get_tasks: zero-arg callable returning current list[{'time': 'HH:MM', 'task': '...'}]
        """
        self.root = root
        self.get_tasks = get_tasks

        # Track which (minute, text) we've already alerted on.
        # Keys look like "YYYYMMDD-HH:MM|Task text"
        self._already_notified = set()

        # Start polling loop
        self._tick()

    def _make_key(self, hhmm: str, text: str):
        today = time.strftime("%Y%m%d")
        return f"{today}-{hhmm}|{text.strip()}"

    def _tick(self):
        try:
            now_hhmm = time.strftime("%H:%M")
            tasks = self.get_tasks() or []

            # Build the set of keys that exist RIGHT NOW (for GC below)
            current_keys = set()
            for t in tasks:
                t_time = (t.get("time") or "").strip()
                t_text = (t.get("task") or "").strip()
                if not t_time or not t_text:
                    continue
                key = self._make_key(t_time, t_text)
                current_keys.add(key)

                # If due this minute and we haven't notified yet, show it
                if t_time == now_hhmm and key not in self._already_notified:
                    self._show_notification(t_text)
                    self._already_notified.add(key)

            # Garbage-collect: if a task was edited/deleted, drop old keys
            self._already_notified.intersection_update(current_keys)

            # Midnight rollover: if date changed, clear history
            today_prefix = time.strftime("%Y%m%d-")
            self._already_notified = {k for k in self._already_notified if k.startswith(today_prefix)}

        finally:
            # Schedule next poll
            self.root.after(POLL_SECONDS * 1000, self._tick)

    def _show_notification(self, task_text: str):
        # First, speak once immediately (async so UI won't freeze)
        _speak_async(f"Time for: {task_text}")

        # Then open a small window with repeating speech every 10 seconds until 'Stop'
        window = tk.Toplevel(self.root)
        window.title("Task Reminder")
        window.geometry("320x160")
        window.attributes("-topmost", True)

        label = tk.Label(window, text=f"It's time for:\n{task_text}", font=("Arial", 14), justify="center")
        label.pack(pady=20)

        repeat_state = {"on": True}  # use dict for mutability in closures

        def stop():
            repeat_state["on"] = False
            window.destroy()

        def repeat_announcement():
            if repeat_state["on"]:
                _speak_async(f"Time for: {task_text}")
                window.after(10000, repeat_announcement)  # repeat every 10s

        stop_button = tk.Button(window, text="Stop", command=stop, width=10)
        stop_button.pack(pady=10)

        window.after(10000, repeat_announcement)

def start_notifier(root, get_tasks):
    """
    Starts the notifier that polls the live tasks without reloading from disk.
    """
    Notifier(root, get_tasks)
