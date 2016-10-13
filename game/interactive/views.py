import logging
from random import choice

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone

from game.contrib.calculate import calculate_score
from game.contrib.random_user import random_user
from game.interactive.forms import RoundForm, ExitSurvey
from game.round.models import Plot
from .models import Settings, Interactive, InteractiveRound


def avatar(exclude=set()):
    avatars = {'bee.png', 'bird.png', 'cat.png', 'cow.png', 'elephant.png', 'lion.png', 'pig.png', 'cute_cat.png',
               'cute_panda.png', 'cute_giraffe.png', 'cute_owl.png', 'cute_cat_color.png', 'smart_dog.png',
               'smart_fox.png', 'smart_monkey.png', 'smart_deer.png'
               }
    return choice(list(avatars.symmetric_difference(exclude)))


def new_interactive_game(game_settings, user):
    i = Interactive(constraints=game_settings)
    i.save()
    i.users.add(user)
    i.save()
    user.avatar = avatar()
    user.save()
    return i


def assign(request):
    if request.method == 'POST':
        return redirect('interactive:lobby')
    return render(request, 'pages/home2.html')


# Create your views here.
def lobby(request):

    if request.user.is_anonymous:
        u, password = random_user('i')
        u = authenticate(username=u.username, password=password)
        login(request, u)
    else:
        u = request.user
        if u.game_type != 'i':
            return redirect('/')

    try:
        with transaction.atomic():
            Interactive.objects.get(users=u)
        return render(request, 'interactive/lobby.html')
    except Interactive.DoesNotExist:
        pass

    try:
        game_settings = Settings.objects.order_by('?')[0]  # pick game settings at random

    except Exception as e:
        logging.error('Lobby function: {}'.format(e))
        game_settings = Settings(max_users=5, min_users=0, max_influencers=3, min_influencers=0)
        game_settings.save()

    # look for a game that didn't start yet
    # randomly ordered list of games that haven't started yet
    games = Interactive.objects.filter(started=False).order_by('?')

    if games:
        # finding a game for a player
        for game in games:

            if game.users.count() < game.constraints.max_users:
                used_avatars = {i.avatar for i in game.users.all()}
                u.avatar = avatar(used_avatars)
                u.save()
                game.users.add(u)
                game.save()
                break

        else:  # else for the FOR loop
            # TODO: log this or raise
            # This is temp work around
            new_interactive_game(game_settings, u)

    else:
        new_interactive_game(game_settings, u)

    return render(request, 'interactive/lobby.html')


@login_required(login_url='/')
def play(request):
    u = request.user
    game = Interactive.objects.get(users=u)
    users = game.users.all()

    # round = InteractiveRound.objects.create(

    played_rounds = InteractiveRound.objects.filter(user=u)
    plot_pks = {i.plot.pk for i in played_rounds}

    score = calculate_score(played_rounds)
    currentRound = len(plot_pks)

    remaining = Plot.objects.count() - currentRound

    if remaining == 0:
        i = Interactive.objects.get(user=u)
        i.end_time = timezone.now()
        i.save()
        return redirect('interactive:exit_survey')

    if request.session.get('PLOT'):
        plot = Plot.objects.get(plot=request.session.get('PLOT'))
    else:
        plots = Plot.objects.exclude(pk__in=plot_pks)
        plot = choice(plots)

    request.session['PLOT'] = plot.plot
    form = RoundForm()

    return render(request, 'interactive/play.html', {'users': users,
                                                     'state': 'initial',
                                                     'round': plot,
                                                     'form': form,
                                                     'remaining': remaining,
                                                     'currentRound': currentRound
                                                     })


# @login_required(login_url='/')
# def instruction(request):
#     u = request.user
#     game = Interactive.objects.get(user=u)
#     game.instruction = True
#     game.save()

#     return render(request, 'interactive/instructions.html')

@login_required(login_url='/')
def submit_answer(request):
    pass


@login_required(login_url='/')
def view_answers(request):
    pass


@login_required(login_url='/')
def exit_survey(request):
    game = Interactive.objects.get(user=request.user)
    form = ExitSurvey(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.game = game
            instance.save()

    if game.end_time is None:
        game.end_time = timezone.now()
        game.save()
    return render(request, 'control/survey.html', {'form': form, 'score': request.user.get_score})
