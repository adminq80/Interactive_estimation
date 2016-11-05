from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.utils import timezone

# from game.round.models import Round


class Setting(models.Model):
    max_rounds = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    batch_size = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return "Setting: max_rounds: {} ".format(self.max_rounds)


# Create your models here.
class Control(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True)
    score = models.DecimalField(max_digits=8, decimal_places=4, default=0.00)

    instruction = models.BooleanField(default=False)
    exist_survey = models.BooleanField(default=False)
    check = models.PositiveIntegerField(default=0)
    check_done = models.BooleanField(default=False)

    max_rounds = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], null=True)
    batch_size = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], null=True)

    def __str__(self):
        return self.user.username


class Survey(models.Model):
    user = models.CharField(max_length=255, blank=True, null=True)
    game = models.CharField(max_length=255, blank=True, null=True)
    age = models.PositiveSmallIntegerField(null=True)
    gender = models.TextField(null=True)
    feedback = models.TextField(null=True)
    bugs = models.TextField(null=True)
    pay = models.TextField(null=True)
    education = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '{}@{}'.format(self.user, self.game)

    def dump(self):
        return {
            'user': self.user or '',
            'game': self.game or '',
            'age': self.age or '',
            'gender': self.gender or '',
            'feedback': self.feedback or '',
            'bugs': self.bugs or '',
            'pay': self.pay or '',
            'education': self.education or '',
        }
