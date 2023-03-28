from django import forms
from .models import Response

# Classe qui permet la création du formulaire
class ResponseForm(forms.ModelForm):
    class Meta:
            model = Response
            fields = ('given_answer',)