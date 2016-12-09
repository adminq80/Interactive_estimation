# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from game.contrib.calculate import calculate_score
from game.interactive.models import InteractiveRound
from game.interactive_shocks.models import InteractiveShocksRound
from game.interactive_static.models import InteractiveStaticRound
from game.round.models import Round


@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    game_type = models.CharField(_('User Type'), max_length=10)
    avatar = models.URLField(null=True)
    user_level = models.CharField(max_length=10, null=True, blank=True)  # level should be either 'e', 'm', or 'h'

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    @property
    def get_avatar(self):
        return 'images/avatars/{}'.format(self.avatar)

    @property
    def get_score(self):
        if self.game_type == 'i':
            cls = InteractiveRound
        elif self.game_type == 'c':
            cls = Round
        elif self.game_type == 'shocks':
            cls = InteractiveShocksRound
        elif self.game_type == 'static':
            cls = InteractiveStaticRound
        else:
            raise NotImplemented('Not Implemented')

        played_rounds = cls.objects.filter(user=self, guess__gte=Decimal(0.0))
        return calculate_score(played_rounds)

    @property
    def level(self):
        return self.user_level

    @level.setter
    def level(self, val):
        if val in ['e', 'm', 'h']:
            self.user_level = val
            self.save()
        else:
            raise TypeError('level must be e, m, or h')
