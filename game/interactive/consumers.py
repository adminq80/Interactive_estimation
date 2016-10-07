import json
import logging
from random import choice
from decimal import Decimal

from functools import wraps

from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user

from game.round.models import Plot
from .models import Interactive, InteractiveRound


def get_round(game):
    users = game.users.all()
    played_rounds = InteractiveRound.objects.filter(user=users[0])

    plot_pks = {i.plot.pk for i in played_rounds}
    current_round = len(plot_pks)

    remaining = Plot.objects.count() - current_round

    if remaining == 0:
        return None

    plots = Plot.objects.exclude(pk__in=plot_pks)
    plot = choice(plots)
    for user in users.all():
        i_round = InteractiveRound(user=user, game=game, plot=plot, round_order=current_round, guess=Decimal(-10))
        i_round.save()
        if current_round == 0:
            # random initial game configuration
            following = users.exclude(username=user.username).order_by('?')[:game.constraints.max_following]  # random
            i_round.following = following
            i_round.save()

    return {'plot': plot.plot, 'remaining': remaining, 'current_round': current_round}


def user_and_game(message):

    user = message.user
    if user.is_authenticated:
        game = Interactive.objects.get(users=user)
    else:
        logging.error('User is anonymous and needs to login')
        raise Exception('User is Anonymous')
    return user, game


@channel_session_user_from_http
def lobby(message):

    user, game = user_and_game(message)
    if not user.is_authenticated or game is None:
        # redirect to login

        pass
    logging.info('user {} just entered {}'.format(user.username, game.group_channel))

    game.group_channel.add(message.reply_channel)

    logging.info("Channel NAME is {}".format(message.reply_channel.name))

    channel = game.user_channel(user)
    if channel:
        channel.add(message.reply_channel)
    else:
        logging.error("Couldn't create a user channel")
        raise Exception("Couldn't create user channel")

    users_count = game.users.count()
    waiting_for = game.constraints.max_users - users_count
    # TODO: add time to the condition
    if waiting_for == 0:
        # users = game.users.exclude(username=user.username)
        # l = [{'username': i.username, 'avatar': i.get_avatar} for i in users]
        round_ = get_round(game)
        game.group_channel.send({'text': json.dumps({
            'action': 'initial',
            # 'users': l,
            'plot': round_.get('plot'),
            'remaining': round_.get('remaining'),
            'current_round': round_.get('current_round'),
        })
        })
        return

    # TODO I think this should go to the lobby template .. only the variables are passed
    game.broadcast('info', 'There are currently a total of {} out of {} required participants waiting for the game to start.'.
                   format(game.users.count(), game.constraints.max_users - game.users.count()))


@channel_session_user
def exit_game(message):
    user, game = user_and_game(message)
    # logging.info('user {} just exited'.format(user.username))
    game.group_channel.discard(message.reply_channel)


def ws_receive(message):
    payload = json.loads(message['text'])
    action = payload.get('action')

    if action:
        payload['reply_channel'] = message.content['reply_channel']
        payload['path'] = message.content.get('path')
        Channel('game.route').send(payload)
    else:
        # TODO: unrecognized action
        logging.error('Unknown action {}'.format(action))


def channel_debugger(func):
    name = func.__name__

    @wraps(func)
    def inner(message, *args, **kwargs):
        print(name)
        logging.info(name)
        message.reply_channel.send({
            'text': json.dumps({
                'action': 'ping',
                'text': name,
            })
        })
        func(message, *args, **kwargs)

    return inner


@channel_session_user
@channel_debugger
def data_broadcast(message):
    user, game = user_and_game(message)
    print(user)
    print(game)
    pass


@channel_session_user
@channel_debugger
def follow_list(message):
    user, game = user_and_game(message)
    print(user)
    print(game)
    pass


@channel_session_user
@channel_debugger
def initial_submit(message):
    user, game = user_and_game(message)
    guess = message.get('guess')
    try:
        round_ = InteractiveRound.objects.get(user=user, guess=Decimal(-10))
        round_.guess = Decimal(guess)
        round_.save()
    except InteractiveRound.DoesNotExist:
        message.reply_channel.send({
            'text': json.dumps({
                'error': "User not found",
            })
        })

    remaining_users = InteractiveRound.objects.filter(game=game, guess=Decimal(-1))
    if remaining_users is None:
        # Interactive On
        game.group_channel.send({
            'text': json.dumps({
                'action': 'interactive'
            })
        })
        pass
    message.reply_channel.send({
        'text': json.dumps({
            'guess': guess,
            'status': 1,
        })
    })


@channel_session_user
@channel_debugger
def interactive_submit(message):
    user, game = user_and_game(message)
    # round_ = InteractiveRound.objects.filter()