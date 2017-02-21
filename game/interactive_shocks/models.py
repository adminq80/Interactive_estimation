import json

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from channels import Group
from django.utils import timezone

from game.round.models import Round


class Settings(models.Model):
    """
    :var alpha is number of rounds to take into account when making score calculation
    """
    max_users = models.PositiveSmallIntegerField()
    min_users = models.PositiveSmallIntegerField()

    max_following = models.PositiveSmallIntegerField()
    min_following = models.PositiveSmallIntegerField()

    score_lambda = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    max_rounds = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return "Settings: users({},{}), following({},{})".format(self.min_users, self.max_users,
                                                                 self.min_following, self.max_following
                                                                 )

    def save(self, *args, **kwargs):
        if self.max_users > self.min_users and self.max_users > self.max_following > self.min_following:
            return super(Settings, self).save(*args, **kwargs)
        raise ValidationError("Didn't meet logical constraints for the Settings model")

    class Meta:
        verbose_name_plural = 'Settings'


class InteractiveShocksRound(Round):
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, symmetrical=False, related_name='shock_following')
    # followers = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', null=True)

    influenced_guess = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    game = models.ForeignKey('InteractiveShocks', null=True, on_delete=models.CASCADE)
    outcome = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def round_data(self):
        data = super(InteractiveShocksRound, self).round_data()
        data['game_id'] = self.game.id
        data['condition'] = 'interactive'
        data['revised_guess'] = self.influenced_guess
        data['game_size'] = self.game.constraints.max_users
        data['following_capacity'] = self.game.constraints.max_following
        data['following'] = []
        for u in self.following.all():
            current_round = InteractiveShocksRound.objects.get(user=u, round_order=data['round_id'])
            data['following'].append({'username': u.username,
                                      'independent_guess': current_round.guess,
                                      'revised_guess': current_round.influenced_guess,
                                      })
        return data

    def get_influenced_guess(self):
        return float(self.influenced_guess) if self.influenced_guess else -1


class InteractiveShocks(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)

    constraints = models.ForeignKey(Settings, on_delete=models.CASCADE)

    started = models.BooleanField(default=False)

    def __str__(self):
        return 'Interactive {}'.format(self.id)

    @property
    def group_channel(self):
        return Group('game-{}'.format(self.id))

    def broadcast(self, **kwargs):
        packet = json.dumps(kwargs)
        self.group_channel.send({'text': packet})

    def user_channel(self, user):
        return Group('user-{}-{}'.format(self.id, user.id))

    def user_send(self, user, **kwargs):
        packet = json.dumps(kwargs)
        return self.user_channel(user).send({'text': packet})


class Survey(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    game = models.CharField(max_length=20, blank=True, null=True)
    age = models.PositiveSmallIntegerField(null=True)
    gender = models.CharField(max_length=30, blank=True, null=True)
    feedback = models.TextField(null=True)

    def __str__(self):
        return self.username

    def dump(self):
        return {
            'user': self.username or '',
            'game': self.game or '',
            'age': self.age or '',
            'gender': self.gender or '',
            'feedback': self.feedback or '',
        }
