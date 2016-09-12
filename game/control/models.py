from django.db import models
from django.conf import settings

# from game.round.models import Round


# Create your models here.
class Control(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True, null=True)
    end_time = models.DateTimeField(null=True)
    score = models.DecimalField(max_digits=8, decimal_places=4, default=0.00)

    def __str__(self):
        return self.user.username
