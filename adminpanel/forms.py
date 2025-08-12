from django import forms
from django.forms.models import ModelForm, inlineformset_factory

from accounts.models import UserProfile
from orders.models import Order, OrderItem


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'role', 'phone_number', 'address', 'city', 'postal_code', 'birth_date', 'avatar']


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'order_notes', 'status', 'paid']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea'}),
            'order_notes': forms.Textarea(attrs={'class': 'form-textarea'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'paid': forms.Select(choices=[(True, 'پرداخت شده'), (False, 'پرداخت نشده')],
                                 attrs={'class': 'form-select'}),
        }


# Create the formset factory for OrderItem, related to Order
# extra=1 allows adding one new blank form for a new item
# can_delete=True adds a checkbox to delete existing items
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    fields=['product', 'quantity','price'],
    extra=1,
    can_delete=True,
    widgets={
        'quantity': forms.NumberInput(attrs={'class': 'form-input w-20 text-center '}),
        'product': forms.Select(attrs={'class': 'form-select'}),
        'price':forms.HiddenInput(),
    }
)