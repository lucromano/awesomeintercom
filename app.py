from flask import Flask, render_template, request, redirect
import requests
import utils

app = Flask(__name__)


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
    command = request.form.get('command')

    rpi_url = "http://192.168.1.111:5000/rpi_command"
    response = requests.post(rpi_url, json={'rpi_command': command})

    if response.status_code == 200:

        print("Command sent successfully!")
    else:
        print("Failed to send command to Raspberry Pi.")

    return redirect('/')


app.run(host='0.0.0.0', port=5100)
