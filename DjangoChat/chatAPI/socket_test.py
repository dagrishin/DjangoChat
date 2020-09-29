import asyncio
import websockets
import json

from websockets import InvalidStatusCode


async def hello():
    uri = "ws://127.0.0.1:8000/chat/29/"
    try:
        async with websockets.connect(uri, extra_headers={'authorization': 'Token 46f9b0ac29def45f5eb5069abdef082572204ac1, chat_id 29'}) as websocket:
            message = json.dumps({
                    'message': "hello world",
                    'id': ''
                })
            await websocket.send(message)
            print(f"> {message}")

            greeting = await websocket.recv()
            print(f"< {greeting}")
    except InvalidStatusCode:
        pass

asyncio.get_event_loop().run_until_complete(hello())