from django.conf.urls import url

from .views import submit_answer, play

urlpatterns = [
    url('^play/$', play, name='play'),
    url('^submit/$', submit_answer, name='submit'),

]
