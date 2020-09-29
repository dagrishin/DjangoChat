import json
import asyncio
from threading import Thread

import websockets
from websockets import InvalidStatusCode


def send(chat_id, message, token):

    async def send_message_def(chat_id, message, token):
        print(chat_id, message, token)

        uri = f"ws://127.0.0.1:8000/chat/{chat_id}/"
        try:
            async with websockets.connect(uri, extra_headers={'authorization': f'Token {token}, chat_id {chat_id}'}) as websocket:

                message = json.dumps({
                        'message': f"{message}",
                        'id': ''
                    })

                await websocket.send(message)
                # print(f"> {message}")

                greeting = await websocket.recv()
                print('asa', greeting)
                return greeting
        except InvalidStatusCode:
            pass

    asyncio.get_event_loop().run_until_complete(send_message_def(chat_id, message, token))
    # asyncio.get_event_loop().run_forever()

def start_listening(incoming_message_callback, chat_id, token, username):
    Thread(target=listen, args=(incoming_message_callback, chat_id, token, username), daemon=True).start()

def listen(incoming_message, chat_id, token, username):

    async def send_message_def(incoming_message, chat_id, token, username):
        # print(chat_id, message, token)

        uri = f"ws://127.0.0.1:8000/chat/{chat_id}/"
        try:
            async with websockets.connect(uri, extra_headers={'authorization': f'Token {token}, chat_id {chat_id}'}) as websocket:
                # if message:
                #     message = json.dumps({
                #             'message': f"{message}",
                #             'id': ''
                #         })
                #
                #     await websocket.send(message)
                # # print(f"> {message}")
                while True:
                    if not websocket.open:
                        try:
                            websocket = await websockets.connect(uri, extra_headers={'authorization': f'Token {token}, chat_id {chat_id}'})
                        except:
                            pass
                    else:
                        try:
                            greeting = await websocket.recv()
                            greeting = json.loads(greeting)
                            if greeting['username'] != username:
                                incoming_message(greeting['username'], greeting['message'])
                        except:
                            try:
                                websocket = await websockets.connect(uri, extra_headers={
                                    'authorization': f'Token {token}, chat_id {chat_id}'})
                            except:
                                pass
        except InvalidStatusCode:
            pass

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(send_message_def(incoming_message, chat_id, token, username))




