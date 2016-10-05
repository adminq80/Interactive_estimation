from django.conf.urls import url


from .views import submit_answer, play
from .views import instruction, exit_survey


urlpatterns = [
    url(r'^play/$', play, name='play'),
    url(r'^submit/$', submit_answer, name='submit'),
    url(r'^instruction/$', instruction, name='instruction'),
    url(r'^exit/$', exit_survey, name='exit_survey'),
]
