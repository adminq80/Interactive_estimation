from django.conf.urls import url

from .views import assign, lobby, submit_answer, play,  view_answers, exit_survey

urlpatterns = [
    url(r'^$', assign),
    url(r'^lobby/$', lobby, name='lobby'),
    url(r'^play/$', play, name='play'),
    url(r'^submit', submit_answer, name='submit'),
    url(r'^view_answers', view_answers, name='view_answers'),
    url(r'^exit', exit_survey, name='exit'),
]
