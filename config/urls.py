# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from game.users.views import user_logout


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include('game.users.urls', namespace='users')),
    # url(r'^accounts/', include('allauth.urls')),
    url(r'^logout/$', user_logout, name='account_logout'),
    # Your stuff: custom urls includes go here
    # url(r'start/', include('game.player.urls')),
    # url(r'^board/', include('game.board.urls', namespace='board')),

    url(r'^done/$', TemplateView.as_view(template_name='pages/done.html')),

    url(r'^solo/', include('game.control.urls', namespace='control')),
    url(r'^dynamic_mode/', include('game.interactive_shocks.urls', namespace='dynamic_mode')),
    url(r'^static_mode/', include('game.interactive_static.urls', namespace='static_mode')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
