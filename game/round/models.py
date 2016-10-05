from django.db import models
from django.conf import settings


# Create your models here.
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
    guess = models.DecimalField(max_digits=3, decimal_places=2)

    # start time of the round
    # end time of the round

    def __str__(self):
        return self.user.username
