from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import logging
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
import utils
import os



app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app.secret_key = os.urandom(24)

handset_status = 'IDLE'


@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('user_type') == 'user':
        return redirect(url_for('home'))

    else:
        form = LoginForm()

        create = CreateForm()

        if form.validate_on_submit():
            hashed_password = utils.user_login(form.email.data)[0][0]
            password_check = check_password_hash(hashed_password, form.password.data)
            if password_check:
                session['user_type'] = 'user'
                return redirect(url_for('home'))
            else:
                return redirect(url_for('index'))

        elif create.validate_on_submit():
            utils.create_user('Luciano', 'Romano', 'luciano@awesomeinter.com', 'luctech12345!')
            return redirect(url_for('index'))

        else:
            return render_template('index.html', form=form, create=create)


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
