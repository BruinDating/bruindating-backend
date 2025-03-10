from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
# from . import views  # Import your new views

app_name = 'chat'

urlpatterns = [
    path('', TemplateView.as_view(template_name='test_chat.html'), name='chat'),
    
    path("admin/", admin.site.urls),
    
    # Authentication routes from pre-prod-dev
    path("auth/", include("auth_app.urls")),
    
    # Chat app routes from local_chat
    path("chat/", include("chat.urls")),
] 

# urlpatterns = [
#     path('', views.chat_home, name='chat'),  # Replace TemplateView with a real view
# ]