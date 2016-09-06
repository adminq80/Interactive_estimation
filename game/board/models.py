from django.db import models

from game.users.models import User


class Board(models.Model):
    # player = models.ManyToManyField(User, through='Match')
    plot = models.URLField()
    answer = models.DecimalField(max_digits=4, decimal_places=3)

    def __str__(self):
        return '{}'.format(self.answer)


class Match(models.Model):
    # This class is a relational class meaning it will hold the status of each board
    player = models.ForeignKey(User)
    board = models.ForeignKey(Board)
    guess = models.DecimalField(max_digits=4, decimal_places=3)

    def __str__(self):
        return self.player.username
