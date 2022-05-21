from django.contrib import admin

# Register your models here.
from chat.models import ChatChannels, ChatMessage, DMChatMessage

admin.site.register(ChatChannels)
admin.site.register(ChatMessage)
admin.site.register(DMChatMessage)
