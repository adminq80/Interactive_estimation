from random import choice

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import RoundForm
from game.round.models import Round, Plot


# Create your views here.
@login_required(login_url='/')
def play(request):
    u = request.user
    matches = {i.board.pk for i in Round.objects.filter(user=u)}

    if len(matches) == Plot.objects.count():
        pass
        #return redirect('/done')

    plots = Plot.objects.exclude(pk__in=matches)

    plot = choice(plots)
    form = RoundForm()

    return render(request, 'round/play.html', {'round': plot, 'form': form})
