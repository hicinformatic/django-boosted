from django import forms

from .models import Alphabet, Country


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ["name"]

class AlphabetForm(forms.ModelForm):
    class Meta:
        model = Alphabet
        fields = ["name",]
