from django.urls import path, re_path
from .views import ChatsView, ChatView

app_name = 'chatAPI'
urlpatterns = [
    path('chats/', ChatsView.as_view()),
    path('chat/', ChatView.as_view())
]
