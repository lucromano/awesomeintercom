import asyncio
import logging
import os
from aiohttp import web, WSMsgType, ClientSession
from forms import *
from views import *
import aiohttp_session
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy
from aiohttp_security import authorized_userid
from cryptography import fernet
from passlib.context import CryptContext
import utils
import aiohttp_jinja2
import jinja2
import base64
import bcrypt
import json


async def setup_session(app):
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    storage = EncryptedCookieStorage(secret_key)
    setup(app, storage)

app = web.Application()
app['websockets'] = set()

app.on_startup.append(setup_session)
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

# Security setup
class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def authorized_userid(self, identity):
        return identity

    async def permits(self, identity, permission, context=None):
        # You can implement custom permission checks here
        return True


async def on_shutdown(app):
    # Close any open websockets on shutdown
    for ws in app['websockets']:
        await ws.close()

app.on_shutdown.append(on_shutdown)


@aiohttp_jinja2.template('index.html')
async def index(request):
    # user_type = await authorized_userid(request)
    session = await get_session(request)
    user_type = session.get('user_type', None)

    if user_type == 'user':
        return web.HTTPFound('/home')
    else:
        form = LoginForm()
        # create_form = CreateForm()

        if request.method == 'POST':
            data = await request.post()

            # if 'email' in data and 'password' in data:

            email = data['email']
            password = data['password']
            hashed_password = utils.user_login(email)[0][0]

            encoded_password = password.encode('utf-8')
            encoded_hashed_password = hashed_password.encode('utf-8')

            if bcrypt.checkpw(encoded_password, encoded_hashed_password):
                session = await get_session(request)
                session['user_type'] = 'user'
                return web.HTTPFound('/home')
            else:
                return web.HTTPFound('/')

            # else:
            #     utils.create_user('Luciano', 'Romano', 'luciano@awesomeinter.com', 'luctech123!')

        # return {'form': form, 'create_form': create_form}
        return {'form': form}


@aiohttp_jinja2.template('home.html')
async def home(request):
    session = await get_session(request)
    user_type = session.get('user_type', None)
    if user_type == 'user':
        websocket_status = request.app.get('status', 'IDLE')

        if request.method == 'POST':
            data = await request.json()
            request.app['status'] = data['status']

        url_for_send_command = request.app.router['send_command'].url_for()

        return {'handset_status': websocket_status, 'url_for_send_command': url_for_send_command}

    else:
        return web.HTTPFound('/')


async def send_command(request):
    data = await request.json()
    command = data['rpi_command']
    print(command)
    rpi_url = "http://192.168.1.111:5000/receive_commands"
    async with ClientSession() as session:
        async with session.post(rpi_url, json={'rpi_command': command}) as response:
            if response.status == 200:
                return web.json_response({'message': 'command send success'})
            else:
                return web.json_response({'message': 'command send error'})


async def voltages(request):
    data = await request.json()
    print(data)
    return web.json_response({'message': 'success'})


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    app['websockets'].add(ws)

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    # Handle WebSocket messages here
                    try:
                        data = json.loads(msg.data)
                        # Process the JSON data sent by the client
                        # Example: You can access data['reads'] or data['status']
                        # and perform actions based on the received data.
                        if 'reads' in data:
                            a1, a2 = data['reads']
                            # Perform actions based on a1 and a2
                        elif 'status' in data:
                            status = data['status']
                            # Handle the received status
                    except json.JSONDecodeError as e:
                        # Handle JSON decoding errors
                        print(f"Failed to decode JSON: {e}")
            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket connection closed with error: {ws.exception()}")

    finally:
        app['websockets'].remove(ws)

app.router.add_get('/', index)
app.router.add_post('/', index)
app.router.add_get('/home', home)
app.router.add_post('/home', home)
app.router.add_post('/send_command', SendCommandView, name='send_command')
app.router.add_post('/voltages', voltages)
app.router.add_get('/websocket', websocket_handler)

web.run_app(app, port=5100)
