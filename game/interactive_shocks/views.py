from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from game.users.models import User
from game.contrib.random_user import random_user

from .forms import ExitSurvey
from .models import InteractiveShocks


def assign(request):
    if request.method == 'POST':
        return redirect('interactive_shocks:instruction')
    return render(request, 'pages/home2.html')


# Create your views here.
@login_required(login_url='interactive_shocks:instruction')
def lobby(request):
    if cache.get('interactive_instruction_{}'.format(request.user.id)):
        return render(request, 'interactive_shocks/lobby.html')
    return redirect('interactive_shocks:instruction')


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
    if request.method == 'POST':
        if form.is_valid():
            u = User.objects.get(username=request.user.username)
            game = InteractiveShocks.objects.get(users=u)
            instance = form.save(commit=False)
            instance.username = u.username
            instance.game = game.id
            instance.save()
            return redirect('interactive_shocks:done')
        else:
            print('NOT Valid')
    return render(request, 'control/survey.html', {'form': form, 'score': request.user.get_score})


def done(request):
    return render(request, 'interactive_shocks/done.html')


def instruction(request):
    if request.user.is_anonymous:
        u, password = random_user('shocks')
        u = authenticate(username=u.username, password=password)
        login(request, u)
        cache.set('interactive_instruction_{}'.format(u.id), False)
    else:
        u = request.user
        if u.game_type != 'shocks':
            return redirect('/')
    if request.method == 'POST':
        cache.set('interactive_instruction_{}'.format(u.id), True)
        return redirect('interactive_shocks:lobby')
    return render(request, 'interactive_shocks/instructions.html')
