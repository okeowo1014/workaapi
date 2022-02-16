from django.urls import path

from chat.views import get_my_channels, read_chats, index, room

app_name = 'chat'
urlpatterns = [
    path('get_my_channels/', get_my_channels, name='get_my_channels'),
    path('read_chats/<str:chat_uid>', read_chats, name='read_chats'),
    path('', index, name='index', ),
    path('<str:room_name>/<str:username>/', room, name='room')

]
