from django.urls import path, re_path


from .views import ChatView, ChatAllView, CreateRoomView, ChatUpdate

app_name = 'chat'
urlpatterns = [
    path("", ChatAllView.as_view(), name='all'),
    path("create_room", CreateRoomView.as_view(), name='create_room'),
    path("update_room/<int:pk>/", ChatUpdate.as_view(), name='update_room'),
    re_path(r"^(?P<room_name>[\w.@+-]+)/$", ChatView.as_view(), name='room'),
]
