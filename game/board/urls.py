# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from game.board import views

urlpatterns = [
    url('^play/$', views.play, name='match'),
    url('^submit/$', views.submit, name='submit'),
]
