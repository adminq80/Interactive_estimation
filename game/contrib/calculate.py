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
        guess = r.guess
        answer = r.plot.answer
        calc = answer - guess
        if calc != 0.0:
            score += 1/math.sqrt(calc**2)
        else:
            score += 100
    return round(score, 2)
