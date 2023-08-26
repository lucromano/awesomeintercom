from flask import Flask, render_template, request, jsonify
import requests
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

handset_status = 'IDLE'


@app.route('/', methods=['GET', 'POST'])
def index():
    global handset_status

    if request.method == 'POST':
        data = request.get_json()
        handset_status = data['status']

    return render_template('index.html', handset_status=handset_status)




@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.get_json()['rpi_command']
    print(command)

    rpi_url = "http://192.168.1.111:5000/rpi_command"
    response = requests.post(rpi_url, json={'rpi_command': command})

    if response.status_code == 200:
        return jsonify({'message': 'command send success'})
    else:
        return jsonify({'message': 'command send error'})


@app.route('/voltages', methods=['GET', 'POST'])
def voltages():
    data = request.get_json()
    print(data)
    return jsonify({'message': 'success'})


app.run(host='0.0.0.0', port=5100)
