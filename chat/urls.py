from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')

urlpatterns = [
    path('', include(router.urls)),
     path('chat-test/', TemplateView.as_view(
        template_name='test_chat.html',
        content_type='text/html'
    )),
] 