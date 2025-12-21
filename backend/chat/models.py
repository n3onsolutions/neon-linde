import uuid
from django.db import models

from django.contrib.auth.models import User

class AIChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True, help_text="AI generated summary of the conversation")
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.id} - {self.created_at}"

class ChatInteraction(models.Model):
    session = models.ForeignKey(AIChatSession, related_name='interactions', on_delete=models.CASCADE)
    is_user = models.BooleanField(default=True, help_text="True if message is from user, False if from AI")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.session.id} by {'User' if self.is_user else 'AI'}"
