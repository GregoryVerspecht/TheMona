from flask import Flask, send_from_directory, render_template
app = Flask(__name__, static_url_path='/static', template_folder='../templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=("/home/mona/ssl/cert.pem", "/home/mona/ssl/key.pem"))