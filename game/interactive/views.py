import logging

from django.shortcuts import render
from django.db import transaction
from django.contrib.auth.decorators import login_required

from .models import Settings, Interactive, InteractiveRound


def new_interactive_game(game_settings, user):
    i = Interactive(constraints=game_settings)
    i.save()
    i.users.add(user)
    i.save()
    return i


# Create your views here.
@login_required(login_url='/')
def lobby(request):
    u = request.user.id

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
    # randomly ordered list of gamess that haven't started yet
    games = Interactive.objects.filter(started=False).order_by('?')

    if games:
        # finding a game for a player
        for game in games:

            if game.users.count() < game.constraints.max_users:
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
    return render(request, 'interactive/play.html')


@login_required(login_url='/')
def submit_answer(request):
    pass


@login_required(login_url='/')
def view_answers(request):
    pass
