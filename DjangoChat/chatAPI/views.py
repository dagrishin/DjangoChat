from pprint import pprint

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Chat, Contact
from chatAPI.serializers import ChatAllSerializer, ChatSerializer, MessagePostSerializer


class ChatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        user = request._user
        contact = Contact.objects.get(user=user)
        chats = Chat.objects.filter(participants=contact)
        serializer = ChatAllSerializer(chats, many=True)
        return Response(serializer.data)


class ChatView(APIView):

    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request):
        chat_id = request.GET.get("chat")
        chat = Chat.objects.filter(id=int(chat_id))
        print(chat)
        serializer = ChatSerializer(chat, many=True)
        return Response(serializer.data)

    def post(self, request):
        chat_id = request.data.get('chat')
        # print(request.data)
        # contact_id = request.data.get('contact')
        # content = request.data.get('content')
        # contact = Contact.objects.get(id=int(contact_id))
        message = MessagePostSerializer(data=request.data)
        print(message, message.is_valid())
        if message.is_valid():
            message = message.save()

            Chat.objects.get(id=int(chat_id)).messages.add(message)
            return Response(status=201)
        else:
            return Response(status=400)
