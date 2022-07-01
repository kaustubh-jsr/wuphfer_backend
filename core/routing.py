from django.urls import re_path,path

from . import consumers

websocket_urlpatterns = [
    #  path('ws/notifications/<username>',consumers.NotificationConsumer.as_asgi()),
     path('ws/notifications',consumers.NotificationConsumer.as_asgi()),
    #  path('ws/notifications/',consumers.NotificationConsumer.as_asgi()),
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.NotificationConsumer.as_asgi()),
]