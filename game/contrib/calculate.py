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
        error = math.fabs(answer - guess)
        #if calc == 0.0:
        #    score += 100
        #else:
        #    if guess > 0:
        #        score += 1/math.sqrt(calc**2)
        score += (1.0-error)**2
            
    return round(score, 2)
