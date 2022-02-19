from django.db import models

# Create your models here.
from api.models import User


class ChatChannels(models.Model):
    CHAT_TYPE = [['normal', 'normal'],
                 ['no_reply', 'no_reply'],
                 ['auto', 'auto']]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sender')
    sender_dp = models.URLField()
    chat_type = models.CharField(max_length=8, choices=CHAT_TYPE)
    group = models.ManyToManyField(User, related_name='chat_group')
    chat_uid = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=225)
    created = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    MSG_TYPE = [['text', 'text'],
                ['interview', 'interview'],
                ['auto', 'auto']]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender')
    message = models.TextField()
    message_type = models.CharField(max_length=10, choices=MSG_TYPE)
    channel = models.ForeignKey(ChatChannels, on_delete=models.CASCADE, related_name='chat_channel')
    created = models.DateTimeField(auto_now_add=True)


class DMChatMessage(models.Model):
    chatid = models.CharField(max_length=255)
    # sender = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    seenby = models.TextField(null=True)

    def __str__(self):
        return self.chatid

    @property
    def last_10_message(self):
        return self.objects.order_by('-timestamp').all()[:10]
