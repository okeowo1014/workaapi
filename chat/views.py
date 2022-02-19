from django.shortcuts import render
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.extractor import generate_chat_key
from api.models import Employee, Employer
from chat.models import ChatChannels, ChatMessage, DMChatMessage
from chat.serializers import ChatChannelSerializer, ChatMessageSerializer
from notifier.views import interview_invitation_notifier


def get_user(uid):
    employee = Employee.objects.get(uid=uid)
    return employee.user


def get_sender_dp(request):
    if request.user.account_type == 'employee':
        userobj = Employee.objects.get(user=request.user)
        dp = userobj.display_picture
    elif request.user.account_type == 'employer':
        userobj = Employer.objects.get(user=request.user)
        dp = userobj.company_logo
    return dp


class CreateMessageChannel:
    def __init__(self, request, group, name):
        self.request = request
        self.sender = self.request.user
        self.name = name
        self.chat_uid = generate_chat_key()
        self.group = [get_user(uid) for uid in group]
        self.channel = ChatChannels(sender=self.sender, chat_type='no_reply', sender_dp=get_sender_dp(self.request),
                                    chat_uid=self.chat_uid, name=self.name)
        self.channel.save()
        for each in self.group:
            self.channel.group.add(each)

    def push_text_message(self, text):
        ChatMessage.objects.create(sender=self.sender, message_type='text', message=text, channel=self.channel)

    def push_interview_link(self, link):
        ChatMessage.objects.create(sender=self.sender, message_type='interview', message=link, channel=self.channel)

    def push_shortlist_message(self):
        text = """ Hello!
                you have been shortlisted fot this job, 
                Get prepared for interview.
                Wish you best of luck.
                """
        ChatMessage.objects.create(sender=self.sender, message_type='text', message=text, channel=self.channel)


class GetMessageChannel:
    def __init__(self, chat_id):
        self.channel = ChatChannels.objects.get(chat_uid=chat_id)
        self.sender = self.channel.sender
        self.group = self.channel.group.all()

    def push_text_message(self, text):
        ChatMessage.objects.create(sender=self.sender, message_type='text', message=text, channel=self.channel)

    def push_interview_alert(self, text, company):
        interview_invitation_notifier(self.group, text, company)
        ChatMessage.objects.create(sender=self.sender, message_type='text', message=text, channel=self.channel)

    def push_interview_link(self, link):
        ChatMessage.objects.create(sender=self.sender, message_type='interview', message=link, channel=self.channel)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_channels(request):
    my_channels = ChatChannels.objects.filter(group=request.user)
    serializer = ChatChannelSerializer(my_channels, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def read_chats(request, chat_uid):
    channel = ChatChannels.objects.get(chat_uid=chat_uid)
    serializer = ChatMessageSerializer(channel, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Create your views here.
def index(request):
    print('hi')
    DMChatMessage.objects.all().delete()
    return render(request, 'chat/index.html')


def room(request, room_name, username):
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'username': username
    })
