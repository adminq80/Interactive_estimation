import json
import logging
from random import shuffle
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction
from django.db.models import Count
from django.db.models import Q
from django.urls import reverse

from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user
from django.utils import timezone
from game.round.models import Plot

from .utils import avatar
from .models import InteractiveShocks, InteractiveShocksRound, Settings, Task
from .delayed_message import DelayedMessageExecutor

SECONDS = 30


def changing_levels(game):
    total_users = game.users.count()
    chunk = total_users // 3
    last_chuck = total_users - chunk * 2
    level_list = ['e', 'm'] * chunk + ['h'] * last_chuck
    shuffle(level_list)
    for i, user in enumerate(game.users.all()):
        user.level = level_list[i]
        user.save()


def get_round(game, user=None):
    users = game.users.order_by('?')
    if not user:
        user = users[0]
    played_rounds = InteractiveShocksRound.objects.filter(user=user, game=game)

    current_round = played_rounds.count()

    remaining = game.constraints.max_rounds - current_round
    if remaining == 0:
        # reactor.stop()
        return None, None

    users_plots = []
    seqs = {
        'e': 1,
        'm': 2,
        'h': 3,
    }
    for user in users.all():
        seq = seqs[user.level]
        plot = Plot.objects.filter(non_stationary_seq=seq).order_by('seq')[current_round]
        users_plots.append({'user': user, 'plot': plot.plot})

        i_round, _ = InteractiveShocksRound.objects.get_or_create(user=user, game=game, plot=plot,
                                                                  round_order=current_round)

        if current_round == 0:
            # random initial game configuration
            following = users.exclude(username=user.username).order_by('?')[:game.constraints.max_following]  # random
            for f in following.all():
                i_round.following.add(f)
        else:
            previous_round = InteractiveShocksRound.objects.get(user=user, game=game, round_order=current_round - 1)
            for f in previous_round.following.all():
                i_round.following.add(f)
        with transaction.atomic():
            i_round.save()

    return {'plot': None, 'remaining': remaining, 'current_round': current_round}, users_plots


def user_and_game(message):
    user = message.user
    if user.is_authenticated:
        try:
            game = InteractiveShocks.objects.get(users=user)
        except InteractiveShocks.DoesNotExist:
            game = None
    else:
        logging.error('User is anonymous and needs to login')
        raise Exception('User is Anonymous')
    return user, game


def send_user_avatar(game, user):
    game.user_send(user, action='avatar', url='/static/{}'.format(user.get_avatar))


def send_game_status(game):
    game.broadcast(action='info', connected_players=game.users.count(), total_players=game.constraints.max_users)


def task_runner(message):
    """
    runs tasks from asgi.delay
    """
    # 'content': {'task': t.id},
    try:
        t = Task.objects.get(id=message['task'])
    except Task.DoesNotExist:
        return None
    Channel(t.route).send({'task': message['task'], 'path': t.path})


def create_task(route, game, user):
    return {'route': route,
            'path': '/dynamic_mode/lobby',
            'game': game,
            'payload': json.dumps({'username': user.username, }),
            }


def watch_user(game, user):
    if game.started:
        return
    if user.exited or user.kicked:
        return
    DelayedMessageExecutor(create_task('watcher', game, user), game.constraints.prompt_seconds).send()


@channel_session_user_from_http
def lobby(message):
    user = message.user

    if not user.is_authenticated or user.kicked or user.exited:
        message.reply_channel.send({'text': json.dumps({'action': 'logout', 'url': reverse('account_logout')})})
        return

    try:
        game_settings = Settings.objects.order_by('?')[0]
    except Settings.DoesNotExist:
        game_settings, _ = Settings.objects.get_or_create(max_users=5, min_users=0, max_following=2, min_following=0)

    try:
        with transaction.atomic():
            game = InteractiveShocks.objects.get(users=user)
    except InteractiveShocks.DoesNotExist:
        game = None

    if game:
        if game.end_time is None:
            # game is still in progress
            game.group_channel.add(message.reply_channel)
            game.user_channel(user).add(message.reply_channel)
            send_user_avatar(game, user)
            if game.started:
                # game started we need to assigned player to the latest round with the correct mode
                try:
                    d = cache.get(game.id)
                    state = d.get('state')
                    round_data = d.get('round_data')
                    users_plots = d.get('users_plots')
                except AttributeError:
                    print('Cache invalid')
                    game.user_send(user, action='logout', url=reverse('account_logout'))
                    return
                cache.set('{}_disconnected_users'.format(game.id),
                          cache.get('{}_disconnected_users'.format(game.id)) - 1)
                game.broadcast(action='reconnected', username=user.username)
                for i in users_plots:
                    if i['user'] == user:
                        round_data['plot'] = i['plot']
                if state == 'initial':
                    initial(game, round_data, users_plots, message)
                elif state == 'interactive':
                    interactive(user, game, round_data)
                elif state == 'outcome':
                    outcome(user, game, round_data)
                else:
                    raise Exception('Unknown state')
                return
            else:
                try:
                    d = cache.get(game.id)
                    state = d.get('state')
                except AttributeError:
                    print("Game was not found")
                    game.user_send(user, action='logout', url=reverse('account_logout'))
                watch_user(game, user)
                send_game_status(game)
        else:
            game.user_send(user, action='logout', url=reverse('account_logout'))
            game.broadcast(error=True, msg='The has ended please login back again')
        return

    games = InteractiveShocks.objects.filter(started=False).annotate(
        num_of_users=Count('users')).order_by('-num_of_users')

    if games:
        for game in games:
            if game.users.count() < game.constraints.max_users:
                used_avatars = {i.avatar for i in game.users.all()}
                user.avatar = avatar(used_avatars)
                user.save()
                game.users.add(user)
                watch_user(game, user)
                break
        else:
            print("Could not find an empty game")
            logging.error("User couldn't be assigned to a game")
            return
    else:
        game = InteractiveShocks.objects.create(constraints=game_settings)
        game.users.add(user)
        user.avatar = avatar()
        user.save()
        watch_user(game, user)

    game.group_channel.add(message.reply_channel)
    game.user_channel(user).add(message.reply_channel)

    send_user_avatar(game, user)

    users_count = game.users.count()
    waiting_for = game.constraints.max_users - users_count

    if waiting_for == 0:
        print("Going to start the game")
        game.started = True
        game.save()
        print("Game started value {}".format(game.started))
        [m.delete() for m in Task.objects.filter(route='kickout', game=game)]
        [m.delete() for m in Task.objects.filter(route='watcher', game=game)]
        cache.set('{}_disconnected_users'.format(game.id), 0)
        # change users levels
        print("Going to chane the levels")
        changing_levels(game)
        print("Going to start the first round")
        start_initial(game)
    else:
        send_game_status(game)
    return


@channel_session_user
def exit_game(message):
    user, game = user_and_game(message)
    logging.info('user {} just exited'.format(user.username))
    if game:
        # game and user found
        if user.kicked or not game.started:
            game.users.remove(user)
            game.save()
            send_game_status(game)
        if game.started:
            if game.end_time is None:
                game.broadcast(action='disconnected', username=user.username)
                disconnected_count = cache.get('{}_disconnected_users'.format(game.id)) or 0
                cache.set('{}_disconnected_users'.format(game.id), disconnected_count + 1)
        game.group_channel.discard(message.reply_channel)
        game.user_channel(user).discard(message.reply_channel)
    else:
        message.reply_channel.send({'text': json.dumps({'action': 'logout', 'url': reverse('account_logout')})})


@channel_session_user
def ws_receive(message):
    payload = json.loads(message['text'])
    action = payload.get('action')

    if action:
        payload['reply_channel'] = message.content['reply_channel']
        payload['path'] = message.content.get('path')
        Channel('game.route').send(payload)
    else:
        # TODO: unrecognized action
        print('unrecognized action')
        print(message)
        logging.error('Unknown action {}'.format(action))


@channel_session_user
def data_broadcast(message):
    slider = float(message.get('sliderValue'))
    if slider:
        user, game = user_and_game(message)
        try:
            d = cache.get(game.id)
            state = d.get('state')
            round_data = d.get('round_data')
        except AttributeError:
            game.user_send(user, action='logout', url=reverse('account_logout'))
            return
        if state == 'interactive':
            # Returns every one who followed this user on this round
            rounds = InteractiveShocksRound.objects.filter(
                following=user, game=game, round_order=round_data.get('current_round'))
            # check the game and state and make sure we are on interactive mode

            for user_round in rounds.all():
                game.user_send(user_round.user, action='sliderChange', username=user.username, slider=slider)
    else:
        logging.error('Got invalid value for slider')


@channel_session_user
def follow_list(message):
    user, game = user_and_game(message)
    follow_users = message.get('following')
    # a list of all the usernames to follow
    try:
        d = cache.get(game.id)
        state = d.get('state')
        round_data = d.get('round_data')
    except AttributeError:
        game.user_send(user, action='logout', url=reverse('account_logout'))
        return
    if state != 'outcome':
        return
    if len(follow_users) <= game.constraints.max_following:
        next_round = InteractiveShocksRound.objects.get(user=user, round_order=round_data.get('current_round'))
        next_round.following.clear()
        next_round.save()
        u_can_follow = []
        just_followed = []
        for u in game.users.all():
            d = {
                'username': u.username,
                'avatar': u.get_avatar,
                'score': u.get_score_and_gain[0],
                'gain': u.get_score_and_gain[1],
            }
            if u.username == user.username:
                continue
            elif u.username in follow_users:
                next_round.following.add(u)
                just_followed.append(d)
            else:
                u_can_follow.append(d)
        with transaction.atomic():
            next_round.save()
        message.reply_channel.send({'text': json.dumps({
            'action': 'followNotify',
            'following': just_followed,
            'all_players': u_can_follow,
        })})
    else:
        print(follow_users)
        print(message.get('following'))
        message.reply_channel.send({'text': json.dumps({
            'error': True,
            'msg': "didn't meet game constraints max is {} and list is {}".format(game.constraints.max_following,
                                                                                  len(follow_users)),
        })})


@channel_session_user
def initial_submit(message):
    user, game = user_and_game(message)
    guess = message.get('guess')
    try:
        d = cache.get(game.id)
        state = d.get('state')
        round_data = d.get('round_data')
    except AttributeError:
        game.user_send(user, action='logout', url=reverse('account_logout'))
        return
    if state == 'initial':
        try:
            current_round = InteractiveShocksRound.objects.get(user=user, game=game,
                                                               round_order=round_data.get('current_round'))
            current_round.guess = Decimal(guess)
            current_round.save()
        except InteractiveShocksRound.DoesNotExist:
            message.reply_channel.send({
                'text': json.dumps({
                    'error': True,
                    'msg': "User not found",
                })
            })


@channel_session_user
def interactive_submit(message):
    user, game = user_and_game(message)
    guess = message.get('socialGuess')
    try:
        d = cache.get(game.id)
        state = d.get('state')
        round_data = d.get('round_data')
    except AttributeError:
        game.user_send(user, action='logout', url=reverse('account_logout'))
        return

    if state == 'interactive':
        try:
            current_round = InteractiveShocksRound.objects.get(user=user, game=game,
                                                               round_order=round_data.get('current_round'))
            current_round.influenced_guess = Decimal(guess)
            current_round.save()
        except InteractiveShocksRound.DoesNotExist:
            message.reply_channel.send({
                'text': json.dumps({
                    'error': True,
                    'msg': "User not found",
                })
            })


@channel_session_user
def round_outcome(message):
    user, game = user_and_game(message)
    try:
        d = cache.get(game.id)
        round_data = d.get('round_data')
    except AttributeError:
        game.user_send(user, action='logout', url=reverse('account_logout'))
        return
    round_ = InteractiveShocksRound.objects.get(user=user, game=game, round_order=round_data.get('current_round'))
    round_.outcome = True
    round_.save()
    return


# def game_state_checker(game, state, round_data, users_plots, counter=0):
def game_state_checker(message):
    game, _ = get_game_from_message(message)
    if not game:
        return
    data = cache.get(game.id)
    state = data.get('state')
    round_data = data.get('round_data')
    users_plots = data.get('users_plots')
    counter = data.get('counter')

    if counter == SECONDS:
        # move to the next state
        if state == 'initial':
            start_interactive(game, round_data, users_plots)
        elif state == 'interactive':
            start_outcome(game, round_data, users_plots)
        else:
            start_initial(game)
        return

    if state == 'initial':
        r = InteractiveShocksRound.objects.filter(
            game=game, round_order=round_data.get('current_round'), guess=None).count()
        try:
            r -= cache.get('{}_disconnected_users'.format(game.id))
        except TypeError:
            pass
        if r == 0:
            start_interactive(game, round_data, users_plots)
            return
    elif state == 'interactive':
        r = InteractiveShocksRound.objects.filter(game=game, round_order=round_data.get('current_round'),
                                                  influenced_guess=None).count()
        try:
            r -= cache.get('{}_disconnected_users'.format(game.id))
        except TypeError:
            pass

        if r == 0:
            start_outcome(game, round_data, users_plots)
            return
    elif state == 'outcome':
        r = InteractiveShocksRound.objects.filter(game=game, round_order=round_data.get('current_round'),
                                                  outcome=False).count()
        try:
            r -= cache.get('{}_disconnected_users'.format(game.id))
        except TypeError:
            pass

        if r == 0:
            start_initial(game)
            return

    counter += 1
    data['counter'] = counter
    cache.set(game.id, data)
    DelayedMessageExecutor(create_game_task('game_state', game), 1).send()


def create_game_task(route, game, path='/dynamic_mode/lobby', payload=None):
    return {'route': route,
            'game': game,
            'path': path,
            'payload': json.dumps(payload),
            }


def start_initial(game):
    round_data, users_plots = get_round(game)
    state = 'initial'

    if round_data is None:
        game.end_time = timezone.now()
        game.save()
        game.broadcast(action='redirect', url=reverse('dynamic_mode:exit'))
        return
    else:
        cache.set(game.id, {'state': state,
                            'round_data': round_data,
                            'users_plots': users_plots,
                            'counter': 0,
                            })
    initial(game, round_data, users_plots)
    DelayedMessageExecutor(create_game_task('game_state', game), 1).send()
    # task.deferLater(reactor, 1, game_state_checker, game, state, round_data, users_plots).addErrback(twisted_error)


def initial(game, round_data, users_plots, message=None):
    data = {'action': 'initial',
            'plot': round_data.get('plot'),
            'remaining': round_data.get('remaining'),
            'current_round': round_data.get('current_round'),
            'seconds': SECONDS,
            }

    if message:
        # send to only one user and return
        game.user_send(message.user, **data)
        return
    else:
        for i in users_plots:
            user = i['user']
            data['plot'] = i['plot']
            game.user_send(user, **data)


def start_interactive(game, round_data, users_plots):
    state = 'interactive'
    cache.set(game.id, {'state': state,
                        'round_data': round_data,
                        'users_plots': users_plots,
                        'counter': 0,
                        })
    for i in users_plots:
        user = i['user']
        round_data['plot'] = i['plot']
        interactive(user, game, round_data)
    DelayedMessageExecutor(create_game_task('game_state', game), 1).send()


def interactive(user, game, round_data):
    current_round = InteractiveShocksRound.objects.get(
        user=user, game=game, round_order=round_data.get('current_round'))

    following = [{'username': u.username, 'avatar': u.get_avatar, 'guess': InteractiveShocksRound.objects.get(
        user=u,
        round_order=round_data.get('current_round')).get_guess()} for u in current_round.following.all()]
    score, gain = user.get_score_and_gain
    game.user_send(user, action='interactive', score=score, gain=gain,
                   following=following, seconds=SECONDS, **round_data)


def start_outcome(game, round_data, users_plots):
    cache.set(game.id, {'state': 'outcome',
                        'round_data': round_data,
                        'users_plots': users_plots,
                        'counter': 0,
                        })
    for i in users_plots:
        user = i['user']
        round_data['plot'] = i['plot']
        outcome(user, game, round_data)
    DelayedMessageExecutor(create_game_task('game_state', game), 1).send()


def outcome_loop(l):
    return [{'username': u.username, 'avatar': u.get_avatar, 'score': u.get_score_and_gain[0],
             'gain': u.get_score_and_gain[1]} for u in l]


def outcome(user, game: InteractiveShocks, round_data):
    current_round = InteractiveShocksRound.objects.get(user=user, round_order=round_data.get('current_round'))

    rest_of_users = outcome_loop(current_round.game.users.filter(~Q(username__in=current_round.following.values(
        'username'))).exclude(username=user.username))

    currently_following = outcome_loop(current_round.following.all())
    score, gain = user.get_score_and_gain

    game.user_send(user, action='outcome', guess=float(current_round.get_influenced_guess()),
                   score=score, gain=gain, following=currently_following, all_players=rest_of_users,
                   max_following=game.constraints.max_following, correct_answer=float(current_round.plot.answer),
                   seconds=SECONDS, **round_data)


def get_game_from_message(message):
    try:
        t = Task.objects.get(id=message['task'])
    except Task.DoesNotExist:
        print('Encountered an error')
        return None, None
    game = t.game
    payload = json.loads(t.payload)
    t.delete()
    return game, payload


def game_watcher(message):
    print('Watcher')
    game, payload = get_game_from_message(message)
    if not game and not payload:
        return
    if game.started:
        return
    username = payload.get('username')
    if username:
        try:
            user = game.users.get(username=username)
        except game.users.model.DoesNotExist:
            print('USER was not found in WATCHER')
            return
    else:
        return
    print('Timer reached for {}'.format(username))
    if user.prompted < game.constraints.max_prompts:
        print("Going to prompt {}".format(user.username))

        DelayedMessageExecutor(create_task('kickout', game, user), game.constraints.kickout_seconds).send()
        print(Task.objects.all())
        if game.constraints.minutes_mode:
            game.user_send(user, action='timeout_prompt', minutes=game.constraints.prompt_seconds//60,
                           sound_interval=game.constraints.prompt_sound_interval, url=reverse('dynamic_mode:exit'))
        else:
            game.user_send(user, action='timeout_prompt', minutes=None, seconds=game.constraints.prompt_seconds,
                           sound_interval=game.constraints.prompt_sound_interval, url=reverse('dynamic_mode:exit'))
    else:
        DelayedMessageExecutor(create_task('kickout', game, user), 0.1).send()


def kickout(message):
    print('Kickout')
    game, payload = get_game_from_message(message)
    if not game and not payload:
        return
    if game.started:
        return
    username = payload.get('username')
    if username:
        try:
            user = game.users.get(username=username)
        except game.users.model.DoesNotExist:
            print('USER was not found in WATCHER')
            return
    else:
        return
    print("Kickout id={} started {}".format(game.id, game.started))
    print("Kickout pk={} started {}".format(game.pk, game.started))
    print('Going to kick user {}'.format(username))
    user.kicked = True
    user.save()
    game.user_send(user, action='AFK')
    send_game_status(game)


@channel_session_user
def reset_timer(message):
    user, game = user_and_game(message)
    if game:
        print('Reset timer for {}'.format(user.username))
        try:
            print(Task.objects.all())
            m = Task.objects.get(route='kickout', game=game, payload__contains=user.username)
            m.delete()
        except Task.DoesNotExist as e:
            print('Reset timer')
            print("Don't know how to handle this error")
            print(e)
            print(Task.objects.all())
            return
        user.prompted += 1
        user.save()
        if game.started:
            one = [m.delete() for m in Task.objects.filter(route='kickout', game=game)]
            two = [m.delete() for m in Task.objects.filter(route='watcher', game=game)]
            print('Reset one {}, two {}'.format(len(one), len(two)))
            game.user_send(user, action='ping', text='Hello')
        else:
            watch_user(game, user)


@channel_session_user
def cancel_game(message):
    user, game = user_and_game(message)
    if game:
        game.user_send(user, action='logout', url=reverse('dynamic_mode:exit'))
