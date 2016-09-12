from django.shortcuts import render

from channels import Group


# Create your views here.
def lobby(request):
    return render(request, 'interactive/lobby.html')


def play(request):
    pass


def submit_answer(request):
    pass


def view_answers(request):
    pass
