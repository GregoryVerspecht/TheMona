import RPi.GPIO as GPIO
from flask import Flask, render_template, send_from_directory, make_response, request, jsonify

app = Flask(__name__, static_url_path='/static', template_folder='../templates')

# GPIO Setup
GPIO.setmode(GPIO.BCM)
pins = [17, 18, 27]
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:path>')
def static_files(path):
    response = make_response(send_from_directory('static', path))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# API route to get pin status
@app.route('/api/pins/status', methods=['GET'])
def get_pin_status():
    status = {pin: GPIO.input(pin) for pin in pins}
    return jsonify(status)

# API route to start the game
@app.route('/api/game/start', methods=['POST'])
def start_game():
    return jsonify({'message': 'Game started!'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=("/home/mona/ssl/cert.pem", "/home/mona/ssl/key.pem"))
