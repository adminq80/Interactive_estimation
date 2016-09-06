from django.shortcuts import render, redirect

from .forms import PlayerForm
from .models import Player


# Create your views here.
def start(request):
    form = PlayerForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            p = form.save(commit=True)
            print(p.email)
            return redirect('/')
    return render(request, 'users/start.html', {'form': form})
