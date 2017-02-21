import math


def get_guess(rnd):
    if hasattr(rnd, 'influenced_guess'):
        return rnd.influenced_guess
    return rnd.guess


def get_error(rnd):
    guess = get_guess(rnd)
    if guess is None:
        return 0.0
    answer = rnd.plot.answer
    error = math.fabs(answer - guess)
    return (1.0 - error) ** 2


def score_gain(rounds):
    l = [get_error(r) for r in rounds]
    score = sum(l[:-1])  # Sum all errors except the last one
    gain = l[-1]
    return round(float(score), 2), round(float(gain), 2)


def calculate_score(rounds):
    score = sum([get_error(r) for r in rounds])
    return round(float(score), 2)
