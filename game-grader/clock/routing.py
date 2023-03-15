# clock/routing.py
# from django.urls import re_path
# from . import consumers

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django_private_chat2 import urls

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            urls.websocket_urlpatterns
        )
    ),
})

# websocket_urlpatterns = [
#     re_path(r'ws/clock/(?P<room_name>\w+)/$', consumers.ClockConsumer.as_asgi()),
# ]
