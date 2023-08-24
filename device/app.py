import automationhat
from flask import Flask, request, jsonify
import time
import threading
import requests

lock = threading.Lock()

app = Flask(__name__)


def poll_inputs():
    while True:

        with lock:
            a1 = automationhat.analog.one.read()
            a2 = automationhat.analog.two.read()
            if a1 > 3.0 and a2 > 3.0:
                send_status('ringing')
            elif 0.5 > a1 > 1.5 and 1.0 > a2 > 5.0:
                send_status('answered')

            send_voltages(a1, a2)

        time.sleep(5)


def send_voltages(a1, a2):
    voltages_url = "http://192.168.1.105:5100/voltages"
    response = requests.post(voltages_url, json={'voltages': [a1, a2]})


def send_status(status):
    status_url = "http://192.168.1.105:5100/"
    response = requests.post(status_url, json={'status': status})

    if response.status_code == 200:
        print("Status sent")
    else:
        print("Status failed")


@app.route('/rpi_command', methods=['GET', 'POST'])
def rpi_command():
    data = request.get_json()
    command = data['rpi_command']

    if command == 'answer':
        automationhat.relay.two.toggle()
        automationhat.relay.three.toggle()
        automationhat.output.one.on()
        time.sleep(0.3)
    elif command == 'open':
        automationhat.relay.one.toggle()
        time.sleep(0.3)
        automationhat.relay.one.toggle()
        send_status('opened')
    elif command == 'hangup':
        automationhat.relay.two.toggle()
        automationhat.relay.three.toggle()
        automationhat.output.one.off()
        time.sleep(0.3)
        send_status('idle')

    return jsonify({'message': 'success'})


polling_thread = threading.Thread(target=poll_inputs)
polling_thread.daemon = True
polling_thread.start()
app.run(host='0.0.0.0', port=5000)


