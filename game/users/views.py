# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate

from django.contrib.auth.mixins import LoginRequiredMixin

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
    form = UserForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            u, created = User.objects.get_or_create(username=email)
            passwd = None
            if created:
                # new user
                passwd = User.objects.make_random_password()
                u.set_password(passwd)
                u.save()
            u = authenticate(username=email, password=passwd)
            if u is not None:
                login(request, u)
            return render(request, 'users/redirect.html')  # (reverse('board:match'))
    return render(request, 'users/start.html', {'form': form})
