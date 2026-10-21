# 📝 To-Do List Application

A Python and Web-based To-Do List Application with synchronized persistence across both a Desktop GUI (Tkinter) and a Classic Web Frontend (HTML5, CSS3, JavaScript), connected seamlessly via a Flask REST API backend.

**Developed By:** Sharad Sharma  
**Task:** Task-1: To-Do List Application Using Python  
**Organization:** CodSoft Technologies Pvt. Ltd.

---

## 📌 Features

### 1. 🌐 Classic Web Frontend
- **Design & Layout**: Clean, classic, standard CSS interface with fixed 500px width (clean white card, `#f4f4f9` light background, standard Arial font).
- **Task Management**:
  - Add tasks with the Enter key or "Add Task" button.
  - Interactive checkboxes to mark tasks as completed (with strikethrough styling).
  - Delete individual tasks with one click.
  - "Clear Completed" button to purge finished tasks.
- **Filter Tabs**: Toggle between **All**, **Active**, and **Completed** tasks in real time.
- **Task Counter**: Live counter displaying the number of active tasks remaining.
- **CSS3 & JS Pop Animation Footer**:
  - Interactive footer badge with CSS3 `@keyframes popAnimation` scale-bounce effect.
  - JavaScript-powered pop trigger on click or task creation.
  - Copyright and legal notice:
    > *All Rights Reserved. All other trademarks and copyrights are the property of their respective holders.*  
    > *Copyright © 2026 Sharad Sharma.*

### 2. 🖥️ Python Desktop GUI (`todo.py`)
- Built with Python's native **Tkinter** library.
- Add, toggle status, and delete tasks directly from your desktop.
- 1-Click **"🌐 Open Web Frontend in Browser"** button to launch the web interface in your default browser.
- Automatically synchronizes with `tasks.json`.

### 3. ⚙️ Python Backend Server (`app.py`)
- Lightweight REST API powered by **Flask**.
- Automatically reads from and writes to `tasks.json`.
- Automatically normalizes legacy and rich task entries for full backwards compatibility.

---

## 📂 Project Structure

```text
todolist/
├── app.py             # Flask backend & REST API server
├── todo.py            # Tkinter desktop GUI application
├── tasks.json         # Shared JSON database file
├── README.md          # Project documentation
└── static/
    ├── index.html     # Classic web frontend HTML
    ├── style.css      # Classic CSS3 stylesheet with pop keyframe animations
    └── app.js         # JavaScript application logic & API synchronization
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.8+ installed along with Flask:
```bash
pip install flask flask-cors
```

### Option A: Run the Web Application
1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and go to:
   ```text
   http://127.0.0.1:5000
   ```

### Option B: Run the Desktop GUI Application
1. Launch the Tkinter desktop app:
   ```bash
   python todo.py
   ```
2. You can use the desktop interface or click **"Open Web Frontend in Browser"** to launch the web app side-by-side.

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tasks` | Retrieve all tasks from `tasks.json` |
| `POST` | `/api/tasks` | Add a new task (`{"text": "Your task"}`) |
| `POST` | `/api/tasks/<id>/toggle` | Toggle task completion status |
| `PUT` | `/api/tasks/<id>` | Update task title or properties |
| `DELETE` | `/api/tasks/<id>` | Delete a task by ID |
| `DELETE` | `/api/tasks/clear-completed` | Clear all completed tasks |
| `GET` | `/api/health` | Check backend server health |

---

## 📜 License & Copyright

All Rights Reserved. All other trademarks and copyrights are the property of their respective holders.

Copyright © 2026  
**Sharad Sharma**
