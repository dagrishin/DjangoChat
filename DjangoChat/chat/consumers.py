import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404

from registration.models import User
from .models import Contact, Chat, Message




def get_user_contact(username):
    user = get_object_or_404(User, username=username)
    return get_object_or_404(Contact, user=user)


def get_current_chat(chatId):
    return get_object_or_404(Chat, id=int(chatId))
# data['from'] user
# data['chatId'] chat_id


class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("connected", event)

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # user = self.scope['user']
        # print('aaaaaaaaaa', self.room_name)
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        print("receive", event)
        front_text = event.get('text', None)
        # print(front_text)
        if front_text is not None:

            load_dict_data = json.loads(front_text)


            msg = load_dict_data.get('message')
            if load_dict_data.get('user_id'):
                # print(int(load_dict_data.get('user_id')))
                # print(Contact.objects.get(user_id=int(load_dict_data.get('user_id'))))
                user = await self.get_user(int(load_dict_data.get('user_id')))
                # print(user, 'jhdsjshdjdshjsdh')
            else:
                user = self.scope['user']
            username = 'default'
            if user.is_authenticated:
                username = user.username

            if not user.id:
                self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "chat_message",
                     "text": "error"
                     },
                )
            else:

                if load_dict_data.get('id'):
                    id = load_dict_data.get('id')
                    await self.update_chat_message(int(id), msg)

                else:
                    obj = await self.create_chat_message(user, msg, int(self.room_name))
                    id = obj.id

                myResponse = {
                    'message': msg,
                    'username': username,
                    'id': id,

                }

                # await self.create_chat_message(user, msg)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {   "type": "chat_message",
                        "text": json.dumps(myResponse)
                    },
                )
    async def chat_message(self, event):
        print("message", event)
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    async def websocket_disconnect(self, event):
        print("disconnected", event)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    # @database_sync_to_async
    # def get_thread(self, user, other_username):
    #     return Thread.objects.get_or_new(user, other_username)[0]

    @database_sync_to_async
    def get_user(self, id):
        return User.objects.get(id=id)

    @database_sync_to_async
    def create_chat_message(self, me, msg, chat_id):
        user_contact = get_user_contact(me)
        current_chat = get_current_chat(chat_id)

        if current_chat.participants.filter(user=me):

            message = Message.objects.create(
                contact=user_contact,
                content=msg)

            current_chat.messages.add(message)
            current_chat.save()

            return message

    @database_sync_to_async
    def update_chat_message(self, id, msg):
        update_message = Message.objects.filter(id=id)
        update_message.update(content=msg)

        return update_message