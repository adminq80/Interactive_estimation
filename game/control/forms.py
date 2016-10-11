from django import forms


class RoundForm(forms.Form):
    guess = forms.DecimalField(required=True, max_digits=3, decimal_places=2)


class CheckForm(forms.Form):
    Q1_choices = (('1', 'Estimate the correlation of two variables'),
                  ('2', 'Calculate the correlation of two variables'),
                  )
    q1 = forms.ChoiceField(label='Your goal in the game is to', widget=forms.RadioSelect(attrs={'class': 'form-group'}),
                           choices=Q1_choices)

    q2 = forms.DecimalField(label='In general, correlation can be between', widget=forms.TextInput)
    q3 = forms.DecimalField(label='and', widget=forms.TextInput)

    q4 = forms.ChoiceField(label='In this game, all correlations will be', widget=forms.RadioSelect,
                           choices=(('1', 'Negative or positive'),
                                    ('2', 'Only positive'),
                                    ))

    q5 = forms.ChoiceField(label='Have you participated in this study before?', widget=forms.RadioSelect,
                           choices=(('1', 'No'),
                                    ('2', 'Yes'),
                                    ))

    def clean(self):
        cleaned_data = super(CheckForm, self).clean()
        q1 = cleaned_data.get('q1')
        q2 = float(cleaned_data.get('q2'))
        q3 = float(cleaned_data.get('q3'))
        q4 = cleaned_data.get('q4')
        q5 = cleaned_data.get('q5')

        if q1 == '1' and q2 == -1 and q3 == 1 and q4 == '2' and q5 == '1':
            return cleaned_data
        raise forms.ValidationError('One or more answer/s is/are wrong')
