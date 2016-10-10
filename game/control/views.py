from random import choice
from decimal import Decimal

from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from game.contrib.calculate import calculate_score
from game.contrib.random_user import random_user

from game.round.models import Round, Plot

from .forms import RoundForm
from .models import Control


def assign(request):
    if request.method == 'POST':
        return redirect('control:play')
    return render(request, 'pages/home2.html')


# Create your views here.
def play(request):

    if request.user.is_anonymous:
        u, password = random_user('c', length=130)
        Control.objects.create(user=u)
        u = authenticate(username=u.username, password=password)
        login(request, u)
    else:
        u = request.user
        if u.game_type != 'c':
            return redirect('/')

    game = Control.objects.get(user=u)
    if not game.instruction:
        return redirect('control:instruction')

    played_rounds = Round.objects.filter(user=u)
    plot_pks = {i.plot.pk for i in played_rounds}

    score = calculate_score(played_rounds)
    currentRound = len(plot_pks)
    remaining = Plot.objects.count() - currentRound

    if remaining == 0:
        c = Control.objects.get(user=u)
        c.score = Decimal(score)
        c.end_time = timezone.now()
        c.save()
        return redirect('control:exit_survey')

    if request.session.get('PLOT'):  # Or None
        plot = Plot.objects.get(plot=request.session.get('PLOT'))
    else:
        plots = Plot.objects.exclude(pk__in=plot_pks)
        plot = choice(plots)

    request.session['PLOT'] = plot.plot
    form = RoundForm()

    return render(request, 'control/play.html', {'round': plot, 'form': form, 'score': score, 'remaining': remaining, 'currentRound': currentRound})


# TODO: score, plots remaining off by one
@login_required(login_url='/')
def submit_answer(request):
    if request.method == 'POST':
        form = RoundForm(request.POST)
        if form.is_valid():
            guess = form.cleaned_data['guess']
            plot = request.session.get('PLOT', None)

            p = Plot.objects.get(plot=plot)
            played_rounds = Round.objects.filter(user=request.user)
            
            Round.objects.create(user=request.user, guess=guess, plot=p, round_order=played_rounds.count()).save()
            request.session.pop('PLOT')

            plot_pks = {i.plot.pk for i in played_rounds}
            
            score = calculate_score(played_rounds)
            currentRound = len(plot_pks)
            remaining = Plot.objects.count() - currentRound
            return render(request, 'control/answer.html', {'round': p, 'guess': guess, 'score': score, 'remaining': remaining, 'currentRound': currentRound})

    return redirect('control:play')


@login_required(login_url='/')
def instruction(request):
    u = request.user
    game = Control.objects.get(user=u)
    game.instruction = True
    game.save()
    # if request.method == 'POST':
    #     if form.is_valid():
    #         game.instruction = True
    #         game.save()
    #     else:
    #         pass
    # else:
    #     pass
    return render(request, 'control/instructions.html')

@login_required(login_url='/')
def check(request):
    return render(request, 'control/check.html')


@login_required(login_url='/')
def exit_survey(request):
    return render(request, 'control/survey.html')
