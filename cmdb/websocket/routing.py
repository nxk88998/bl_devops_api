from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import re_path
from cmdb.websocket.terminal import SSHConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            re_path(r'^server/terminal/(?P<ssh_ip>.*)/(?P<ssh_port>\d+)/(?P<credential_id>\d+)/', SSHConsumer.as_asgi()),
        ])
    ),
})
