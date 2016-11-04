import json
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from game.round.models import Round
from game.control.models import Survey


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class Command(BaseCommand):

    def handle(self, *args, **options):
        rounds = []
        for i in Round.objects.all():
            user = i.user.username
            try:
                s = Survey.objects.get(user=user)
                survey = s.dump()
            except Survey.DoesNotExist:
                survey = None
            data = i.round_data()
            data['survey'] = survey
            rounds.append(data)
        print(json.dumps(rounds, cls=DecimalEncoder))
