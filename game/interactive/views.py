from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from game.users.models import User
from game.contrib.random_user import random_user
from game.interactive.forms import ExitSurvey

from .models import Interactive


def assign(request):
    if request.method == 'POST':
        return redirect('interactive:instruction')
    return render(request, 'pages/home2.html')


# Create your views here.
@login_required(login_url='interactive:instruction')
def lobby(request):
    if cache.get('interactive_instruction_{}'.format(request.user.id)):
        return render(request, 'interactive/lobby.html')
    return redirect('interactive:instruction')


@login_required(login_url='/')
def exit_survey(request):
    form = ExitSurvey(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            u = User.objects.get(username=request.user.username)
            game = Interactive.objects.get(users=u)
            instance = form.save(commit=False)
            instance.username = u.username
            # instance.user.add(request.user)
            instance.game = game
            instance.save()
            return redirect('interactive:done')
        else:
            print('NOT Valid')
    return render(request, 'control/survey.html', {'form': form, 'score': request.user.get_score})


def done(request):
    return render(request, 'interactive/done.html')


def instruction(request):
    if request.user.is_anonymous:
        u, password = random_user('i')
        u = authenticate(username=u.username, password=password)
        login(request, u)
        cache.set('interactive_instruction_{}'.format(u.id), False)
    else:
        u = request.user
        if u.game_type != 'i':
            return redirect('/')
    if request.method == 'POST':
        cache.set('interactive_instruction_{}'.format(u.id), True)
        return redirect('interactive:lobby')
    render(request, 'interactive/instructions.html')
    cache.set('interactive_instruction_{}'.format(u.id), True)
    return redirect('interactive:lobby')
    # return render(request, 'interactive/instructions.html')
