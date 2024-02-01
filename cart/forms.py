from django import forms


class CartAddForm(forms.Form):
    QUANTITIES_CHOICES = ([(i, str(i)) for i in range(1, 30)])
    quantity = forms.TypedChoiceField(choices=QUANTITIES_CHOICES, coerce=int)
    inplace = forms.BooleanField(required=False,widget=forms.HiddenInput())