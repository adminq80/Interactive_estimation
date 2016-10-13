import json
import logging
from random import choice
from decimal import Decimal

from channels import Channel
from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse

from game.round.models import Plot
from game.users.models import User
from .models import Interactive, InteractiveRound


def get_round(game, user=None):
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


@channel_session_user_from_http
def lobby(message):

    user, game = user_and_game(message)
    if not user.is_authenticated or game is None:
        # redirect to login
        return redirect('/')

    logging.info('user {} just entered {}'.format(user.username, game.group_channel))

    game.group_channel.add(message.reply_channel)

    logging.info("Channel NAME is {}".format(message.reply_channel.name))

    # channel = game.user_channel(user)
    # if channel:
    #     Grop(channel).add(message.reply_channel)
    # else:
    #     logging.error("Couldn't create a user channel")
    #     raise Exception("Couldn't create user channel")
    Group(game.user_channel(user)).add(message.reply_channel)

    users_count = game.users.count()
    waiting_for = game.constraints.max_users - users_count
    # TODO: add time to the condition
    if waiting_for == 0:
        # users = game.users.exclude(username=user.username)
        # l = [{'username': i.username, 'avatar': i.get_avatar} for i in users]
        data = cache.get(user.username)
        if data:
            # game already started
            round_ = json.loads(data)
            if round_:
                game = Interactive.objects.get(id=round_.get('game'))
                print(game)
            else:
                raise NotImplementedError
        else:
            game.started = True
            game.save()
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
    game.broadcast('info',
                   'There are currently a total of {} out of {} required participants waiting for the game to start.'.
                   format(game.users.count(), game.constraints.max_users))


@channel_session_user
def exit_game(message):
    user, game = user_and_game(message)
    logging.info('user {} just exited'.format(user.username))
    if not game.started:
        game.users.remove(user)
        game.broadcast('info',
                       'There are currently a total of {} out of {} required '
                       'participants waiting for the game to start.'.
                       format(game.users.count(), game.constraints.max_users))
    game.group_channel.discard(message.reply_channel)
    Group(game.user_channel(user)).discard(message.reply_channel)


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

        for follower in rounds.all():
            # r = InteractiveRound.objects.filter(user=follower,
            #                                     round_outcome=round_data.get('current_round'),
            #                                     guess__gt=Decimal(-3),  # user would submit a -1 for no answer
            #                                     influenced_guess__gt=Decimal(-3), # sum
            #                                     )

            Group(game.user_channel(follower.user)).send({
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
    print(follow_users)
    # a list of all the usernames to follow
    if game.constraints.max_following >= len(follow_users):
        round_data = json.loads(cache.get(user.username))
        current_round = InteractiveRound.objects.get(user=user, game=game, round_order=round_data.get('current_round'))

        current_round.following.clear()
        current_round.save()
        for username in follow_users:
            u = User.objects.get(username=username)
            if u != user:
                current_round.following.add(u)
                current_round.save()
        print(follow_users)
        new_list = {}
        for u in current_round.following.all():
            new_list[u.username] = ({'username': u.username, 'avatar': u.get_avatar, 'score': u.get_score})

        # g.users.filter(~Q(username__in=i.following.values('username')))
        rest_of_users = []
        for u in current_round.game.users.filter(~Q(username__in=current_round.following.values('username'))).\
                exclude(username=user.username):
            rest_of_users.append({'username': u.username, 'avatar': u.get_avatar, 'score': u.get_score})

        message.reply_channel.send({
            'text': json.dumps({
                'action': 'followNotify',
                'following': list(new_list.values()),
                'all_players': rest_of_users,
            })
        })
    else:
        message.reply_channel.send({
            'text': json.dumps({
                'error': True,
                'msg': 'didn\'t meet game constraints',
            })
        })


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

        # for user in game.users.all():
        #     d = {u.username: {'username': u.username, 'avatar': u.get_avatar, 'score': u.get_score}
        #          for u in current_round.following.all()}
        #     users = []
        #     for i in game.users.all().exclude(username=user.username):
        #         try:
        #             d[i]
        #         except KeyError:
        #             users.append({
        #                 'username': i.username,
        #                 'avatar': i.get_avatar,
        #                 'score': i.get_score,
        #             })
        #
        #     following = list(d.values())
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
                })
            })
        # we assign users to the next game
        round_ = get_round(game)
        if round_ is None:
            game.group_channel.send({'text': json.dumps({
                'action': 'redirect',
                'url': reverse('interactive:exit'),
            })})
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

    if waiting_for == 0:
        game.group_channel.send({'text': json.dumps({
            'action': 'initial',
            'plot': round_data.get('plot'),
            'remaining': round_data.get('remaining'),
            'current_round': round_data.get('current_round'),
        })
        })
    return
