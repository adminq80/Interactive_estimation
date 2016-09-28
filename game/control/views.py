from random import choice
from decimal import Decimal

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from game.contrib.calculate import calculate_score

from game.round.models import Round, Plot

from .forms import RoundForm
from .models import Control


# Create your views here.
@login_required(login_url='/')
def play(request):
    u = request.user

    played_rounds = Round.objects.filter(user=u)
    plot_pks = {i.plot.pk for i in played_rounds}

    score = calculate_score(played_rounds)
    remaining = Plot.objects.count() - len(plot_pks)

    if remaining == 0:
        c = Control.objects.get(user=u)
        c.score = Decimal(score)
        c.end_time = timezone.now()
        c.save()
        return redirect('users:done')

    if request.session.get('PLOT'):  # Or None
        plot = Plot.objects.get(plot=request.session.get('PLOT'))
    else:
        plots = Plot.objects.exclude(pk__in=plot_pks)
        plot = choice(plots)

    request.session['PLOT'] = plot.plot
    form = RoundForm()

    return render(request, 'control/play.html', {'round': plot, 'form': form, 'score': score, 'remaining': remaining})

# TO-DO score, plots remaining off by one
@login_required(login_url='/')
def submit_answer(request):
    if request.method == 'POST':
        form = RoundForm(request.POST)
        if form.is_valid():
            guess = form.cleaned_data['guess']
            plot = request.session.get('PLOT', None)

            played_rounds = Round.objects.filter(user=request.user)
            plot_pks = {i.plot.pk for i in played_rounds}

            score = calculate_score(played_rounds)
            remaining = Plot.objects.count() - len(plot_pks)
            p = Plot.objects.get(plot=plot)
            Round.objects.create(user=request.user, guess=guess, plot=p, round_order=played_rounds.count()).save()
            request.session.pop('PLOT')
            return render(request, 'control/answer.html', {'round': p, 'guess': guess, 'score': score, 'remaining': remaining})

    return redirect('control:play')
