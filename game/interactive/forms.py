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
        fields = ['max_users', 'min_users', 'score_lambda', 'max_following', 'min_following', 'max_rounds']

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('max_users', 0) > cleaned_data.get('max_following', 0) > \
                cleaned_data.get('min_following', 0) and cleaned_data.get('max_users', 0) > \
                cleaned_data.get('min_users', 0) and cleaned_data.get('score_lambda', 1) and \
                                Plot.objects.all().count() >= cleaned_data.get('max_rounds') > 0:
            return cleaned_data

        raise ValidationError("Didn't meet logical constraints for the Settings model")
