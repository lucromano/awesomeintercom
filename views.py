from aiohttp import web, ClientSession


class SendCommandView(web.View):
    async def post(self):
        data = await self.request.json()
        command = data['rpi_command']
        print(command)
        rpi_url = "http://192.168.1.111:5000/rpi_command"
        async with ClientSession() as session:
            async with session.post(rpi_url, json={'rpi_command': command}) as response:
                if response.status == 200:
                    return web.json_response({'message': 'command send success'})
                else:
                    return web.json_response({'message': 'command send error'})
