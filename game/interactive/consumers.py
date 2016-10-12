import json
import logging
from random import choice
from decimal import Decimal

from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user
from django.core.cache import cache

from game.round.models import Plot
from game.users.models import User
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
        cache.set(user.username, json.dumps({
            'game': game.id,
            'current_round': current_round,
            'plot': plot.plot,
            'remaining': remaining,
        }))
        i_round = InteractiveRound(user=user, game=game, plot=plot, round_order=current_round, guess=Decimal(-3),
                                   influenced_guess=Decimal(-3))
        i_round.save()
        if current_round == 0:
            # random initial game configuration
            following = users.exclude(username=user.username).order_by('?')[:game.constraints.max_following]  # random
            for f in following.all():
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
        data = cache.get(user.username)
        if data:
            # game already started
            round_ = json.loads(data)
            print('ROUND')
            print(round_)
            print('='*20)
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
    if game.started:
        game.users.remove(user)
        game.broadcast('info',
                       'There are currently a total of {} out of {} required '
                       'participants waiting for the game to start.'.
                       format(game.users.count(), game.constraints.max_users))
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

            game.user_channel(follower.user).send({
                'text': json.dumps({
                    'action': 'sliderChange',
                    'username': user.username,
                    'slider': slider,
                })
            })

    else:
        logging.error('Got invalid value for slider')


@channel_session_user
def follow_list(message):
    user, game = user_and_game(message)
    follow_users = message.get('follow')
    # a list of all the usernames to follow
    if game.constraints.max_following >= len(follow_users) > game.constraints.min_following:
        round_data = json.loads(cache.get(user.username))
        round_ = InteractiveRound.objects.get(user=user, game=game, influenced_guess=Decimal(-3),
                                              round_order=round_data.get('current_round'))
        round_.following.clear()
        for username in follow_users:
            u = User.objects.get(username=username)
            round_.following.add(u)
        round_.save()
        print(follow_users)
        message.replay_channel.send({
            'text': json.dumps({
                'action': 'followNotify',
                'following': follow_users,
            })
        })
    else:
        message.replay_channel.send({
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
            following = [{'username': u.username, 'avatar': u.get_avatar} for u in current_round.following.all()]
            game.user_channel(user).send({
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
            d = {u.username: {'username': u.username, 'avatar': u.get_avatar, 'score': u.get_score}
                 for u in current_round.following.all()}
            users = []
            for i in game.users.all().exclude(username=user.username):
                try:
                    d[i]
                except KeyError:
                    users.append({
                        'username': i.username,
                        'avatar': i.get_avatar,
                        'score': i.get_score,
                    })

            following = list(d.values())
            game.user_channel(user).send({
                'text': json.dumps({
                    'action': 'outcome',
                    'plot': round_data.get('plot'),
                    'remaining': round_data.get('remaining'),
                    'current_round': round_data.get('current_round'),
                    # a list of dicts of {usernames and avatars} for the players that the user follows
                    'following': following,
                    'all_players': users,
                    'max_following': game.constraints.max_following,
                })
            })
        # we assign users to the next game
        get_round(game)
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
    round_ = InteractiveRound.objects.get(user=user, game=game, round_order=round_data.get('current_round'))
    round_.outcome = True
    round_.save()
    waiting_for = InteractiveRound.objects.filter(game=game, round_order=round_data.get('current_round'),
                                                  outcome=False).count()

    if waiting_for == 0:
        round_ = get_round(game)
        game.group_channel.send({'text': json.dumps({
            'action': 'initial',
            'plot': round_.get('plot'),
            'remaining': round_.get('remaining'),
            'current_round': round_.get('current_round'),
        })
        })
        return
