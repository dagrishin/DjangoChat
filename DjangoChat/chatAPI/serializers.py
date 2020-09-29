from rest_framework import serializers

from chat.models import Contact, Message, Chat
from registration.models import User, Interest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class InterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = ("id", "name")


class ContactSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    friends = UserSerializer(many=True)
    interests = InterestSerializer(many=True)

    class Meta:
        model = Contact
        fields = ("id", "user", "friends", "interests")


class ChatAllSerializer(serializers.ModelSerializer):
    author = ContactSerializer()
    participants = ContactSerializer(many=True)

    class Meta:
        model = Chat
        fields = ("id", "author", "title", "participants")


class MessageSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = Message
        fields = ("id", "contact", "content", "timestamp")


class ChatSerializer(serializers.ModelSerializer):
    author = ContactSerializer()
    participants = ContactSerializer(many=True)
    messages = MessageSerializer(many=True)

    class Meta:
        model = Chat
        fields = ("id", "author", "title", "participants", "messages")


class MessagePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ("contact", "content")


