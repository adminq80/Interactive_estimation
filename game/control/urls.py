from django.conf.urls import url


from .views import assign, submit_answer, play
from .views import check, instruction, exit_survey


urlpatterns = [
    url(r'^play/$', play, name='play'),
    url(r'^submit/$', submit_answer, name='submit'),
    url(r'^instruction/$', instruction, name='instruction'),
    url(r'^check/$', check, name='check'),
    url(r'^exit/$', exit_survey, name='exit'),
    url(r'^$', assign),
]
