import json
import logging
from random import choice
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse

from channels import Channel
from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user
from twisted.internet import task, reactor


from game.round.models import Plot

from .utils import avatar
from .models import Interactive, InteractiveRound, Settings


def get_round(game, user=None):
    # reactor.callLater(seconds, func, *args)
    users = game.users.all()
    if not user:
        user = users[0]
    played_rounds = InteractiveRound.objects.filter(user=user, game=game)

    plot_pks = {i.plot.pk for i in played_rounds}
    current_round = len(plot_pks)

    remaining = Plot.objects.count() - current_round
    print('current_round ======================== {}'.format(current_round))
    if remaining == 0:
        return None

    plots = Plot.objects.exclude(pk__in=plot_pks)
    plot = choice(plots)
    for user in users.all():
        cache.set(user.username, json.dumps({
            'game': game.id,
            'current_round': current_round,
            'plot': plot.plot,
            'remaining': remaining,
        }))
        try:
            i_round = InteractiveRound(user=user, game=game, plot=plot, round_order=current_round, guess=Decimal(-3),
                                       influenced_guess=Decimal(-3))
            i_round.save()
        except InteractiveRound.IntegrityError:
            round = InteractiveRound.objects.get(user=user, game=game, plot=plot, round_order=current_round,
                                                 guess=Decimal(-3), influenced_guess=Decimal(-3))
            return {'plot': round.plot.plot, 'current_round': round.round_order, 'remaining': remaining}

        if current_round == 0:
            # random initial game configuration
            following = users.exclude(username=user.username).order_by('?')[:game.constraints.max_following]  # random
            print(user)
            for f in following.all():
                print('Going to follow {}'.format(f.username))
                i_round.following.add(f)
            i_round.save()
        else:
            previous_round = InteractiveRound.objects.get(user=user, game=game, round_order=current_round-1)
            for f in previous_round.following.all():
                i_round.following.add(f)
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


def send_user_avatar(game, user):
    Group(game.user_channel(user)).send({
        'text':
            json.dumps({
                'action': 'avatar',
                'url': '/static/{}'.format(user.get_avatar),
            })
    })


def send_game_status(game):
    game.broadcast(action='info', connected_players=game.users.count(), total_players=game.constraints.max_users)


@channel_session_user_from_http
def lobby(message):
    user = message.user

    if not user.is_authenticated:
        return redirect('/')

    try:
        game_settings = Settings.objects.order_by('?')[0]
    except Settings.DoesNotExist:
        game_settings, _ = Settings.objects.get_or_create(max_users=5, min_users=0, max_following=2, min_following=0)

    try:
        with transaction.atomic():
            game = Interactive.objects.get(users=user)
    except Interactive.DoesNotExist:
        game = None

    if game:
        # user has already been assigned to a game
        # todo: connect him to the game
        game.group_channel.add(message.reply_channel)
        Group(game.user_channel(user)).add(message.reply_channel)
        send_user_avatar(game, user)
        send_game_status(game)
        return

    games = Interactive.objects.filter(started=False).order_by('?')

    if games:
        for game in games:
            if game.users.count() < game.constraints.max_users:
                used_avatars = {i.avatar for i in game.users.all()}
                user.avatar = avatar(used_avatars)
                user.save()
                game.users.add(user)
                game.save()
                break
    else:
        game = Interactive(constraints=game_settings)
        game.save()
        game.users.add(user)
        game.save()
        user.avatar = avatar()
        user.save()

    game.group_channel.add(message.reply_channel)
    Group(game.user_channel(user)).add(message.reply_channel)

    send_user_avatar(game, user)

    users_count = game.users.count()
    waiting_for = game.constraints.max_users - users_count

    # TODO: add time to the condition
    if waiting_for == 0:
        game.started = True
        game.save()
        round_ = get_round(game)
        task.deferLater(reactor, 5, foo, game)
        game.broadcast(action='initial', plot=round_.get('plot'), remaining=round_.get('remaining'),
                       current_round=round_.get('current_round'))
    else:
        send_game_status(game)
    return


@channel_session_user
def exit_game(message):
    user, game = user_and_game(message)
    logging.info('user {} just exited'.format(user.username))
    if not game.started:
        game.users.remove(user)
        game.save()
    game.group_channel.discard(message.reply_channel)
    Group(game.user_channel(user)).discard(message.reply_channel)
    send_game_status(game)


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


@channel_session_user
def data_broadcast(message):
    slider = float(message.get('sliderValue'))
    if slider:
        user, game = user_and_game(message)
        # Returns every one who followed this user on this round
        round_data = json.loads(cache.get(user.username))
        rounds = InteractiveRound.objects.filter(following=user, round_order=round_data.get('current_round'))
        # check the game and state and make sure we are on interactive mode
        print('1'*20)
        print('ROUNDS')
        print(rounds.all())
        print('1'*20)

        for user_round in rounds.all():
            # r = InteractiveRound.objects.filter(user=follower,
            #                                     round_outcome=round_data.get('current_round'),
            #                                     guess__gt=Decimal(-3),  # user would submit a -1 for no answer
            #                                     influenced_guess__gt=Decimal(-3), # sum
            #                                     )
            print('Going to send data to {}'.format(user_round.user.username))
            Group(game.user_channel(user_round.user)).send({
                'text': json.dumps({
                    'action': 'sliderChange',
                    'username': user.username,
                    'slider': slider,
                })
            })
            # game.user_channel(follower.user).send({
            #
            # })

    else:
        logging.error('Got invalid value for slider')


@channel_session_user
def follow_list(message):
    user, game = user_and_game(message)
    follow_users = message.get('following')
    print('*'*20)
    print(follow_users)
    print('*'*20)
    # a list of all the usernames to follow
    if len(follow_users) <= game.constraints.max_following:
        round_data = json.loads(cache.get(user.username))
        next_round = InteractiveRound.objects.get(user=user, round_order=round_data.get('current_round'))

        print('Next Round Following list before clearing {}'.format(next_round.following.count()))
        next_round.following.clear()
        next_round.save()
        print('Next Round following list {}'.format(next_round.following.count()))

        u_can_follow = []
        just_followed = []
        for u in game.users.all():
            d = {
                    'username': u.username,
                    'avatar': u.get_avatar,
                    'score': u.get_score,
                }
            if u.username == user.username:
                continue
            elif u.username in follow_users:
                next_round.following.add(u)
                just_followed.append(d)
            else:
                u_can_follow.append(d)

        next_round.save()
        print('After loop following list {}'.format(next_round.following.count()))

        message.reply_channel.send({'text':json.dumps({
            'action': 'followNotify',
            'following': just_followed,
            'all_players': u_can_follow,
        })})
    else:

        message.reply_channel.send({'text': json.dumps({
            'error': True,
            'msg': 'didn\'t meet game constraints max is {} and list is {}'.format(game.constraints.max_following,
                                                                                   len(follow_users)),
            })})


@channel_session_user
def initial_submit(message):
    user, game = user_and_game(message)
    guess = message.get('guess')
    try:
        round_data = json.loads(cache.get(user.username))
        current_round = InteractiveRound.objects.get(user=user, round_order=round_data.get('current_round'))
        current_round.guess = Decimal(guess)
        current_round.save()
        message.reply_channel.send({
            'text': json.dumps({
                'guess': guess,
                'status': 1,
            })
        })
    except InteractiveRound.DoesNotExist:
        message.reply_channel.send({
            'text': json.dumps({
                'error': True,
                'msg': "User not found",
            })
        })
        return

    remaining_users = InteractiveRound.objects.filter(game=game, guess=Decimal(-3),
                                                      round_order=round_data.get('current_round'))
    if remaining_users.count() == 0:
        # Interactive On
        for user in game.users.all():
            current_round = InteractiveRound.objects.get(user=user, round_order=round_data.get('current_round'))
            following = [{'username': u.username, 'avatar': u.get_avatar, 'guess':
                float(InteractiveRound.objects.get(user=u, round_order=round_data.get('current_round')).guess)}
                         for u in current_round.following.all()]
            Group(game.user_channel(user)).send({
                'text': json.dumps({
                    'action': 'interactive',
                    'plot': round_data.get('plot'),
                    'score': user.get_score,
                    'remaining': round_data.get('remaining'),
                    'current_round': round_data.get('current_round'),
                    # a list of dicts of {usernames and avatars} for the players that the user follows
                    'following': following,
                })
            })
    return


@channel_session_user
def interactive_submit(message):
    auth_user, game = user_and_game(message)
    guess = message.get('socialGuess')
    try:
        round_data = json.loads(cache.get(auth_user.username))
        current_round = InteractiveRound.objects.get(user=auth_user, round_order=round_data.get('current_round'))
        current_round.influenced_guess = Decimal(guess)
        current_round.save()
    except InteractiveRound.DoesNotExist:
        message.reply_channel.send({
            'text': json.dumps({
                'error': True,
                'msg': "User not found",
            })
        })
        return

    remaining_users = InteractiveRound.objects.filter(game=game, influenced_guess=Decimal(-3),
                                                      round_order=round_data.get('current_round'))
    if remaining_users.count() == 0:
        # Outcome On
        for user in game.users.all():
            current_round = InteractiveRound.objects.get(user=user, round_order=round_data.get('current_round'))
            rest_of_users = []
            print('=' * 20)
            for u in current_round.game.users.filter(~Q(username__in=current_round.following.values('username')))\
                    .exclude(username=user.username):
                print(u)
                rest_of_users.append({'username': u.username, 'avatar': u.get_avatar, 'score': u.get_score})
            print('=' * 20)
            currently_following = []
            for u in current_round.following.all():
                currently_following.append({'username': u.username, 'avatar': u.get_avatar, 'score': u.get_score})

            Group(game.user_channel(user)).send({
                'text': json.dumps({
                    'action': 'outcome',
                    'plot': round_data.get('plot'),
                    'remaining': round_data.get('remaining'),
                    'current_round': round_data.get('current_round'),
                    # a list of dicts of {usernames and avatars} for the players that the user follows
                    'guess': float(current_round.influenced_guess),
                    'score': user.get_score,
                    'following': currently_following,
                    'all_players': rest_of_users,
                    'max_following': game.constraints.max_following,
                    'correct_answer': float(current_round.plot.answer),
                })
            })
        # we assign users to the next game
        round_ = get_round(game)
        if round_ is None:
            game.broadcast(action='redirect', url=reverse('interactive:exit'))
        return
    message.reply_channel.send({
        'text': json.dumps({
            'guess': guess,
            'status': 1,
        })
    })


@channel_session_user
def round_outcome(message):
    user, game = user_and_game(message)
    round_data = json.loads(cache.get(user.username))
    if round_data is None:
        print('round_data is None')
        return
    round_ = InteractiveRound.objects.get(user=user, game=game, round_order=round_data.get('current_round')-1)
    round_.outcome = True
    round_.save()
    waiting_for = InteractiveRound.objects.filter(game=game, round_order=round_data.get('current_round')-1,
                                                  outcome=False).count()

    print('#'*20)
    print('waiting for')
    print(waiting_for)
    print('#'*20)

    if waiting_for == 0:
        game.broadcast(action='initial', plot=round_data.get('plot'), remaining=round_data.get('remaining'),
                       current_round=round_data.get('current_round'))
    return


def foo(game):
    print('&'*30)
    print("{}{}".format(' '*15, 'Called'))
    print('&'*30)
    game.broadcast(foo='foo', msg='Hello world')
