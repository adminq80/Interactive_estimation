from random import choice
from string import ascii_lowercase, digits
from game.users.models import User


def random_user(game_type, length=80, chars=ascii_lowercase+digits):
    username = ''.join([choice(chars) for i in range(length)])
    try:
        User.objects.get(username=username)
        return random_user(game_type, length=length, chars=chars)
    except User.DoesNotExist:
        u = User(username=username, game_type=game_type)
        u.save()
        password = User.objects.make_random_password()
        u.set_password(password)
        #u.level = choice(['e', 'm', 'h']) #abdullah
        u.level = choice(['h'])
        u.save()
        return u, password
