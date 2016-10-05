import json
import uuid

from django.db import models
from django.conf import settings

from channels import Group

from game.round.models import Round


class Settings(models.Model):
    max_users = models.PositiveSmallIntegerField()
    min_users = models.PositiveSmallIntegerField()

    max_influencers = models.PositiveSmallIntegerField()
    min_influencers = models.PositiveSmallIntegerField()

    def __str__(self):
        return "Settings: users({},{}), influencers({},{})".format(self.min_users, self.max_users,
                                                                   self.min_influencers, self.max_influencers
                                                                   )

    class Meta:
        verbose_name_plural = 'Settings'


class InteractiveRound(Round):
    influencers = models.ManyToManyField(settings.AUTH_USER_MODEL)
    influenced_guess = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    def __str__(self):
        return self.user.username


class Interactive(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    start_time = models.DateTimeField(auto_now_add=True, null=True)
    end_time = models.DateTimeField(null=True)

    constraints = models.ForeignKey(Settings, on_delete=models.CASCADE)

    started = models.BooleanField(default=False)

    def __str__(self):
        return 'Interactive {}'.format(self.id)

    @property
    def group_channel(self):
        return Group('game-{}'.format(self.id))

    def broadcast(self, action, msg):
        packet = json.dumps({
            'action': action,
            'text': msg,
        })
        self.group_channel.send({'text': packet})

    def user_channel(self, user):
        if user.is_authenticated:
            return Group('user-{}-{}'.format(self.id, user.username))
        else:
            return None
