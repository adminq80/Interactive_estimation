from django import forms


class RoundForm(forms.Form):
    guess = forms.DecimalField(required=True, max_digits=3, decimal_places=2)
