from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import logging
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
import utils
import os
import numpy as np
import socket
import sounddevice as sd
import threading
import time

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app.secret_key = os.urandom(24)

handset_status = 'IDLE'
listening_thread = None
stop_audio_threads = threading.Event()

sample_rate = 44100
channels = 1


@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('user_type') == 'user':
        return redirect(url_for('home'))

    else:
        form = LoginForm()

        if form.validate_on_submit():
            hashed_password = utils.user_login(form.email.data)[0][0]
            password_check = check_password_hash(hashed_password, form.password.data)
            if password_check:
                session['user_type'] = 'user'
                return redirect(url_for('home'))
            else:
                return redirect(url_for('index'))

        else:
            return render_template('index.html', form=form)


@app.route('/home', methods=['GET', 'POST'])
def home():
    if session.get('user_type') == 'user':
        global handset_status

        if request.method == 'POST':
            data = request.get_json()
            handset_status = data['status']

        return render_template('home.html', handset_status=handset_status)
    else:
        return redirect(url_for('index'))


@app.route('/send_command', methods=['POST'])
def send_command():
    global listening_thread

    command = request.get_json()['rpi_command']
    print(command)

    if command == 'answer':
        listening_thread = threading.Thread(target=listen_audio)
        listening_thread.start()
    elif command == 'hangup':
        listening_thread.join()
        print(listening_thread)

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

#
# def listen_audio():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
#         server_socket.bind(('0.0.0.0', 12334))
#         server_socket.listen(1)
#         print("Listening for audio data...")
#
#         connection = None
#
#         try:
#             connection, address = server_socket.accept()
#             print(f"Connected to {address}")
#         except Exception as e:
#             print(f"Error accepting connection: {e}")
#
#         if connection:
#             sd_stream = sd.OutputStream(channels=channels, samplerate=sample_rate, blocksize=4096)
#             sd_stream.start()
#
#             # try:
#             while True:
#                 data = connection.recv(1024)
#                 if not data:
#                     break
#
#                 audio_samples = np.frombuffer(data, dtype=np.int16)
#                 audio_samples_float32 = audio_samples.astype(
#                     np.float32) / 32768.0  # Convert to float32 in range [-1, 1]
#
#                 sd_stream.write(audio_samples_float32)
#             # except KeyboardInterrupt:
#             #     print("Server interrupted.")
#             # finally:
#             #     connection.close()
#             #     sd_stream.stop()


app.run(host='0.0.0.0', port=5100)
