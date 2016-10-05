import json
import logging

from django.urls import reverse

from channels.auth import channel_session_user_from_http, channel_session_user

from .models import Interactive


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
        game.group_channel.send({'text': json.dumps({
            'action': 'redirect',
            'url': reverse('interactive:play'),
        })
        })
        return

    # TODO I think this should go to the lobby template .. only the variables are passed
    game.broadcast('info', 'There are currently a total of {} out of {} required participants waiting for the game to start.'.
                   format(game.constraints.max_users - game.users.count(), game.users.count()))

@channel_session_user
def exit_game(message):
    user, game = user_and_game(message)
    # logging.info('user {} just exited'.format(user.username))
    game.group_channel.discard(message.reply_channel)


@channel_session_user
def send_data(message):
    _, game = user_and_game(message)
    text = json.loads(message['text'])
    for user in game.users.all():
        game.user_channel(user).send({'text': json.dumps({
            'action': 'info',
            'text': text,
        }
        )})


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
