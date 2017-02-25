from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from game.users.models import User
from game.contrib.random_user import random_user

from .forms import ExitSurvey, CheckForm
from .models import InteractiveStatic, Settings


def assign(request):
    if request.method == 'POST':
        return redirect('static_mode:instruction')
    return render(request, 'pages/home2.html')


# Create your views here.
@login_required(login_url='static_mode:instruction')
def lobby(request):
    if cache.get('interactive_static_instruction_{}'.format(request.user.id)):
        return render(request, 'interactive_static/lobby.html')
    return redirect('static_mode:instruction')


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
            game = InteractiveStatic.objects.get(users=u)
            instance = form.save(commit=False)
            instance.username = u.username
            instance.game = game.id
            instance.save()
            return redirect('static_mode:done')
        else:
            print('NOT Valid')
    return render(request, 'control/survey.html', {'form': form, 'score': round(request.user.get_score * .2, 2)})


def done(request):
    return render(request, 'static/done.html')


def instruction(request):
    form = CheckForm(request.POST or None)
    if request.user.is_anonymous:
        u, password = random_user('static')
        u = authenticate(username=u.username, password=password)
        login(request, u)
        cache.set('interactive_static_instruction_{}'.format(u.id), False)
    else:
        u = request.user
        if u.game_type != 'static':
            return redirect('/')
    if request.method == 'POST':
        if form.is_valid():
            cache.set('interactive_static_instruction_{}'.format(u.id), True)
            return redirect('static_mode:lobby')
    game_settings = Settings.objects.order_by('?')[0]
    cache.set('interactive_static_instruction_{}'.format(u.id), True)
    return render(request, 'interactive_static/instructions.html', {'players_num': game_settings.max_users,
                                                             'rounds_num': game_settings.max_rounds,
                                                             'following_num': game_settings.max_following,
                                                             'form': form,
                                                             })
