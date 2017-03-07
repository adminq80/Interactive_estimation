import json
import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from game.interactive_shocks.models import InteractiveShocks, InteractiveShocksRound, Survey


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

        for game in InteractiveShocks.objects.all():
            for u in game.users.all():
                rounds = InteractiveShocksRound.objects.filter(user=u)
                if rounds.count() < 1:
                    continue
                d = {'user': u.username,
                     'final_score': u.get_score,
                     'condition': 'dynamic',
                     'time_created': u.date_joined,
                     'game_id': game.id,
                     'unanswered': rounds.filter(guess__lt=0).count(),
                     }
                try:
                    s = Survey.objects.get(username=u.username)
                    survey = s.dump()
                except Survey.DoesNotExist:
                    survey = None
                d['survey'] = survey
                d['rounds'] = [r.round_data() for r in rounds]
                # d['completed_hit'] = c.max_rounds == len(d['rounds'])
                users.append(d)
        print(json.dumps(users, cls=DecimalEncoder))
