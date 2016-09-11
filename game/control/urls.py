from django.conf.urls import url

from .views import play

urlpatterns = [
    url('^play/$', play, name='play'),
]
