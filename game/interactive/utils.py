from random import choice


def avatar(exclude=set()):
    avatars = {'bee.png', 'bird.png', 'cat.png', 'cow.png', 'elephant.png', 'lion.png', 'pig.png', 'cute_cat.png',
               'cute_panda.png', 'cute_giraffe.png', 'cute_owl.png', 'cute_cat_color.png', 'smart_dog.png',
               'smart_fox.png', 'smart_monkey.png', 'smart_deer.png'
               }
    return choice(list(avatars.symmetric_difference(exclude)))
