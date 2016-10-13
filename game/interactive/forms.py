from django import forms
from .models import Survey


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
