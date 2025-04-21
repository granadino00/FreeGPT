from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Conversation, Message, Bot
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from ollama import chat, ChatResponse, Client

client = Client(host='http://localhost:11434')

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

@csrf_exempt
@require_POST
def create_conversation_view(request):
    if request.user:
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON payload")

        model_id = payload.get("model_id")
        model_name = payload.get("model_name")
        user_message = payload.get("message")

        # Validaciones
        if not all([model_name, user_message, model_id]):
            return HttpResponseBadRequest("model_name, message, and conversation_id are required")

        convo = Conversation.objects.create(user=request.user, bot=model_id, title="null")

        # 3. Generar título
        prompt = f"Give me the title for the following text: {user_message}"
        try:
            title_response = client.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        # 4. Actualizar título
        convo.title = title_response
        convo.save()

        # 6. Respuesta
        return JsonResponse({
            "conversation_id": convo.id,
            "title": convo.title,
        })

@csrf_exempt
@require_POST
def message_conversation_view(request):
    """
    Maneja el envío de mensajes en una conversación existente.
    Recibe JSON con:
      - model_name: nombre del modelo en Ollama
      - message: texto del usuario
      - conversation_id: ID de la conversación existente
    Flujo:
      1. Validar y obtener Conversation.
      2. Guardar Message del usuario.
      3. Enviar a Ollama el mensaje original.
      4. Guardar Message del bot con la respuesta.
      5. Devolver JSON con conversation_id y bot_reply.
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON payload")

    model_name = payload.get("model_name")
    user_message = payload.get("message")
    conversation_id = payload.get("conversation_id")

    # Validaciones
    if not all([model_name, user_message, conversation_id]):
        return HttpResponseBadRequest("model_name, message, and conversation_id are required")

    convo = get_object_or_404(Conversation, id=conversation_id)

    # 1. Guardar mensaje del usuario
    Message.objects.create(
        conversation=convo,
        sender='user',
        content=user_message
    )

    # 2. Enviar a Ollama
    try:
        bot_response = client.chat(model=model_name, messages=[{"role": "user", "content": user_message}])
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    # 3. Guardar respuesta del bot
    Message.objects.create(
        conversation=convo,
        sender='bot',
        content=bot_response
    )

    # 4. Respuesta al cliente
    return JsonResponse({
        "conversation_id": convo.id,
        "bot_reply": bot_response
    })

# urls.py
# from django.urls import path
# from .views import create_conversation_view, message_conversation_view
# urlpatterns = [
#     path('api/ollama/create/', create_conversation_view, name='ollama_create'),
#     path('api/ollama/message/', message_conversation_view, name='ollama_message'),
# ]
