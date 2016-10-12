from django.db import models
from django.conf import settings

# from game.round.models import Round


# Create your models here.
class Control(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    start_time = models.DateTimeField(auto_now_add=True, null=True)
    end_time = models.DateTimeField(null=True)
    score = models.DecimalField(max_digits=8, decimal_places=4, default=0.00)

    instruction = models.BooleanField(default=False)
    exist_survey = models.BooleanField(default=False)
    check = models.PositiveIntegerField(default=0)
    check_done = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Survey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.OneToOneField(Control)
    age = models.PositiveSmallIntegerField(null=True)
    gender = models.CharField(max_length=10, choices=(('m', 'Male'),
                                                      ('f', 'Female'),
                                                      ), blank=True, null=True)
    feedback = models.TextField(null=True)

    def __str__(self):
        return self.user.username
