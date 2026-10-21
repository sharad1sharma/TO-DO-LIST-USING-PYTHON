import os
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

DATA_FILE = "tasks.json"

app = Flask(__name__, static_folder="static")
CORS(app)


def normalize_task(raw_task):
    """Normalize a task into standard dictionary format for web & desktop compatibility."""
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
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            normalized = []
            for item in data:
                task = normalize_task(item)
                if task and task["text"]:
                    normalized.append(task)
            return normalized
    except Exception as e:
        print(f"Error reading {DATA_FILE}: {e}")
        return []


def write_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


# --- Static and Web UI Route ---
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


# --- API Routes ---
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "file": DATA_FILE})


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = read_tasks()
    return jsonify({"tasks": tasks, "count": len(tasks)})


@app.route("/api/tasks", methods=["POST"])
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
def delete_task(task_id):
    tasks = read_tasks()
    initial_len = len(tasks)
    tasks = [t for t in tasks if str(t["id"]) != str(task_id)]
    if len(tasks) == initial_len:
        return jsonify({"error": "Task not found"}), 404

    write_tasks(tasks)
    return jsonify({"success": True, "deleted_id": task_id})


@app.route("/api/tasks/clear-completed", methods=["DELETE"])
def clear_completed():
    tasks = read_tasks()
    remaining = [t for t in tasks if not t.get("completed", False)]
    cleared_count = len(tasks) - len(remaining)
    write_tasks(remaining)
    return jsonify({"success": True, "cleared_count": cleared_count})


@app.route("/api/tasks/reorder", methods=["POST"])
def reorder_tasks():
    data = request.get_json(silent=True) or {}
    ordered_ids = data.get("ids", [])
    if not isinstance(ordered_ids, list):
        return jsonify({"error": "ids list required"}), 400

    tasks = read_tasks()
    task_map = {str(t["id"]): t for t in tasks}
    reordered = []
    for tid in ordered_ids:
        if str(tid) in task_map:
            reordered.append(task_map.pop(str(tid)))
    # Append any remaining that were not in the reordered list
    for remaining_task in task_map.values():
        reordered.append(remaining_task)

    write_tasks(reordered)
    return jsonify({"success": True, "tasks": reordered})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[TaskFlow] Backend & Web Frontend running on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
