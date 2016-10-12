# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from random import choice

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db import transaction
from django.http import Http404
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.mail import send_mass_mail

from game.interactive.models import Interactive
from game.control.models import Control

from .models import User
from .forms import UserForm


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

    c = choice(['i', 'c'])

    if request.user.is_authenticated:
        print("User is authenticated")
        c = request.user.game_type

    if c == 'i':
        return redirect('interactive:lobby')
    elif c == 'c':
        return redirect('control:play')
    else:
        raise Http404('{} not implemented'.format(c))
