from django import forms


class BoardForm(forms.Form):
    guess = forms.DecimalField(required=True, max_digits=4, decimal_places=3)
    plot = forms.CharField(widget=forms.HiddenInput)
