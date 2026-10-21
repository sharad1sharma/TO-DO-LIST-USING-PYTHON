# To-Do List Application Made By :- SHARAD SHARMA
# TASK-1: To-Do List Application USING PYTHON COMPLETED ON 12-06-2026
# BY CodSoft Technologies Pvt. Ltd.

import tkinter as tk
from tkinter import messagebox
import json
import os
import uuid
import webbrowser
import subprocess
import socket
from datetime import datetime

DATA_FILE = "tasks.json"
WEB_URL = "http://127.0.0.1:5000"

# In-memory storage for tasks to synchronize cleanly with tasks.json
tasks_data = []


def is_server_running(host="127.0.0.1", port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.5)
        s.connect((host, port))
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def open_web_frontend():
    """Launch Flask server if not active, and open the web frontend in the default browser."""
    if not is_server_running():
        try:
            # Start app.py as a separate background process
            subprocess.Popen(["python", "app.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start web server: {e}")
            return
    webbrowser.open(WEB_URL)


def render_listbox():
    listbox.delete(0, tk.END)
    for task in tasks_data:
        status_icon = "✓ " if task.get("completed") else "○ "
        category = f"[{task.get('category', 'General')}] " if task.get("category") else ""
        listbox.insert(tk.END, f"{status_icon}{category}{task.get('text', '')}")


def load_tasks():
    global tasks_data
    tasks_data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
                if isinstance(raw_items, list):
                    for item in raw_items:
                        if isinstance(item, str):
                            tasks_data.append({
                                "id": str(uuid.uuid4())[:8],
                                "text": item.strip(),
                                "completed": False,
                                "priority": "medium",
                                "category": "General",
                                "created_at": datetime.now().isoformat()
                            })
                        elif isinstance(item, dict):
                            tasks_data.append({
                                "id": item.get("id") or str(uuid.uuid4())[:8],
                                "text": item.get("text", "").strip(),
                                "completed": bool(item.get("completed", False)),
                                "priority": item.get("priority", "medium"),
                                "category": item.get("category", "General"),
                                "created_at": item.get("created_at") or datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"Error loading tasks: {e}")
    render_listbox()


def save_tasks():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save tasks: {e}")


def add_task():
    task_text = entry.get().strip()
    if task_text:
        new_item = {
            "id": str(uuid.uuid4())[:8],
            "text": task_text,
            "completed": False,
            "priority": "medium",
            "category": "General",
            "created_at": datetime.now().isoformat()
        }
        tasks_data.insert(0, new_item)
        entry.delete(0, tk.END)
        save_tasks()
        render_listbox()
    else:
        messagebox.showwarning("Input Error", "Please enter a task.")


def delete_task():
    try:
        index = listbox.curselection()[0]
        del tasks_data[index]
        save_tasks()
        render_listbox()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to delete.")


def toggle_task_status():
    try:
        index = listbox.curselection()[0]
        tasks_data[index]["completed"] = not tasks_data[index].get("completed", False)
        save_tasks()
        render_listbox()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to toggle.")


# Main Screen For Window
root = tk.Tk()
root.title("To-Do List (Connected Desktop + Web)")
root.geometry("520x580")
root.configure(bg="#0f172a")

# Header Frame
header_frame = tk.Frame(root, bg="#0f172a")
header_frame.pack(pady=(15, 10))

title_label = tk.Label(header_frame, text="⚡ Task Master", font=("Helvetica", 16, "bold"), fg="#f8fafc", bg="#0f172a")
title_label.pack()

subtitle_label = tk.Label(header_frame, text="Connected with Modern Web Frontend", font=("Helvetica", 9), fg="#94a3b8", bg="#0f172a")
subtitle_label.pack()

# Entry For Screen
entry_frame = tk.Frame(root, bg="#0f172a")
entry_frame.pack(pady=8)

entry = tk.Entry(entry_frame, width=32, font=("Helvetica", 11), bg="#1e293b", fg="#ffffff", insertbackground="#ffffff", relief="flat")
entry.pack(ipady=6, padx=5)
entry.bind("<Return>", lambda event: add_task())

# Buttons Container
button_frame = tk.Frame(root, bg="#0f172a")
button_frame.pack(pady=8)

add_button = tk.Button(button_frame, text="✚ Add Task", width=12, font=("Helvetica", 9, "bold"), bg="#6366f1", fg="#ffffff", activebackground="#4f46e5", activeforeground="#ffffff", relief="flat", cursor="hand2", command=add_task)
add_button.grid(row=0, column=0, padx=4)

toggle_button = tk.Button(button_frame, text="✓ Toggle Done", width=12, font=("Helvetica", 9, "bold"), bg="#10b981", fg="#ffffff", activebackground="#059669", activeforeground="#ffffff", relief="flat", cursor="hand2", command=toggle_task_status)
toggle_button.grid(row=0, column=1, padx=4)

delete_button = tk.Button(button_frame, text="🗑 Delete Task", width=12, font=("Helvetica", 9, "bold"), bg="#ef4444", fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff", relief="flat", cursor="hand2", command=delete_task)
delete_button.grid(row=0, column=2, padx=4)

# Listbox with Scrollbar
list_frame = tk.Frame(root, bg="#0f172a")
list_frame.pack(pady=10, padx=20, fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(
    list_frame,
    font=("Helvetica", 11),
    bg="#1e293b",
    fg="#f1f5f9",
    selectbackground="#6366f1",
    selectforeground="#ffffff",
    highlightthickness=1,
    highlightbackground="#334155",
    relief="flat",
    yscrollcommand=scrollbar.set,
    selectmode=tk.SINGLE
)
listbox.pack(side=tk.LEFT, fill="both", expand=True)
scrollbar.config(command=listbox.yview)

# Web Frontend Launch Button at Bottom
footer_frame = tk.Frame(root, bg="#0f172a")
footer_frame.pack(pady=(5, 15), fill="x", padx=20)

web_button = tk.Button(
    footer_frame,
    text="🌐 Open Web Frontend in Browser (http://localhost:5000)",
    font=("Helvetica", 10, "bold"),
    bg="#3b82f6",
    fg="#ffffff",
    activebackground="#2563eb",
    activeforeground="#ffffff",
    relief="flat",
    cursor="hand2",
    command=open_web_frontend
)
web_button.pack(fill="x", ipady=8)

load_tasks()

if __name__ == "__main__":
    root.mainloop()