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

    print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCC == {}".format(c))
    if c == 'i':
        return redirect('interactive:lobby')
    elif c == 'c':
        return redirect('control:play')
    else:
        raise Http404('{} not implemented'.format(c))


# def start(request):
#     form = UserForm(request.POST or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             try:
#                 with transaction.atomic():
#                     u = User(username=email, game_type=choice(['i', 'c']))
#                     u.save()
#             except IntegrityError:
#                 with transaction.atomic():
#                     u = User(username=email+'.old', game_type=choice(['i', 'c']))
#                     u.save()
#             passwd = None
#
#             passwd = User.objects.make_random_password()
#             u.set_password(passwd)
#             u.save()
#
#             datatuple = (
#                 ('Interactive estimation Game', 'Your username is {} and your password is {}'.format(
#                     u.username, passwd), 'admin@game.acubed.me', [u.username]),
#                 ('Interactive estimation Game', 'Your username is {} and your password is {}'.format(
#                     u.username, passwd), 'admin@game.acubed.me', ['adminq80@gmail.com'])
#             )
#             send_mass_mail(datatuple=datatuple)
#
#             u = authenticate(username=email, password=passwd)
#             if u is not None:
#                 login(request, u)
#                 if u.game_type == 'i':
#                     # Interactive game
#                     return redirect(reverse('interactive:lobby'))
#                 elif u.game_type == 'c':
#                     Control.objects.create(user=u).save()
#                     return redirect(reverse('control:play'))
#                 raise Exception('User must be either Control or Interactive')
#     return render(request, 'users/start.html', {'form': form})

#
# @login_required(login_url='/')
# def done(request):
#     c = Control.objects.get(user=request.user)
#     return render(request, 'users/done.html', {'score': c.score})
