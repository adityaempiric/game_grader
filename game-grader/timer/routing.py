from django.urls import path

from timer import consumers

websocket_urlpatterns = [
    path('timer/<int:id>/', consumers.ChatConsumer.as_asgi()),
]