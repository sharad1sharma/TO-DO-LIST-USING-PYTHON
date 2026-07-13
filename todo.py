                      # To-Do List Application Made By :- SHARAD SHARMA
            #TASK-1: To-Do List ApplicationUSING PYTHON COMPLETED ON 12-06-2026
                           # BY CodSoft Technologies Pvt. Ltd.       



import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE ="tasks.json"

# Here Some Functions Define Like :-- load_tasks, save_tasks, add_task, delete_task.......!!

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                tasks = json.load(f)
                for task in tasks:
                    listbox.insert(tk.END, task)
            except json.JSONDecodeError:
                pass  # empty file found
            
                
def save_tasks():
    tasks = listbox.get(0, tk.END)
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)
        
def add_task():
    task = entry.get()
    if task:
        listbox.insert(tk.END, task)
        entry.delete(0, tk.END)
        save_tasks()
    else:
        messagebox.showwarning("Input Error", "Please enter a task.")

def delete_task():
    try:
        index = listbox.curselection()[0]
        listbox.delete(index)
        save_tasks()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to delete.")

# Main Screen For Window.......!!

root = tk.Tk()
root.title("To-Do List")
root.geometry("500x500")

# Entry For Screen.......!!

entry = tk.Entry(root, width=30)
entry.pack(pady=10)

# Add Buttons For Screen.......!!

add_button = tk.Button(root,text="Add Task", width=15, command=add_task)
add_button.pack(pady=5)

# Delete Button For Screen.......!!

delete_button = tk.Button(root, text="Delete Task", width=15, command=delete_task)
delete_button.pack(pady=5)

# ListboxFor Screen.......!!
listbox = tk.Listbox(root, width=30, height=15, selectmode=tk.SINGLE)
listbox.pack(pady=15)

load_tasks()

root.mainloop()