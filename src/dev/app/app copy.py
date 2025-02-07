from flask import Flask, render_template, request, jsonify
import subprocess
import os
import signal

app = Flask(
    __name__,
    template_folder=os.path.join(os.getcwd(), "views"),  # Absoluut pad naar views
    static_folder=os.path.join(os.getcwd(), "static")    # Absoluut pad naar assets
)


# Categorieën met modes
categories = {
    "game_modes": {
        "Squid Game": "/home/mona/the-mona/app/game_modes/mode1.py",
        "Russian Roulette": "/home/mona/the-mona/app/game_modes/mode2.py"
    },
    "maintenance_modes": {
        "Flashkes": "/home/mona/the-mona/app/maintenance/flash2.py",
        "Sound of the Police": "/home/mona/the-mona/app/maintenance/sound-of-the-police.py",
        "Rainbow": "/home/mona/the-mona/app/maintenance/rainbow.py"
    },
        "sounboard": {
        "Peppa_Pig_The_Mix": "/home/mona/the-mona/app/soundboard/playsound_peppa_liesa.py",
        "Sound of the Police": "/home/mona/the-mona/app/soundboard/playsound_sound_of_the_police.py",
        "Meow": "/home/mona/the-mona/app/soundboard/playsound_meow.py",
        "PgPgPg": "/home/mona/the-mona/app/soundboard/playsound_liesa_pgpg.py"
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

@app.route("/debug")
def debug():
    print("Template folder:", app.template_folder)
    print("Bestand aanwezig:", os.path.exists(os.path.join(app.template_folder, "index.html")))
    return render_template("index.html")


@app.route("/direct")
def direct():
    with open('/home/mona/the-mona/templates/index.html') as f:
        return f.read()

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

    print("Templates folder:", os.path.abspath(app.template_folder))

    app.run(host="0.0.0.0", port=8443, ssl_context=("/home/mona/ssl/cert.pem", "/home/mona/ssl/key.pem"))
