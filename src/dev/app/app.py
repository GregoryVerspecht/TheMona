from flask import Flask, render_template, request, jsonify
import subprocess
import os
import signal

app = Flask(__name__, template_folder='../templates')

# Categorieën met modes
categories = {
    "game_modes": {
        "mode1": "/home/mona/the-mona/app/game_modes/mode1.py",
        "mode2": "/home/mona/the-mona/app/game_modes/mode2.py"
    },
    "maintenance_modes": {
        "Flashkes": "/home/mona/the-mona/app/game_modes/flash2.py",
        "Sound of the Police": "/home/mona/the-mona/app/game_modes/sound-of-the-police.py"
    }
}

# Globale variabelen voor actieve processen
active_process = None


@app.route("/")
def index():
    # Geef alle categorieën en modes door aan de template
    return render_template("index.html", categories=categories)


@app.route("/start", methods=["POST"])
def start_mode():
    global active_process
    mode = request.json.get("mode")
    category = request.json.get("category")

    if category in categories and mode in categories[category]:
        if active_process is not None:
            return jsonify({"status": "error", "message": "A mode is already running"})

        # Start de geselecteerde mode met sudo
        process = subprocess.Popen(["sudo", "python", categories[category][mode]])
        active_process = {"mode": mode, "category": category, "process": process}
        return jsonify({"status": "success", "message": f"{mode} from {category} started"})

    return jsonify({"status": "error", "message": "Invalid mode or category"})


@app.route("/stop", methods=["POST"])
def stop_mode():
    global active_process
    mode = request.json.get("mode")
    category = request.json.get("category")

    if active_process and active_process["mode"] == mode and active_process["category"] == category:
        process = active_process["process"]
        os.kill(process.pid, signal.SIGTERM)
        active_process = None
        return jsonify({"status": "success", "message": f"{mode} from {category} stopped"})

    return jsonify({"status": "error", "message": "Mode not running or invalid"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=("/home/mona/ssl/cert.pem", "/home/mona/ssl/key.pem"))
