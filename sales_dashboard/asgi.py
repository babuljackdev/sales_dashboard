import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_dashboard.settings')
django.setup()

def get_application():
    from dashboard.routing import ws_urls  # Import here to delay import

    return ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    ws_urls
                )
            )
        ),
    })

application = get_application()

