from django.conf.urls import url


from .views import assign, lobby, exit_survey, done, instruction

urlpatterns = [
    url(r'^$', assign),
    url(r'^lobby/$', lobby, name='lobby'),
    url(r'^exit/$', exit_survey, name='exit'),
    url(r'^done/$', done, name='done'),
    url(r'^instruction/$', instruction, name='instruction'),
]
