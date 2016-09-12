from django import forms


class RoundForm(forms.Form):
    guess = forms.DecimalField(required=True, max_digits=4, decimal_places=3)