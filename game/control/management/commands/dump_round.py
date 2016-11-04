import json
import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from game.round.models import Round
from game.control.models import Control, Survey
from game.users.models import User


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        if isinstance(o, datetime.timedelta):
            return o.seconds
        return super(DecimalEncoder, self).default(o)


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = []
        for u in User.objects.filter(game_type='c'):
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
            d['completed_hit'] = c.max_rounds == len(d['rounds'])
            users.append(d)
        with open('control_data.json', 'w') as f:
            f.write(json.dumps(users, cls=DecimalEncoder))
