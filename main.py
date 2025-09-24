import os
import threading
import uuid
from flask import Flask, render_template, request, jsonify

from automation_wrapper import run_automation

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# --- Global State ---
automation_thread = None
stop_event = threading.Event()
automation_status = {
    "status": "Stopped",
    "error": None,
}

def status_callback(status, error=None):
    """Callback function to update the global status from the worker thread."""
    global automation_status
    automation_status["status"] = status
    automation_status["error"] = error
    print(f"Status updated: {status}" + (f" | Error: {error}" if error else ""))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    return jsonify(automation_status)

@app.route("/start", methods=["POST"])
def start():
    global automation_thread, stop_event, automation_status

    if automation_thread and automation_thread.is_alive():
        return jsonify({"status": "error", "message": "Automation is already running."}), 400

    if 'creds_file' not in request.files or 'sheet_name' not in request.form:
        return jsonify({"status": "error", "message": "Missing credential file or sheet name."}), 400

    creds_file = request.files['creds_file']
    sheet_name = request.form['sheet_name']

    if creds_file.filename == '' or sheet_name == '':
        return jsonify({"status": "error", "message": "Credential file or sheet name cannot be empty."}), 400

    if not creds_file.filename.endswith('.json'):
        return jsonify({"status": "error", "message": "Invalid file type. Please upload a .json file."}), 400

    # Save the credential file securely
    filename = str(uuid.uuid4()) + ".json"
    creds_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    creds_file.save(creds_path)

    # Reset state and start the automation thread
    stop_event.clear()
    automation_status["error"] = None
    
    automation_thread = threading.Thread(
        target=run_automation,
        args=(creds_path, sheet_name, stop_event, status_callback)
    )
    automation_thread.start()

    return jsonify({"status": "success", "message": "Automation started."})

@app.route("/stop", methods=["POST"])
def stop():
    global automation_thread, stop_event

    if not automation_thread or not automation_thread.is_alive():
        return jsonify({"status": "error", "message": "Automation is not running."}), 400

    print("🛑 Received stop request. Setting stop event.")
    stop_event.set()
    # The thread will update the status to "Stopped" upon exit
    
    return jsonify({"status": "success", "message": "Stop signal sent."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
