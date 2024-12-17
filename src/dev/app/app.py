from flask import Flask, render_template, send_from_directory, make_response

app = Flask(__name__, static_url_path='/static', template_folder='../templates')

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:path>')
def static_files(path):
    response = make_response(send_from_directory('static', path))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=("/home/mona/ssl/cert.pem", "/home/mona/ssl/key.pem"))
