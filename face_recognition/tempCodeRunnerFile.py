import tkinter as tk
import threading
import pyttsx3
import time
from task_data import load_tasks

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def show_notification_window(task_text):
    def stop():
        nonlocal repeat
        repeat = False
        window.destroy()

    def repeat_announcement():
        if repeat:
            speak(f"Time for: {task_text}")
            window.after(10000, repeat_announcement)  # تکرار هر 10 ثانیه

    repeat = True
    speak(f"Time for: {task_text}")

    window = tk.Toplevel()
    window.title("Task Reminder")
    window.geometry("300x150")

    label = tk.Label(window, text=f"It's time for:\n{task_text}", font=("Arial", 14))
    label.pack(pady=20)

    stop_button = tk.Button(window, text="Stop", command=stop)
    stop_button.pack(pady=10)

    window.after(10000, repeat_announcement)

def run_scheduler(root):
    def check_tasks():
        tasks = load_tasks()
        now = time.strftime("%H:%M")
        for t in tasks:
            if t["time"] == now:
                # فراخوانی اعلان در thread اصلی (رابط کاربری)
                root.after(0, show_notification_window, t["task"])
        root.after(60000, check_tasks)  # چک کردن هر 60 ثانیه

    check_tasks()

def start_notifier(root):
    threading.Thread(target=run_scheduler, args=(root,), daemon=True).start()
