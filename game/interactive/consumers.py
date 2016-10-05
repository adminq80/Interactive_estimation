import json
import logging
from random import choice

from django.urls import reverse

from channels.auth import channel_session_user_from_http, channel_session_user

from game.round.models import Plot
from .models import Interactive, InteractiveRound


def get_round(game):
    users = game.users.all()
    played_rounds = InteractiveRound.objects.filter(user=users[0])
    plot_pks = {i.plot.pk for i in played_rounds}
    current_round = len(plot_pks)
    remaining = Plot.objects.count() - current_round
    plots = Plot.objects.exclude(pk__in=plot_pks)
    plot = choice(plots)

    return {'round': plot, 'remaining': remaining, 'current_round': current_round}
    # played_rounds = InteractiveRound.objects.filter(user=u)
    # plot_pks = {i.plot.pk for i in played_rounds}
    #
    # score = calculate_score(played_rounds)
    # currentRound = len(plot_pks)
    #
    # remaining = Plot.objects.count() - currentRound
    #
    # if remaining == 0:
    #     i = Interactive.objects.get(user=u)
    #     i.end_time = timezone.now()
    #     i.save()
    #     return redirect('interactive:exit_survey')
    #
    # if request.session.get('PLOT'):
    #     plot = Plot.objects.get(plot=request.session.get('PLOT'))
    # else:
    #     plots = Plot.objects.exclude(pk__in=plot_pks)
    #     plot = choice(plots)
    #
    # request.session['PLOT'] = plot.plot
    # form = RoundForm()
    #
    # return render(request, 'interactive/play.html', {'users': users,
    #                                                  'state': 'initial',
    #                                                  'round': plot,
    #                                                  'form': form,
    #                                                  'remaining': remaining,
    #                                                  'currentRound': currentRound
    #                                                  })
    #

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
        l = game.users.exclude(username=user.username).value_list('username', 'avatar')
        round_ = get_round(game)
        game.group_channel.send({'text': json.dumps({
            'action': 'initial',
<<<<<<< HEAD
            'players': l,
            'plot': round_.get('plot'),
            'remaining': round_.get('remaining'),
            'current_round': round_.get('current_round'),
=======
>>>>>>> 338cdb247052518de3c82c1bbff7b0fb8877d270
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


@channel_session_user
def send_data(message):
    _, game = user_and_game(message)
    val = json.loads(message['sliderValue'])
    print(val)
    # for user in game.users.all():
    #     game.user_channel(user).send({'text': json.dumps({
    #         'action': 'info',
    #         'text': text,
    #     }
    #     )})


@channel_session_user
def data_submit(message):
    user, game = user_and_game(message)
    payload = json.loads(message['text'])

    pass


def data_broadcast(message):
    pass


def follow_list(message):
    pass


def unfollow(message):
    pass

def lobby2(message):
    message.reply_channel()