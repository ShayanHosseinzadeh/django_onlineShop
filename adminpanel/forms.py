from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm, inlineformset_factory

from accounts.models import UserProfile
from adminpanel.jalali import JalaliOrGregorianDateField
from orders.models import Order, OrderItem

User = get_user_model()

# --- UserCreateForm (as you already have, trimmed for brevity) ---
class UserCreateForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="ایمیل",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                     'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                     'placeholder:text-right text-right',
            'placeholder': 'ایمیل خود را وارد کنید'
        })
    )
    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                     'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                     'placeholder:text-right text-right',
            'placeholder': 'نام کاربری خود را وارد کنید'
        })
    )
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                     'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                     'placeholder:text-right text-right',
            'placeholder': 'رمز عبور خود را وارد کنید'
        })
    )
    password2 = forms.CharField(
        label="تأیید رمز عبور",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                     'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                     'placeholder:text-right text-right',
            'placeholder': 'تأیید رمز عبور خود را وارد کنید'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email",)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email


class UserProfileForm(ModelForm):
    birth_date = JalaliOrGregorianDateField(
        required=False,
        label="تاریخ تولد",
        input_formats=["%Y-%m-%d", "%Y/%m/%d"],  # Gregorian formats allowed
        widget=forms.TextInput(attrs={
            'id': 'id_birth_date',
            'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                     'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                     'placeholder:text-right text-right',
            'placeholder': 'YYYY/MM/DD'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['full_name', 'role', 'phone_number', 'address', 'city', 'postal_code', 'birth_date', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                         'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                         'placeholder:text-right text-right',
                'placeholder': 'نام و نام خانوادگی خود را وارد کنید'
            }),
            'role': forms.Select(attrs={
                'id': 'id_user_role',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                         'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                         'appearance-none bg-white placeholder:text-right text-right'
            }),
            'phone_number': forms.TextInput(attrs={
                'id': 'id_phone_number',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                         'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                         'placeholder:text-right text-right',
                'placeholder': '۰۹۱۲۳۴۵۶۷۸۹'
            }),
            'address': forms.Textarea(attrs={
                'id': 'id_address',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                         'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                         'resize-none placeholder:text-right text-right',
                'rows': 4,
                'placeholder': 'آدرس کامل'
            }),
            'city': forms.TextInput(attrs={
                'id': 'id_city',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                         'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                         'placeholder:text-right text-right',
                'placeholder': 'نام شهر'
            }),
            'postal_code': forms.TextInput(attrs={
                'id': 'id_postal_code',
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl '
                         'focus:border-primary focus:outline-none input-focus transition-all duration-200 '
                         'placeholder:text-right text-right',
                'placeholder': '۱۲۳۴۵۶۷۸۹'
            }),
            'avatar': forms.FileInput(attrs={
                'id': 'id_avatar', 'class': 'hidden', 'accept': 'image/*'
            }),
        }

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
    fields=['product', 'quantity', 'price'],
    extra=1,
    can_delete=True,
    widgets={
        'quantity': forms.NumberInput(attrs={'class': 'form-input w-20 text-center '}),
        'product': forms.Select(attrs={'class': 'form-select'}),
        'price': forms.HiddenInput(),
    }
)
