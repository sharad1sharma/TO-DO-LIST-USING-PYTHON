import os
import json
import uuid
import tempfile
import shutil
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
PUBLIC_DIR = os.path.join(ROOT_DIR, "public")
STATIC_DIR = PUBLIC_DIR if os.path.exists(PUBLIC_DIR) else os.path.join(ROOT_DIR, "static")

# Serverless environment handling for Vercel
IS_VERCEL = bool(os.environ.get("VERCEL"))
if IS_VERCEL:
    DATA_FILE = os.path.join(tempfile.gettempdir(), "tasks.json")
    bundled = os.path.join(ROOT_DIR, "tasks.json")
    if not os.path.exists(DATA_FILE) and os.path.exists(bundled):
        try:
            shutil.copyfile(bundled, DATA_FILE)
        except Exception:
            pass
else:
    DATA_FILE = os.path.join(ROOT_DIR, "tasks.json")

app = Flask(__name__, static_folder=STATIC_DIR if os.path.exists(STATIC_DIR) else None)
CORS(app)

# In-memory default tasks
MEM_TASKS = [
    {
        "id": "t1a2b3c4",
        "text": "Connect modern web frontend to Python backend",
        "completed": True,
        "priority": "high",
        "category": "Work",
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "t5d6e7f8",
        "text": "Explore TaskFlow features & filters",
        "completed": False,
        "priority": "medium",
        "category": "General",
        "created_at": datetime.now().isoformat()
    }
]


def normalize_task(raw_task):
    if isinstance(raw_task, str):
        return {
            "id": str(uuid.uuid4())[:8],
            "text": raw_task.strip(),
            "completed": False,
            "priority": "medium",
            "category": "General",
            "created_at": datetime.now().isoformat(),
        }
    elif isinstance(raw_task, dict):
        return {
            "id": raw_task.get("id") or str(uuid.uuid4())[:8],
            "text": raw_task.get("text", "").strip(),
            "completed": bool(raw_task.get("completed", False)),
            "priority": raw_task.get("priority", "medium").lower(),
            "category": raw_task.get("category", "General"),
            "created_at": raw_task.get("created_at") or datetime.now().isoformat(),
        }
    return None


def read_tasks():
    global MEM_TASKS
    if not os.path.exists(DATA_FILE):
        return MEM_TASKS
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return MEM_TASKS
            normalized = []
            for item in data:
                task = normalize_task(item)
                if task and task["text"]:
                    normalized.append(task)
            MEM_TASKS = normalized
            return normalized
    except Exception as e:
        print(f"Read error: {e}")
        return MEM_TASKS


def write_tasks(tasks):
    global MEM_TASKS
    MEM_TASKS = tasks
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Write error, keeping in memory: {e}")


# ==========================================
# API Routes (Supporting /api/* and root aliases)
# ==========================================

@app.route("/api/health", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "env": "vercel" if IS_VERCEL else "local"})


@app.route("/api/tasks", methods=["GET"])
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = read_tasks()
    return jsonify({"tasks": tasks, "count": len(tasks)})


@app.route("/api/tasks", methods=["POST"])
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Task text is required"}), 400

    tasks = read_tasks()
    new_task = {
        "id": str(uuid.uuid4())[:8],
        "text": text,
        "completed": bool(data.get("completed", False)),
        "priority": data.get("priority", "medium").lower(),
        "category": data.get("category", "General").strip() or "General",
        "created_at": datetime.now().isoformat(),
    }
    tasks.insert(0, new_task)
    write_tasks(tasks)
    return jsonify({"success": True, "task": new_task}), 201


@app.route("/api/tasks/<task_id>", methods=["PUT", "PATCH"])
@app.route("/tasks/<task_id>", methods=["PUT", "PATCH"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    tasks = read_tasks()
    target = None
    for task in tasks:
        if str(task["id"]) == str(task_id):
            target = task
            break

    if not target:
        return jsonify({"error": "Task not found"}), 404

    if "text" in data and str(data["text"]).strip():
        target["text"] = str(data["text"]).strip()
    if "completed" in data:
        target["completed"] = bool(data["completed"])
    if "priority" in data:
        target["priority"] = str(data["priority"]).lower()
    if "category" in data:
        target["category"] = str(data["category"]).strip() or "General"

    write_tasks(tasks)
    return jsonify({"success": True, "task": target})


@app.route("/api/tasks/<task_id>/toggle", methods=["POST"])
@app.route("/tasks/<task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    tasks = read_tasks()
    target = None
    for task in tasks:
        if str(task["id"]) == str(task_id):
            target = task
            break

    if not target:
        return jsonify({"error": "Task not found"}), 404

    target["completed"] = not target["completed"]
    write_tasks(tasks)
    return jsonify({"success": True, "task": target})


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = read_tasks()
    initial_len = len(tasks)
    tasks = [t for t in tasks if str(t["id"]) != str(task_id)]
    if len(tasks) == initial_len:
        return jsonify({"error": "Task not found"}), 404

    write_tasks(tasks)
    return jsonify({"success": True, "deleted_id": task_id})


@app.route("/api/tasks/clear-completed", methods=["DELETE"])
@app.route("/tasks/clear-completed", methods=["DELETE"])
def clear_completed():
    tasks = read_tasks()
    remaining = [t for t in tasks if not t.get("completed", False)]
    cleared_count = len(tasks) - len(remaining)
    write_tasks(remaining)
    return jsonify({"success": True, "cleared_count": cleared_count})


# Fallback for local static file serving
@app.route("/")
def index():
    if app.static_folder and os.path.exists(os.path.join(app.static_folder, "index.html")):
        return send_from_directory(app.static_folder, "index.html")
    return jsonify({"status": "TaskFlow API Online"})


@app.route("/<path:path>")
def static_proxy(path):
    if app.static_folder:
        target_file = os.path.join(app.static_folder, path)
        if os.path.exists(target_file) and os.path.isfile(target_file):
            return send_from_directory(app.static_folder, path)
    return jsonify({"error": "Not found"}), 404
