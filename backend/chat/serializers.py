from rest_framework import serializers
from .models import AIChatSession, ChatInteraction

class ChatInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatInteraction
        fields = ['id', 'is_user', 'message', 'timestamp']

class AIChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatSession
        fields = ['id', 'created_at', 'summary']

class AIChatSessionDetailSerializer(serializers.ModelSerializer):
    interactions = ChatInteractionSerializer(many=True, read_only=True)

    class Meta:
        model = AIChatSession
        fields = ['id', 'created_at', 'summary', 'interactions']
