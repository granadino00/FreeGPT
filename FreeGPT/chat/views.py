from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Conversation, Message

class ChatView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = '../templates/chat/chatview.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        # Obtiene las conversaciones del usuario autenticado
        return Conversation.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation_id = self.kwargs.get('conversation_id')
        if conversation_id:
            # Obtiene la conversación seleccionada y sus mensajes
            conversation = get_object_or_404(Conversation, id=conversation_id)
            messages = Message.objects.filter(conversation=conversation)
            context.update({
                'selected_conversation': conversation,
                'messages': messages,
            })
            return context
          
    # def post(self, request, *args, **kwargs):
    #     conversation_id = self.kwargs.get('conversation_id')
    #     if conversation_id:
    #           conversation = Conversation.objects.filter(user = self.request.user)