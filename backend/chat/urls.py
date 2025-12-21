from django.urls import path
from .views import ChatView, SessionListView, SessionDetailView, LoginView, LogoutView, CheckAuthView, DeleteSessionView

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
    path('sessions/', SessionListView.as_view(), name='session-list'),
    path('sessions/<uuid:id>/', SessionDetailView.as_view(), name='session-detail'),
    path('sessions/<uuid:id>/delete/', DeleteSessionView.as_view(), name='session-delete'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('check-auth/', CheckAuthView.as_view(), name='check-auth'),
]
