from pprint import pprint
import asyncio

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

from chat.models import Chat, Contact


class ChatNotExist(Exception):
    def __init__(self, text):
        self.txt = text



@database_sync_to_async
def get_user(token_key):
    try:
        return Token.objects.get(key=token_key).user
    except Token.DoesNotExist:
        return AnonymousUser()
@database_sync_to_async
def get_in_chat(user, chat_id):
    participants = Chat.objects.get(id=chat_id).participants.all()
    if Contact.objects.get(user=user) in participants:
        return True
    else:
        return False





class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    see:
    https://channels.readthedocs.io/en/latest/topics/authentication.html#custom-authentication
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return TokenAuthMiddlewareInstance(scope, self)


class TokenAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        headers = dict(self.scope['headers'])
        if b'authorization' in headers:
            token, chat_id = token, chat_id = headers[b'authorization'].decode().split(',')
            token_name, token_key = token.split()
            if token_name == 'Token':
                self.scope['user'] = await get_user(token_key)
                chat_id = int(chat_id.split()[1])
                in_chat = await get_in_chat(self.scope['user'], chat_id)
                if not in_chat:
                    raise ChatNotExist(
                        "Chat does not exist"
                    )
        inner = self.inner(self.scope)
        return await inner(receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))