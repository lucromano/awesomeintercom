import automationhat as ah
from flask import Flask, request, jsonify
import time
import threading
import requests

ah.enable_auto_lights(False)

lock = threading.Lock()

app = Flask(__name__)


def poll_inputs():
    while True:

        with lock:
            a1 = ah.analog.one.read()
            a2 = ah.analog.two.read()
            #             a3 = ah.analog.three.read()

            r1 = ah.relay.one.read()
            r2 = ah.relay.two.read()
            r3 = ah.relay.three.read()

            if a1 > 3.0 and a2 > 3.0:
                send_status('ringing')
            elif 0.5 > a1 > 1.5 and 1.0 > a2 > 5.0:
                send_status('answered')

            send_hat_reads(a1, a2, r1, r2, r3)

        time.sleep(1)


def send_hat_reads(a1, a2, r1, r2, r3):
    voltages_url = "http://192.168.1.105:5100/voltages"
    response = requests.post(voltages_url, json={'reads': [a1, a2, r1, r2, r3]})


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
        ah.relay.two.on()
        ah.relay.three.on()
        ah.output.one.on()
        time.sleep(0.3)
    elif command == 'open':
        ah.relay.one.on()
        time.sleep(0.3)
        ah.relay.one.off()
        send_status('opened')
    elif command == 'hangup':
        ah.relay.two.off()
        ah.relay.three.off()
        ah.output.one.off()
        time.sleep(0.3)
        send_status('idle')

    return jsonify({'message': 'success'})


polling_thread = threading.Thread(target=poll_inputs)
polling_thread.daemon = True
polling_thread.start()
app.run(host='0.0.0.0', port=5000)



