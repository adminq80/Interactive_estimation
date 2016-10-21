from decimal import Decimal
from django.db import models
from django.conf import settings


# Create your models here.
from game.contrib.calculate import calculate_score
from game.control.models import Control


class Plot(models.Model):
    plot = models.URLField()
    answer = models.DecimalField(max_digits=3, decimal_places=2)
    duration = models.TimeField(null=True)

    def __str__(self):
        return self.plot


class Round(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)

    round_order = models.PositiveSmallIntegerField()
    guess = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('NaN'))

    # start time of the round
    # end time of the round
    start_time = models.DateTimeField(auto_now=True, null=True)
    end_time = models.DateTimeField(null=True)

    # todo: add cumulative and round scores
    score = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal(0))

    def __str__(self):
        return self.user.username

    def round_data(self):
        played_rounds = self.__class__.objects.filter(user=self.user, round_order__lte=self.round_order,
                                                      guess__gte=Decimal(0.0))
        score = calculate_score(played_rounds)
        this_round = self.__class__.objects.filter(user=self.user, round_order=self.round_order,
                                                   guess__gte=Decimal(0.0))
        round_score = calculate_score(this_round)

        data = {'username': self.user.username, 'cumulative_score': score,
                'avatar': self.user.avatar, 'task_path': self.plot.plot, 'correct_answer': self.plot.answer,
                'independent_guess': self.guess, 'round_id': self.round_order, 'score': round_score,
                'game_id': None, 'condition': None, 'following': None, 'revised_guess': None
                }

        if self.user.game_type == 'c':
            game = Control.objects.get(user=self.user)
            data['game_id'] = game.id
            data['condition'] = 'control'

        return data

    class Meta:
        unique_together = (('user', 'round_order',),)
