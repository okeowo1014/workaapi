from rest_framework import serializers

from chat.models import ChatChannels, ChatMessage

class ChatChannelMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['message', 'created']

class ChatChannelSerializer(serializers.ModelSerializer):
    chat_channel = serializers.SerializerMethodField()

    def get_chat_channel(self, obj):
        return ChatChannelMessageSerializer(
            instance=obj.chat_channel.order_by('-created')[:1],
            many=True
        ).data

    class Meta:
        model = ChatChannels
        fields = ['name', 'sender_dp', 'chat_type', 'chat_uid', 'chat_channel']


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['message', 'message_type', 'created']


class ChatMessageSerializer(serializers.ModelSerializer):
    chat_channel = ChatSerializer(read_only=True, many=True)

    class Meta:
        model = ChatChannels
        fields = ['chat_channel', 'sender_dp', 'name']
