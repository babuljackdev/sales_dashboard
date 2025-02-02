from django.urls import re_path
from . import consumers

ws_urls = [
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
] 