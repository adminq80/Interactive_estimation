from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from game.users.models import User
from game.contrib.random_user import random_user

from .forms import ExitSurvey, CheckForm
from .models import InteractiveShocks, Settings


def assign(request):
    if request.method == 'POST':
        return redirect('dynamic_mode:instruction')
    return render(request, 'pages/home2.html')


# Create your views here.
@login_required(login_url='dynamic_mode:instruction')
def lobby(request):
    if cache.get('interactive_dynamic_instruction_{}'.format(request.user.id)):
        return render(request, 'interactive_shocks/lobby.html')
    return redirect('dynamic_mode:instruction')


@login_required(login_url='/')
def exit_survey(request):
    """
    username = models.CharField(max_length=255, blank=True, null=True)
    game = models.OneToOneField(Interactive)
    age = models.PositiveSmallIntegerField(null=True)
    gender = models.CharField(max_length=10, choices=(('m', 'Male'),
                                                      ('f', 'Female'),
                                                      ), blank=True, null=True)
    feedback = models.TextField(null=True)
    :param request:
    :return:
    """
    form = ExitSurvey(request.POST or None)
    u = User.objects.get(username=request.user.username)
    u.exited = True
    u.save()
    if request.method == 'POST':
        if form.is_valid():
            try:
                game = InteractiveShocks.objects.get(users=u)
                game_id = game.id
            except InteractiveShocks.DoesNotExist:
                game_id = -1
            instance = form.save(commit=False)
            instance.username = u.username
            instance.game = game_id
            instance.save()
            return redirect('dynamic_mode:done')
        else:
            print('NOT Valid')
    return render(request, 'control/survey.html', {'form': form, 'score': round(request.user.get_score * .375, 2)})


def done(request):
    return render(request, 'interactive_shocks/done.html')

import socket

def instruction(request):
    form = CheckForm(request.POST or None)
    if request.user.is_anonymous:
        u, password = random_user('dynamic')
        u = authenticate(username=u.username, password=password)
        login(request, u)
        cache.set('interactive_dynamic_instruction_{}'.format(u.id), False)
    else:
        u = request.user
        if u.game_type != 'dynamic':
            return redirect('/')
    if request.method == 'POST':
        if form.is_valid():
            cache.set('interactive_dynamic_instruction_{}'.format(u.id), True)
            return redirect('dynamic_mode:lobby')
    game_settings = Settings.objects.order_by('?')[0]
    cache.set('interactive_dynamic_instruction_{}'.format(u.id), True)

    return render(request, 'interactive_shocks/instructions.html', {'players_num': game_settings.max_users,
                                                                    'rounds_num': game_settings.max_rounds,
                                                                    'following_num': game_settings.max_following,
                                                                    'form': form,
                                                                    'host': socket.gethostname(),
                                                                    })
