# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse

from django.http import Http404
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User, UserTypes


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


def start(request):

    if request.user.is_authenticated:
        print("User is authenticated")
        c = request.user.game_type
    else:
        choices = UserTypes.objects.all()[0]
        types = choices.types.split(',')
        t = types.pop(0)
        d = {
            '0': 'control',
            '1': 'static',
            '2': 'dynamic',
        }
        c = d[t]
        choices.types = ','.join(types)
        choices.save()

    if c == 'dynamic':
        return redirect('dynamic_mode:lobby')
    elif c == 'control':
        return redirect('control:play')
    elif c == 'static':
        return redirect('static_mode:lobby')
    else:
        raise Http404('{} not implemented'.format(c))
