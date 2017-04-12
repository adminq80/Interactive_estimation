import json

from django.core.management.base import BaseCommand
from game.round.models import Round
from game.control.models import Control, Survey

from game.contrib.decimal_encoder import DecimalEncoder


class Command(BaseCommand):
    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--ids', nargs='+', type=int)
        group.add_argument('--greater', nargs=1, type=int)
        parser.add_argument('--limit', nargs=1, type=int)

    def handle(self, *args, **options):
        if options['greater']:
            qs = Control.objects.filter(pk__gte=options['greater'][0])
            if options['limit']:
                qs = qs[:options['limit'][0]]
        else:
            qs = Control.objects.filter(pk__in=set(options['ids']))

        games = []
        for game in qs:
            user = game.user
            rounds = Round.objects.filter(user=user)
            if rounds.count() < 1: continue
            d = {'user': user.username,
                 'final_score': user.get_score,
                 'condition': 'control',
                 'time_created': user.date_joined,
                 'game_id': game.id,
                 'unanswered': rounds.filter(guess__lt=0).count(),
                 }
            try:
                s = Survey.objects.get(user=user.username)
                survey = s.dump()
            except Survey.DoesNotExist:
                survey = None
            d['survey'] = survey
            d['rounds'] = [r.round_data() for r in rounds]
            if game.max_rounds == len(d['rounds']):
                d['hit_status'] = 'completed'
            else:
                d['hit_status'] = 'disconnected'
            games.append(d)
        print(json.dumps(games, cls=DecimalEncoder))
