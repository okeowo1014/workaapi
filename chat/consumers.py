# from channels.generic.websocket import JsonWebsocketConsumer
# class ChatConsumer(JsonWebsocketConsumer):
#     def connect(self):
#         self.accept()
#
#     def disconnect(self, code):
#         pass
#
#     def receive_json(self, content):
#         print(content)
#
#         self.send_json(content)
#
#

# chat/consumers.py
import json
from django.contrib.auth import get_user_model

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from api.models import Employee, Employer

user = get_user_model()

from .models import DMChatMessage


def get_chat_by_id():
    return DMChatMessage.objects.all()


class ChatConsumer(WebsocketConsumer):

    def message_to_json(self, data):
        return {
            'sender': data.sender,
            'command': 'new_message',
            'message': data.content,
            'timestamp': str(data.timestamp),
            'seenby': data.seenby
        }

    def messages_to_json(self, data):
        result = []
        for each in data:
            result.append(self.message_to_json(each))

        return result

    def preload_messages(self, data):
        room_name = data['room_name']
        messages = DMChatMessage.objects.filter(chatid=room_name).order_by('-timestamp').all()[:10]
        content = {
            'command': 'preloaded_messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        try:
            employee = Employee.objects.get(uid=data['sender'])
            sender = employee.user
        except:
            try:
                employer = Employer.objects.get(uid=data['chatid'])
                sender = employer.user
            except:
                pass
                # sender = user.objects(pk=1)
        message = DMChatMessage.objects.create(chatid=data['chatid'], sender=sender,
                                               content=data['message'])

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        self.send_chat_message(content)

    command = {
        'preload_message': preload_messages,
        'new_message': new_message
    }

    def connect(self):
        print(self.channel_layer.group_add)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        json_data = json.loads(text_data)
        self.command[json_data['command']](self, json_data)

    def send_chat_message(self, data):
        message = data['message']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
