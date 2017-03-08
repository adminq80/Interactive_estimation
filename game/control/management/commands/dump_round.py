import json

from django.core.management.base import BaseCommand
from game.round.models import Round
from game.control.models import Control, Survey
from game.users.models import User

from game.contrib.decimal_encoder import DecimalEncoder


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = []
        for u in User.objects.filter(game_type='control'):
            rounds = Round.objects.filter(user=u)
            if rounds.count() < 1:
                continue
            try:
                c = Control.objects.get(user=u)
            except Control.DoesNotExist:
                continue
            d = {'user': u.username,
                 'final_score': u.get_score,
                 'condition': 'control',
                 'time_created': u.date_joined,
                 'game_id': c.id,
                 'unanswered': rounds.filter(guess__lt=0).count(),
                 }
            try:
                s = Survey.objects.get(user=u.username)
                survey = s.dump()
            except Survey.DoesNotExist:
                survey = None
            d['survey'] = survey
            d['rounds'] = [r.round_data() for r in rounds]
            if c.max_rounds == len(d['rounds']):
                d['hit_status'] = 'completed'
            else:
                d['hit_status'] = 'disconnected'
            users.append(d)
        print('Users = {}'.format(len(users)))
        print(json.dumps(users, cls=DecimalEncoder))
