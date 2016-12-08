from decimal import Decimal
from django.db import models
from django.conf import settings


# Create your models here.
from django.utils import timezone

from game.contrib.calculate import calculate_score
from game.control.models import Control


class Plot(models.Model):
    plot = models.URLField(unique=True)
    answer = models.DecimalField(max_digits=3, decimal_places=2)
    duration = models.TimeField(null=True)
    batch = models.PositiveSmallIntegerField(null=True)

    non_stationary_seq = models.PositiveSmallIntegerField(null=True)
    stationary_seq = models.PositiveSmallIntegerField(null=True)
    seq = models.PositiveSmallIntegerField(null=True)  # not efficient but it will do the job

    def __str__(self):
        return self.plot


class Round(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)

    round_order = models.PositiveSmallIntegerField()
    guess = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    # start time of the round
    # end time of the round
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)

    # todo: change control treatment
    score = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal(0))

    def __str__(self):
        return self.user.username

    def round_data(self):
        played_rounds = self.__class__.objects.filter(user=self.user, round_order__lte=self.round_order,
                                                      guess__gte=Decimal(0.0))
        score = calculate_score(played_rounds)
        this_round = self.__class__.objects.filter(user=self.user, round_order=self.round_order,
                                                   guess__gte=Decimal(0.0))
        round_score = calculate_score(this_round)
        if self.end_time and self.start_time:
            duration = (self.end_time - self.start_time).seconds
        else:
            duration = None

        data = {'username': self.user.username, 'cumulative_score': score,
                'avatar': self.user.avatar, 'task_path': self.plot.plot, 'correct_answer': self.plot.answer,
                'independent_guess': self.guess, 'round_id': self.round_order, 'score': round_score,
                'game_id': None, 'condition': None, 'following': None, 'revised_guess': None,
                'duration': duration, 'start_time': self.start_time, 'end_time': self.end_time,
                'batch': self.plot.batch or 0,
                }

        if self.user.game_type == 'c':
            game = Control.objects.get(user=self.user)
            data['game_id'] = game.id
            data['condition'] = 'control'

        return data

    def get_guess(self):
        return float(self.guess) if self.guess else -1

    class Meta:
        unique_together = (('user', 'round_order',),)
