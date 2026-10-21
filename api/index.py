import os
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
CORS(app)

# In-memory storage for serverless runtime
tasks_data = [
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

# Try to load existing tasks.json if available
data_file_path = os.path.join(CURRENT_DIR, "tasks.json")
if not os.path.exists(data_file_path):
    data_file_path = os.path.join(os.path.dirname(CURRENT_DIR), "tasks.json")

if os.path.exists(data_file_path):
    try:
        with open(data_file_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, list) and len(loaded) > 0:
                tasks_data = loaded
    except Exception as e:
        print(f"Error loading initial tasks: {e}")


def save_tasks_if_possible():
    try:
        if os.path.exists(data_file_path):
            with open(data_file_path, "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        # In read-only serverless environment, in-memory state is preserved during lambda lifecycle
        print(f"Note: filesystem is read-only ({e}), maintaining in-memory state")


# ==========================================
# Static Frontend Routes (Explicit MimeTypes)
# ==========================================

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(app.static_folder, "style.css", mimetype="text/css")


@app.route("/app.js")
def js():
    return send_from_directory(app.static_folder, "app.js", mimetype="application/javascript")


# ==========================================
# REST API Routes (Supporting /api/* & /*)
# ==========================================

@app.route("/api/health", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "count": len(tasks_data)})


@app.route("/api/tasks", methods=["GET"])
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks_data, "count": len(tasks_data)})


@app.route("/api/tasks", methods=["POST"])
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Task text is required"}), 400

    new_task = {
        "id": str(uuid.uuid4())[:8],
        "text": text,
        "completed": bool(data.get("completed", False)),
        "priority": data.get("priority", "medium").lower(),
        "category": data.get("category", "General").strip() or "General",
        "created_at": datetime.now().isoformat(),
    }
    tasks_data.insert(0, new_task)
    save_tasks_if_possible()
    return jsonify({"success": True, "task": new_task}), 201


@app.route("/api/tasks/<task_id>", methods=["PUT", "PATCH"])
@app.route("/tasks/<task_id>", methods=["PUT", "PATCH"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    target = next((t for t in tasks_data if str(t["id"]) == str(task_id)), None)

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

    save_tasks_if_possible()
    return jsonify({"success": True, "task": target})


@app.route("/api/tasks/<task_id>/toggle", methods=["POST"])
@app.route("/tasks/<task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    target = next((t for t in tasks_data if str(t["id"]) == str(task_id)), None)

    if not target:
        return jsonify({"error": "Task not found"}), 404

    target["completed"] = not target.get("completed", False)
    save_tasks_if_possible()
    return jsonify({"success": True, "task": target})


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks_data
    initial_len = len(tasks_data)
    tasks_data = [t for t in tasks_data if str(t["id"]) != str(task_id)]

    if len(tasks_data) == initial_len:
        return jsonify({"error": "Task not found"}), 404

    save_tasks_if_possible()
    return jsonify({"success": True, "deleted_id": task_id})


@app.route("/api/tasks/clear-completed", methods=["DELETE"])
@app.route("/tasks/clear-completed", methods=["DELETE"])
def clear_completed():
    global tasks_data
    initial_len = len(tasks_data)
    tasks_data = [t for t in tasks_data if not t.get("completed", False)]
    cleared_count = initial_len - len(tasks_data)
    save_tasks_if_possible()
    return jsonify({"success": True, "cleared_count": cleared_count})
