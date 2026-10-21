import os
from api.index import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[TaskFlow] Running locally on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
