from django.db import models
from django.conf import settings

# from game.round.models import Round


# Create your models here.
class Control(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.user.username
