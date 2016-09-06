from random import choice
from django.shortcuts import render, redirect
from django.db.models import Q

from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from .models import Board, Match
from .forms import BoardForm


# Create your views here.
@login_required(login_url='/')
def play(request):
    u = request.user
    matches = {i.board.pk for i in Match.objects.filter(player=u)}

    if len(matches) == Board.objects.count():
        return redirect('/done')

    boards = Board.objects.exclude(pk__in=matches)

    board = choice(boards)
    form = BoardForm()

    return render(request, 'board/match.html', {'form': form, 'board': board})


@login_required(login_url='/')
def submit(request):

    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            # Got a guess
            guess = form.cleaned_data['guess']
            plot = form.cleaned_data['plot']
            b = Board.objects.get(plot=plot)
            Match.objects.create(player=request.user, guess=guess, board=b).save()
            return render(request, 'board/answer.html', {'board': b, 'guess': guess})

    return redirect(reverse('board:match'))
