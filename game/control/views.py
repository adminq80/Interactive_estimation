from math import fabs
from random import choice, shuffle
from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction

from game.contrib.random_user import random_user

from game.round.models import Round, Plot

from .forms import RoundForm, CheckForm, ExitSurvey
from .models import Control, Setting


def avatar(exclude=set()):
    avatars = {'bee.png', 'bird.png', 'cat.png', 'cow.png', 'elephant.png', 'lion.png', 'pig.png', 'cute_cat.png',
               'cute_panda.png', 'cute_giraffe.png', 'cute_owl.png', 'cute_cat_color.png', 'smart_dog.png',
               'smart_fox.png', 'smart_monkey.png', 'smart_deer.png'
               }
    return choice(list(avatars.symmetric_difference(exclude)))


def assign(request):
    if request.method == 'POST':
        return redirect('control:instruction')
    return render(request, 'pages/home2.html')


SECONDS = 30
DELAY = 7


# Create your views here.
@login_required(login_url='control:instruction')
def play(request):

    u = request.user
    if u.game_type != 'control':
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
            if u.level == 'e':
                track = 1
            elif u.level == 'm':
                track = 2
            elif u.level == 'h':
                track = 3
            else:
                track = 1
                print('Error no LEVEL was found on the user object')
            plots = Plot.objects.filter(non_stationary_seq=track).order_by('seq')
            plot = plots[0]
            data = {'track': track, 'remaining': game.batch_size-1}
        else:
            data = cache.get('control_user_{}'.format(u.id))
            plots = Plot.objects.filter(non_stationary_seq=data.get('track')).order_by('seq')
            plot_seq = game.batch_size - data['remaining']
            plot = plots[plot_seq]
            data['remaining'] -= 1
        cache.set('control_user_{}'.format(u.id), data)
        with transaction.atomic():
            r, created = Round.objects.get_or_create(user=u, plot=plot, round_order=len(plot_pks))
        if created:
            extra = {'round_id': r.id}
        else:
            extra = None
            print('Tried to create a round with an old plot or round_order {}'.format(r))
    else:
        extra = None
        plot = Plot.objects.get(id=round_data.get('plot_id'))

    d = cache.get('control-{}'.format(game.id))
    payload = {
        'score': 0.0,
    }

    if extra:
        # new round was found
        payload = {
            'new_round': False,
            'plot_id': plot.id,
            'remaining': remaining - 1,
            'currentRound': len(plot_pks) + 1,
            'score': request.user.get_score,
        }
        payload.update(extra)

    if d:
        # there was new data  before
        if payload.get('currentRound', False):
            if payload.get('currentRound') > d.get('currentRound'):
                d = payload
            else:
                print('Cache has recent data than payload')
                return redirect('control:play')
        else:
            print('Found data in the cache and Payload is None')
            r = Round.objects.get(id=d.get('round_id'))
            if (r.start_time + timedelta(seconds=SECONDS + DELAY)) < timezone.now():
                cache.set('control-{}'.format(game.id), None)
                return redirect('control:play')
    else:
        d = payload

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

            if (r.start_time + timedelta(seconds=SECONDS + DELAY)) < timezone.now():
                guess = -1

            if r.guess is None:
                r.guess = guess
                r.score = score
                r.end_time = timezone.now()
                r.save()
            else:
                print("Either r.guess was found or the user didn't submit the answer within the allowed time")
                return redirect('control:play')
            round_data['round'] = plot
            round_data['guess'] = r.guess
            round_data['score'], round_data['bonus'] = request.user.get_score_and_gain
            if r.guess >= 0:
                round_data['difference'] = fabs(r.guess - plot.answer)
            round_data['new_round'] = True
            cache.set('control-{}'.format(game.id), round_data)
            return render(request, 'control/answer.html', round_data)

    return redirect('control:play')


def instruction(request):
    if request.user.is_anonymous:
        u, password = random_user('control', length=60)
        u.avatar = avatar()
        u.save()
        settings = Setting.objects.all()
        if settings.count() != 0:
            setting = settings.order_by('?')[0]
        else:
            setting = Setting.objects.create(max_rounds=10, batch_size=5)
        types = setting.types.split(',')
        shuffle(types)
        try:
            d = {
                '0': 'e',
                '1': 'm',
                '2': 'h',
            }
            t = types.pop(0)
            u.level = d[t]
            u.save()
            setting.types = ','.join(types)
            setting.save()
        except AttributeError:
            print('Control types array is empty')
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
