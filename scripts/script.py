import json

from game.board.models import Board


def run(*arg, **kwargs):
    d = filter(lambda x: x['exp_use'], json.loads(open('../correlation_stash.json').read())['data'])

    plots = map(lambda x: (x['id'], x['cor']), d)
    for p in plots:
        Board.objects.create(plot='{}.png'.format(p[0]), answer=p[1]).save()
