from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import ModelForm, inlineformset_factory
from django.forms.widgets import ClearableFileInput

from accounts.models import UserProfile
from adminpanel.jalali import JalaliOrGregorianDateField
from orders.models import Order, OrderItem
from products.models import Product, Comment

User = get_user_model()


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

INPUT_CLS = "tw-input w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none text-right"

class ProductForm(ModelForm):
    # CKEditor برای فیلدهای ریچ
    description = forms.CharField(
        label="توضیحات",
        widget=CKEditorWidget(config_name="default"),
        required=False,
    )
    key_features = forms.CharField(
        label="ویژگی‌های کلیدی",
        widget=CKEditorWidget(config_name="default"),
        required=False,
    )

    # کنترل حذف تصویر به‌صورت سفارشی (جایگزین ClearableFileInput)
    remove_image = forms.BooleanField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Product
        fields = [
            "title", "category", "status",
            "price", "discount_percent", "stock_quantity",
            "short_description", "key_features", "description", "image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLS, "placeholder": "نام محصول"}),
            "category": forms.Select(attrs={"class": INPUT_CLS}),
            "status": forms.Select(attrs={"class": INPUT_CLS}),
            "price": forms.NumberInput(attrs={"class": INPUT_CLS, "min": 0, "inputmode": "numeric"}),
            "discount_percent": forms.NumberInput(attrs={"class": INPUT_CLS, "min": 0, "max": 100}),
            "stock_quantity": forms.NumberInput(attrs={"class": INPUT_CLS, "min": 0}),
            "short_description": forms.Textarea(attrs={"class": INPUT_CLS, "rows": 3, "placeholder": "توضیح کوتاه"}),
            # فایل اینپوت معمولی (بدون متن «در حال حاضر… پاک کردن»)
            "image": forms.FileInput(attrs={"class": "hidden", "accept": "image/*", "id": "id_image"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # اگر کاربر «حذف تصویر» را زد
        if self.cleaned_data.get("remove_image"):
            if instance.image:
                instance.image.delete(save=False)
            instance.image = None

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class CommentInlineForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["stars", "text", "is_verified"]
        labels = {
            "stars": "امتیاز",
            "text": "متن نظر",
            "is_verified": "تایید؟",
        }
        widgets = {
            "stars": forms.Select(attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-blue-200 focus:border-blue-500 bg-white text-right"
            }),
            "text": forms.Textarea(attrs={
                "rows": 3,
                "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-blue-200 focus:border-blue-500 resize-y text-right leading-relaxed",
                "placeholder": "متن نظر را بنویسید…",
            }),
            "is_verified": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            }),
        }
CommentInlineFormSet = inlineformset_factory(
    Product, Comment, form=CommentInlineForm, extra=0, can_delete=True
)