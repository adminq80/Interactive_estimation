from django import forms
from django.core.exceptions import ValidationError

from game.round.models import Plot
from .models import Survey, Settings


class RoundForm(forms.Form):
    guess = forms.DecimalField(required=True, max_digits=3, decimal_places=2)


class ExitSurvey(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['gender', 'age', 'feedback']

    def __init__(self, *args, **kwargs):
        super(ExitSurvey, self).__init__(*args, **kwargs)
        for f in ['gender', 'age', 'feedback']:
            self.fields[f].required = False


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['max_users', 'min_users', 'score_lambda', 'max_following', 'min_following', 'max_rounds',
                  'prompt_seconds', 'kickout_seconds', 'max_prompts', 'minutes_mode', 'prompt_sound_interval',]

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('max_users', 0) > cleaned_data.get('max_following', 0) > \
                cleaned_data.get('min_following', 0) and cleaned_data.get('max_users', 0) > \
                cleaned_data.get('min_users', 0) and cleaned_data.get('score_lambda', 1) and \
                                Plot.objects.all().count() >= cleaned_data.get('max_rounds') > 0:
            return cleaned_data

        raise ValidationError("Didn't meet logical constraints for the Settings model")


class CheckForm(forms.Form):
    Q1_choices = (('1', 'Estimate the correlation of two variables'),
                  ('2', 'Count the points in the picture'),
                  )
    q1 = forms.ChoiceField(label='Your goal in the game is to', widget=forms.RadioSelect(attrs={'class': 'form-group'}),
                           choices=Q1_choices)

    q2 = forms.DecimalField(label='The maximum correlation possible is', widget=forms.TextInput)

    q4 = forms.ChoiceField(label='In this game, all correlations will be', widget=forms.RadioSelect,
                           choices=(('1', 'Negative or positive'),
                                    ('2', 'Only positive'),
                                    ))

    q5 = forms.ChoiceField(label='You will get a chance to change your estimate after your initial guess.',
                           widget=forms.RadioSelect, choices=(('1', 'True'),
                                                              ('2', 'False'),
                                                              ))

    q6 = forms.ChoiceField(label='Have you participated in this study before?', widget=forms.RadioSelect,
                           choices=(('1', 'No'),
                                    ('2', 'Yes'),
                                    ))

    def clean(self):
        cleaned_data = super(CheckForm, self).clean()
        q1 = cleaned_data.get('q1')
        q2 = float(cleaned_data.get('q2'))
        q4 = cleaned_data.get('q4')
        q5 = cleaned_data.get('q5')
        q6 = cleaned_data.get('q6')

        if q1 == '1' and q2 == 1 and q4 == '2' and q5 == '1' and q6 == '1':
            return cleaned_data
        raise forms.ValidationError('Some answers are wrong .. please go back and read the instructions carefully')
