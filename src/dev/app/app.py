from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Dictionary voor beschikbare game modes
game_modes = {
    "mode1": "game_modes/mode1.py",
    "mode2": "game_modes/mode2.py",
    "mode3": "game_modes/flash2.py"
    
}

@app.route("/")
def index():
    return render_template("index.html", modes=game_modes.keys())

@app.route("/start", methods=["POST"])
def start_game():
    mode = request.json.get("mode")
    if mode in game_modes:
        # Start de game mode (bijv. als subprocess)
        subprocess.Popen(["python", game_modes[mode]])
        return jsonify({"status": "success", "message": f"{mode} started"})
    return jsonify({"status": "error", "message": "Invalid mode"})

@app.route("/stop", methods=["POST"])
def stop_game():
    mode = request.json.get("mode")
    # Je kunt hier logica toevoegen om een specifieke subprocess te beëindigen
    return jsonify({"status": "success", "message": f"{mode} stopped"})

if __name__ == "__main__":
    app.run(debug=True)
