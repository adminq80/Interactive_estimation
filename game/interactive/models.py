import json
import uuid

from django.db import models
from django.conf import settings

from channels import Group

from game.round.models import Round


class Settings(models.Model):
    max_users = models.PositiveSmallIntegerField()
    min_users = models.PositiveSmallIntegerField()

    max_following = models.PositiveSmallIntegerField()
    min_following = models.PositiveSmallIntegerField()

    def __str__(self):
        return "Settings: users({},{}), following({},{})".format(self.min_users, self.max_users,
                                                                 self.min_following, self.max_following
                                                                 )

    class Meta:
        verbose_name_plural = 'Settings'


class InteractiveRound(Round):
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, symmetrical=False, related_name='following')
    # followers = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', null=True)

    influenced_guess = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    game = models.ForeignKey('Interactive', null=True, on_delete=models.CASCADE)
    outcome = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def round_data(self):
        data = super(InteractiveRound, self).round_data()
        data['game_id'] = self.game.id
        data['condition'] = 'interactive'
        data['revised_guess'] = self.influenced_guess
        data['game_size'] = self.game.constraints.max_users
        data['following_capacity'] = self.game.constraints.max_following
        data['following'] = []
        for u in self.following.all():
            current_round = InteractiveRound.objects.get(user=u, round_order=data['round_id'])
            data['following'].append({'username': u.username,
                                      'independent_guess': current_round.guess,
                                      'revised_guess': current_round.influenced_guess,
                                      })
        return data


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
        return 'user-{}-{}'.format(self.id, user.id)


class Survey(models.Model):
    # user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='influenced_users')
    username = models.CharField(max_length=255, blank=True, null=True)
    game = models.OneToOneField(Interactive)
    age = models.PositiveSmallIntegerField(null=True)
    gender = models.CharField(max_length=10, choices=(('m', 'Male'),
                                                      ('f', 'Female'),
                                                      ), blank=True, null=True)
    feedback = models.TextField(null=True)

    def __str__(self):
        return self.user.username
