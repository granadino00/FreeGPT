from django.db import models

from django.contrib.auth.models import User

from django.db import models

class Bot(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Nombre del bot")
    technical_name = models.CharField(max_length=100, unique=True, help_text="Nombre técnico para acceder al bot en Ollama")
    description = models.TextField(blank=True, help_text="Descripción del bot")
    version = models.CharField(max_length=50, blank=True, help_text="Versión del bot")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora de creación del bot")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha y hora de la última actualización del bot")

    def __str__(self):
        return self.name

class Conversation(models.Model):
    user = models.ForeignKey(User, related_name='conversations', on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, related_name='conversations_bot', on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=300, default="null")

    def __str__(self):
        return f"Conversation {self.id} with {self.user.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
