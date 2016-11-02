from random import choice

from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from game.contrib.random_user import random_user

from game.round.models import Round, Plot

from .forms import RoundForm, CheckForm, ExitSurvey
from .models import Control, Setting


def assign(request):
    if request.method == 'POST':
        return redirect('control:instruction')
    return render(request, 'pages/home2.html')


# Create your views here.
@login_required(login_url='control:instruction')
def play(request):

    u = request.user
    if u.game_type != 'c':
        return redirect('/')

    game = Control.objects.get(user=u)

    if not game.check_done:
        if game.check >= 4:
            return redirect('control:exit')
        return redirect('control:instruction')

    played_rounds = Round.objects.filter(user=u)
    plot_pks = {i.plot.pk for i in played_rounds}

    remaining = int(game.max_rounds or 10) - len(plot_pks)

    if remaining == 0:
        game.end_time = timezone.now()
        game.save()
        return redirect('control:exit')

    round_data = cache.get('control-{}'.format(game.id))
    if round_data is None:
        # new user
        round_data = {'new_round': True}

    if round_data.get('new_round', False):
        if len(plot_pks) == 0:
            # first round no batch has been assigned yet
            plots = Plot.objects.all()
            plot = choice(plots)
            batch = plot.batch
            data = {'played_batches': [batch], 'current_batch': batch, 'remaining': game.batch_size-1}
        else:
            data = cache.get('control_user_{}'.format(u.id))
            if data.get('remaining') == 0:
                # assign to new batch
                print('ONE')
                print(data)
                plots = Plot.objects.exclude(batch__in=data.get('played_batches', [])).exclude(pk__in=plot_pks)
                print(plots)
                plot = choice(plots)
                batch = plot.batch
                data['played_batches'].append(batch)
                data['current_batch'] = batch
                data['remaining'] = game.batch_size - 1
            else:
                print('TWO')
                print(data)
                plots = Plot.objects.exclude(pk__in=plot_pks).filter(batch=data.get('current_batch'))
                print('PLOT')
                print(plots)
                plot = choice(plots)
                data['remaining'] -= 1
        cache.set('control_user_{}'.format(u.id), data)
        Round.objects.get_or_create(user=u, plot=plot, round_order=len(plot_pks))
    else:
        plot = Plot.objects.get(id=round_data.get('plot_id'))

    d = {
        'new_round': False,
        'plot_id': plot.id,
        'remaining': remaining - 1,
        'currentRound': len(plot_pks) + 1,
    }
    cache.set('control-{}'.format(game.id), d)

    form = RoundForm()
    d['form'] = form
    d['round'] = plot
    return render(request, 'control/play.html', d)


# TODO: score, plots remaining off by one
@login_required(login_url='/')
def submit_answer(request):
    if request.method == 'POST':
        form = RoundForm(request.POST)
        if form.is_valid():
            guess = form.cleaned_data['guess']
            game = Control.objects.get(user=request.user)
            try:
                round_data = cache.get('control-{}'.format(game.id))
            except ValueError:
                round_data = {'plot_id': 1}
                print("Couldn't load from cache??")
            score = request.user.get_score
            plot = Plot.objects.get(id=round_data.get('plot_id'))
            r = Round.objects.get(user=request.user, plot=plot, round_order=round_data.get('currentRound')-1)

            if r.guess is None:
                r.guess = guess
                r.score = score
                r.end_time = timezone.now()
                r.save()
            round_data['round'] = plot
            round_data['guess'] = r.guess
            round_data['score'] = r.score
            round_data['new_round'] = True
            cache.set('control-{}'.format(game.id), round_data)
            return render(request, 'control/answer.html', round_data)

    return redirect('control:play')


def instruction(request):
    if request.user.is_anonymous:
        u, password = random_user('c', length=60)
        settings = Setting.objects.all()
        if settings.count() != 0:
            setting = settings.order_by('?')[0]
        else:
            setting = Setting.objects.create(max_rounds=10, batch_size=5)
        Control.objects.create(user=u, max_rounds=setting.max_rounds, batch_size=setting.batch_size)
        u = authenticate(username=u.username, password=password)
        login(request, u)

    u = request.user
    game = Control.objects.get(user=u)
    game.instruction = True
    game.save()
    
    form = CheckForm(request.POST or None)
    check_count = game.check
    if check_count >= 4:
        return redirect('control:exit')

    if request.method == 'POST':
        if form.is_valid():
            game = Control.objects.get(user=u, instruction=True, check=check_count)
            game.check_done = True
            game.save()
            return redirect('control:play')
        else:
            try:
                game = Control.objects.get(user=u, instruction=True)
                game.check += 1
                game.save()
            except Control.DoesNotExist:
                return redirect('control:instruction')

    return render(request, 'control/instructions.html', {'form': form})


@login_required(login_url='/')
def exit_survey(request):
    game = Control.objects.get(user=request.user)
    form = ExitSurvey(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user.username
            instance.game = game.id
            instance.save()
            return render(request, 'control/done.html')

    return render(request, 'control/survey.html', {'form': form, 'score':
        round(float(request.user.get_score or 0.0) / 10.0, 2)})
