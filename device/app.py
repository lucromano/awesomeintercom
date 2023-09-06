import automationhat as ah
import time
import threading
import asyncio
import aiohttp
import websockets
import json

ah.enable_auto_lights(False)
a1_lock = threading.Lock()
a2_lock = threading.Lock()


async def poll_inputs():
    while True:

        with a1_lock:
            a1 = ah.analog.one.read()
        with a2_lock:
            a2 = ah.analog.two.read()

            if a1 > 3.0 and a2 > 3.0:
                send_status('ringing')
            elif 0.5 > a1 > 1.5 and 1.0 > a2 > 5.0:
                send_status('answered')

            send_hat_reads(a1, a2)

        time.sleep(0.25)


async def send_hat_reads(a1, a2):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://192.168.1.107:5100/websocket') as ws:
            await ws.send_json({'reads': [a1, a2]})


async def send_status(status):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('ws://192.168.1.107:5100/websocket') as ws:
            await ws.send_json({'status': status})


async def receive_commands():
    async with websockets.connect('ws://192.168.1.111:5000/receive_commands') as websocket:
        async for message in websocket:
            data = json.loads(message)
            command = data['rpi_command']
            if command == 'answer':
                ah.relay.one.on()
                ah.relay.two.on()
                await asyncio.sleep(0.3)
            elif command == 'open':
                ah.relay.three.on()
                await asyncio.sleep(0.2)
                ah.relay.three.off()
                await send_status('opened')
            elif command == 'hangup':
                ah.relay.one.off()
                ah.relay.two.off()
                await asyncio.sleep(0.3)
                await send_status('idle')


async def main():
    # Start all the asynchronous tasks
    tasks = [poll_inputs(), receive_commands()]
    await asyncio.gather(*tasks)

asyncio.run(main())




