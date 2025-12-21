import requests
import logging
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AIChatSession, ChatInteraction
from .serializers import AIChatSessionSerializer, ChatInteractionSerializer, AIChatSessionDetailSerializer

logger = logging.getLogger(__name__)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'username': user.username}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CheckAuthView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
             return Response({'username': request.user.username, 'is_authenticated': True})
        return Response({'is_authenticated': False, 'username': None}, status=status.HTTP_200_OK)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        message = request.data.get('message')

        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or Create Session
        if session_id:
            try:
                # Ensure user owns the session and it is not deleted
                session = AIChatSession.objects.get(id=session_id, user=request.user, is_deleted=False)
            except AIChatSession.DoesNotExist:
                return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            session = AIChatSession.objects.create(user=request.user)
            # Initial temporary summary (can be updated by AI later)
            session.summary = f"New conversation started: {message[:30]}..."
            session.save()

        # Save User Interaction
        user_interaction = ChatInteraction.objects.create(
            session=session,
            is_user=True,
            message=message
        )

        # AI Response Logic
        ai_response_text = ""
        ai_summary = session.summary

        if settings.MOCK_AI_RESPONSE:
            ai_response_text = f"This is a mocked response to: '{message}'. The backend is running in mock mode."
            ai_summary = f"Summary updated for session {session.id} (Mock)"
        else:
            try:
                # Call External N8N Agent
                payload = {
                    'session_id': str(session.id),
                    'message': message,
                    # Add any other context needed
                }
                response = requests.post(settings.AI_AGENT_URL, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                ai_response_text = data.get('answer', 'No answer received.')
                ai_summary = data.get('summary', session.summary)

            except Exception as e:
                logger.error(f"Error calling AI Agent: {e}")
                ai_response_text = "Sorry, I am having trouble connecting to the AI brain right now."

        # Update Session Summary
        if ai_summary:
            session.summary = ai_summary
            session.save()

        # Save AI Interaction
        ai_interaction = ChatInteraction.objects.create(
            session=session,
            is_user=False,
            message=ai_response_text
        )

        return Response({
            'session_id': session.id,
            'summary': session.summary,
            'question_id': user_interaction.id,
            'answer_id': ai_interaction.id,
            'answer': ai_response_text
        })

class SessionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AIChatSessionSerializer

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user, is_deleted=False).order_by('-created_at')

class SessionDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AIChatSessionDetailSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user, is_deleted=False)

class DeleteSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            session = AIChatSession.objects.get(id=id, user=request.user)
            session.is_deleted = True
            session.save()
            return Response({'message': 'Session deleted'}, status=status.HTTP_200_OK)
        except AIChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

