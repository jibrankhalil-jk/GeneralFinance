from django import forms
from django.contrib.auth.models import User
from . import models

class SalesEntryForm(forms.ModelForm):
    class Meta:
        # model =  models.Sales
        # fields = ['email', 'password']
        fields = ['total_amount', 'items']
        # widgets = {
            # 'text': forms.Textarea(attrs={'class': 'form-control'}),
            # 'photo': forms.FileInput(attrs={'class': 'form-control'}),
        # }
