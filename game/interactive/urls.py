from django.conf.urls import url

from .views import lobby, submit_answer, play,  view_answers

urlpatterns = [
    url(r'^lobby/$', lobby, name='lobby'),
    url(r'^play/$', play, name='play'),
    url(r'^submit', submit_answer, name='submit'),
    url(r'^view_answers', view_answers, name='view_answers'),

]
