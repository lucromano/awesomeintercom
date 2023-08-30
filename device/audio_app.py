import automationhat as ah
from flask import Flask, request, jsonify
import time
import threading
import requests
import sounddevice as sd
import numpy as np
import socket
import queue

ah.enable_auto_lights(False)

lock = threading.Lock()

app = Flask(__name__)

audio_queue = queue.Queue()
stop_event = threading.Event()

sample_rate = 44100
channels = 1
target_host = '192.168.1.105'
target_port = 12334


def poll_inputs():
    while True:

        with lock:
            a1 = ah.analog.one.read()
            a2 = ah.analog.two.read()
            a3 = None
            r1 = None
            a4 = ah.analog.four.read()
            r2 = None
            r3 = None
            #             a3 = ah.analog.three.read()
            #             r1 = ah.relay.one.read()
            #             r2 = ah.relay.two.read()
            #             r3 = ah.relay.three.read()

            if a1 > 3.0 and a2 > 3.0:
                send_status('ringing')
            #             elif 0.5 > a1 > 1.5 and 1.0 > a2 > 5.0:
            #                 send_status('answered')

            send_hat_reads(a1, a2, a3, a4, r1, r2, r3)

        time.sleep(2)


def send_hat_reads(a1, a2, a3, a4, r1, r2, r3):
    voltages_url = "http://192.168.1.105:5100/voltages"
    response = requests.post(voltages_url, json={'reads': [a1, a2, a3, a4, r1, r2, r3]})


def send_status(status):
    status_url = "http://192.168.1.105:5100/"
    response = requests.post(status_url, json={'status': status})

    if response.status_code == 200:
        print("Status sent: {}".format(status))
    else:
        print("Status failed: {}".format(status))


@app.route('/rpi_command', methods=['GET', 'POST'])
def rpi_command():
    data = request.get_json()
    command = data['rpi_command']

    if command == 'answer':
        ah.relay.one.on()
        ah.relay.two.on()

        adc_thread = threading.Thread(target=read_adc_and_convert_to_audio)
        send_thread = threading.Thread(target=send_audio_data)
        adc_thread.start()
        send_thread.start()

    elif command == 'open':
        ah.relay.three.on()
        time.sleep(0.5)
        ah.relay.three.off()
        send_status('opened')

    elif command == 'hangup':
        ah.relay.one.off()
        ah.relay.two.off()
        ah.output.one.off()

        #         stop_event.set()  # Signal threads to stop
        adc_thread.join()
        send_thread.join()

        send_status('idle')

    return jsonify({'message': 'success'})


def adc_to_audio(voltage):
    # Map the ADC voltage to audio sample values
    audio_sample = int(voltage * 32767)  # Assuming 16-bit audio
    return audio_sample


# def audio_callback(outdata, frames, time, status):
#     try:
#         audio_samples = audio_queue.get_nowait()
#     except queue.Empty:
#         audio_samples = np.zeros(frames, dtype=np.int16)
#     
#     outdata[:frames, 0] = audio_samples


def read_adc_and_convert_to_audio():
    #     while not stop_event.is_set():
    while True:
        voltage = ah.analog.four.read()  # Read analog voltage
        audio_sample = adc_to_audio(voltage)  # Convert to audio sample
        audio_queue.put(audio_sample)  # Add audio sample to queue


def send_audio_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((target_host, target_port))

        #         while not stop_event.is_set():
        while True:
            try:
                audio_samples = audio_queue.get_nowait()
                data_to_send = np.array(audio_samples, dtype=np.int16)

                s.sendall(data_to_send.tobytes())
            except queue.Empty:
                pass


polling_thread = threading.Thread(target=poll_inputs)
polling_thread.daemon = True
polling_thread.start()
app.run(host='0.0.0.0', port=5000)






