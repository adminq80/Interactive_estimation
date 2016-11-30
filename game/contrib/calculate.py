import math


def calculate_score(rounds):
    """
    :param rounds:
    :return score:

     cumScore = 0
     if corr-guess =! 0 :
        cumScore+=1/sqrt((corr-guess)**2)
     else:
        cumScore += 100
    """
    score = 0.0
    for r in rounds:
        if hasattr(r, 'influenced_guess'):
            guess = r.influenced_guess
        else:
            guess = r.guess
        if guess is None:
            continue
        answer = r.plot.answer
        error = math.fabs(answer - guess)
        score += (1.0-error)**2
            
    return round(float(score), 2)
