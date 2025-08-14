import json
from datetime import date, timedelta, datetime
from io import BytesIO

import jdatetime
import openpyxl
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models.aggregates import Sum, Avg, Count
from django.db.models.expressions import F, ExpressionWrapper
from django.db.models.fields import IntegerField
from django.db.models.functions.comparison import Cast
from django.db.models.functions.datetime import TruncDate
from django.db.models.query import Prefetch
from django.db.models.query_utils import Q
from django.http.response import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, render
from django.urls.base import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext
from django.views import generic
from openpyxl.styles import Font, Alignment

from accounts.models import UserProfile
from adminpanel.forms import UserProfileForm, OrderUpdateForm, OrderItemFormSet, UserCreateForm, ProductForm, \
    CommentInlineFormSet, CategoryForm
from orders.models import Order, OrderItem
from products.models import Product, Comment, Category


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user_profile = getattr(self.request.user, 'profile', None)
        if user_profile and getattr(user_profile, 'role', None) == 'admin':
            return True
        return False

    def handle_no_permission(self):
        return HttpResponseForbidden("شما اجازه دسترسی به این صفحه را ندارید.")


class Admin_Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'adminpanel/admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_revenue = OrderItem.objects.filter(
            order__status='completed'
        ).aggregate(
            total=Cast(Sum(F('quantity') * F('price')), IntegerField())
        )['total'] or 0
        total_orders = Order.objects.count()

        total_products = Product.objects.count()

        User = get_user_model()
        total_users = User.objects.count()

        context.update({
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'total_products': total_products,
            'total_users': total_users,
        })
        return context


class UserProfileCreateView(AdminRequiredMixin, LoginRequiredMixin, generic.View):
    template_name = "adminpanel/admin/admin_user_create.html"
    success_url = reverse_lazy("admin_user_manage")

    def get(self, request, *args, **kwargs):
        user_form = UserCreateForm()
        profile_form = UserProfileForm()
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})

    def post(self, request, *args, **kwargs):
        user_form = UserCreateForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.email = user_form.cleaned_data["email"]
                user.save()

                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()

            messages.success(request, "کاربر و پروفایل با موفقیت ایجاد شدند.")
            return redirect(self.success_url)

        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})


class AdminUserManage(AdminRequiredMixin, generic.ListView):
    template_name = 'adminpanel/admin/admin_users.html'
    model = get_user_model()
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = self.model.objects.select_related('profile').all()

        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(profile__full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(profile__phone_number__icontains=search)
            )

        # فیلتر وضعیت
        status = self.request.GET.get('status', '')
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)

        # فیلتر نقش
        role = self.request.GET.get('role', '')
        if role in ['admin', 'customer']:
            qs = qs.filter(profile__role=role)

        # فیلتر تاریخ ثبت
        date_filter = self.request.GET.get('date', '')
        now = datetime.now()
        if date_filter == 'today':
            qs = qs.filter(date_joined__date=now.date())
        elif date_filter == 'week':
            week_ago = now - timedelta(days=7)
            qs = qs.filter(date_joined__gte=week_ago)
        elif date_filter == 'month':
            month_ago = now - timedelta(days=30)
            qs = qs.filter(date_joined__gte=month_ago)
        elif date_filter == 'year':
            year_ago = now - timedelta(days=365)
            qs = qs.filter(date_joined__gte=year_ago)

        return qs.order_by('-date_joined')

    def get(self, request, *args, **kwargs):
        if 'HX-Request' in request.headers:
            self.template_name = 'adminpanel/admin/partials/user_list.html'
            return super().get(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        user_model = self.model
        context['total_users'] = user_model.objects.count()
        context['users_registered_today'] = user_model.objects.filter(date_joined__date=today).count()
        return context


class BulkOrderActionView(AdminRequiredMixin, generic.View):
    """
    A view to handle bulk actions (completed, cancelled, delete) on orders.
    """

    def post(self, request, *args, **kwargs):
        # Retrieve the list of order IDs from the POST request.
        # The IDs are sent from the front-end with the name 'order_ids[]'.
        order_ids = request.POST.getlist('order_ids[]')

        # Get the action to be performed (e.g., 'completed', 'cancelled', 'delete').
        action = request.POST.get('action')

        # Filter the orders queryset to include only the selected orders.
        orders_to_update = Order.objects.filter(id__in=order_ids)

        # Check the action and perform the corresponding database operation.
        if action == 'completed':
            # Update the status of the selected orders to 'completed'.
            orders_to_update.update(status='completed')
            messages.success(request, f"{orders_to_update.count()} سفارش با موفقیت تکمیل شدند.")

        elif action == 'cancelled':
            # Update the status of the selected orders to 'cancelled'.
            orders_to_update.update(status='cancelled')
            messages.success(request, f"{orders_to_update.count()} سفارش لغو شدند.")

        elif action == 'delete':
            # Delete the selected orders.
            # Note: This will also cascade delete any related OrderItem objects.
            orders_to_update.delete()
            messages.success(request, f"{orders_to_update.count()} سفارش با موفقیت حذف شدند.")

        else:
            # If the action is not recognized, show an error message.
            messages.error(request, "عملیات نامعتبر است.")

        # Redirect the user back to the order management page.
        return redirect('admin_order_manage')


class BulkUserActionView(AdminRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        user_ids = request.POST.getlist('user_ids[]')
        action = request.POST.get('action')
        user_model = get_user_model()
        users_to_update = user_model.objects.filter(id__in=user_ids)

        if action == 'activate':
            users_to_update.update(is_active=True)
            messages.success(request, f"{users_to_update.count()} کاربر فعال شدند.")
        elif action == 'block':
            users_to_update.update(is_active=False)
            messages.success(request, f"{users_to_update.count()} کاربر مسدود شدند.")
        elif action == 'delete':
            users_to_update.delete()
            messages.success(request, f"{users_to_update.count()} کاربر حذف شدند.")
        else:
            messages.error(request, "عملیات نامعتبر است.")

        return redirect('admin_user_manage')


def get_filtered_queryset(request):
    """
    Helper function to get a filtered queryset of users based on GET parameters.
    """
    user_model = get_user_model()
    qs = user_model.objects.select_related('profile').all()

    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(profile__phone_number__icontains=search)
        )

    status = request.GET.get('status', '')
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)

    role = request.GET.get('role', '')
    if role in ['admin', 'customer']:
        qs = qs.filter(profile__role=role)

    date_filter = request.GET.get('date', '')
    now = datetime.now()
    if date_filter == 'today':
        qs = qs.filter(date_joined__date=now.date())
    elif date_filter == 'week':
        week_ago = now - timedelta(days=7)
        qs = qs.filter(date_joined__gte=week_ago)
    elif date_filter == 'month':
        month_ago = now - timedelta(days=30)
        qs = qs.filter(date_joined__gte=month_ago)
    elif date_filter == 'year':
        year_ago = now - timedelta(days=365)
        qs = qs.filter(date_joined__gte=year_ago)

    return qs.order_by('-date_joined')


class ExportUsersToExcelView(AdminRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        queryset = get_filtered_queryset(request)

        output = BytesIO()
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "User Data"

        # Set up headers
        columns = [
            'ID', 'کاربر', 'ایمیل', 'شماره تلفن', 'نقش', 'وضعیت', 'تاریخ عضویت', 'آخرین فعالیت'
        ]
        worksheet.append(columns)

        # Apply some basic styling to headers
        header_font = Font(bold=True)
        header_alignment = Alignment(horizontal='center')
        for cell in worksheet[1]:
            cell.font = header_font
            cell.alignment = header_alignment

        # Write data rows
        for user in queryset:
            row_data = [
                user.id,
                user.get_full_name() or user.username,
                user.email,
                user.profile.phone_number if hasattr(user, 'profile') else '-',
                user.profile.get_role_display() if hasattr(user, 'profile') else '-',
                "فعال" if user.is_active else "غیرفعال",
                user.date_joined.strftime('%Y/%m/%d'),
                user.last_login.strftime('%Y/%m/%d %H:%M') if user.last_login else '-'
            ]
            worksheet.append(row_data)

        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="users_export.xlsx"'
        return response


class UserProfileUpdateView(AdminRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'adminpanel/user/user_edit_profile.html'
    success_url = reverse_lazy('admin_user_manage')

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()

        # Convert Persian digits to English
        def persian_to_english_digits(s):
            persian_digits = '۰۱۲۳۴۵۶۷۸۹'
            english_digits = '0123456789'
            for p, e in zip(persian_digits, english_digits):
                s = s.replace(p, e)
            return s

        if data.get('birth_date'):
            shamsi_str = persian_to_english_digits(data['birth_date'])
            try:
                jy, jm, jd = map(int, shamsi_str.split('/'))
                gregorian_date = jdatetime.date(jy, jm, jd).togregorian()
                # Replace with YYYY-MM-DD
                data['birth_date'] = gregorian_date.strftime('%Y-%m-%d')
            except Exception:
                pass  # Let the form handle the invalid date

        request.POST = data
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.get_object().user
        user.email = self.request.POST.get('email')
        user.save()
        messages.success(self.request, 'پروفایل کاربر با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)


class UserProfileDeleteView(AdminRequiredMixin, generic.DeleteView):
    model = get_user_model()
    success_url = reverse_lazy('admin_user_manage')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'کاربر با موفقیت حذف شد')
        return HttpResponseRedirect(self.success_url)


def get_filtered_orders_queryset(request):
    qs = Order.objects.all()

    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(address__icontains=search) |
            Q(order_notes__icontains=search)
        )

    status = request.GET.get('status', '')
    if status in [choice[0] for choice in Order.STATUS_CHOICES]:
        qs = qs.filter(status=status)

    paid = request.GET.get('paid', '')
    if paid == 'yes':
        qs = qs.filter(paid=True)
    elif paid == 'no':
        qs = qs.filter(paid=False)

    date_filter = request.GET.get('date', '')
    now = datetime.now()
    if date_filter == 'today':
        qs = qs.filter(datetime_created__date=now.date())
    elif date_filter == 'week':
        week_ago = now - timedelta(days=7)
        qs = qs.filter(datetime_created__gte=week_ago)
    elif date_filter == 'month':
        month_ago = now - timedelta(days=30)
        qs = qs.filter(datetime_created__gte=month_ago)
    elif date_filter == 'year':
        year_ago = now - timedelta(days=365)
        qs = qs.filter(datetime_created__gte=year_ago)

    return qs.order_by('-datetime_created')


class ExportOrdersToExcelView(AdminRequiredMixin, LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        queryset = get_filtered_orders_queryset(request)

        output = BytesIO()
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Order Data"

        # Excel columns
        columns = [
            'ID', 'نام مشتری', 'نام خانوادگی', 'ایمیل', 'شماره تماس', 'آدرس',
            'وضعیت سفارش', 'پرداخت شده', 'مبلغ کل', 'یادداشت مشتری', 'تاریخ ایجاد', 'تاریخ ویرایش'
        ]
        worksheet.append(columns)

        # Header styling
        header_font = Font(bold=True)
        header_alignment = Alignment(horizontal='center')
        for cell in worksheet[1]:
            cell.font = header_font
            cell.alignment = header_alignment

        # Writing data
        for order in queryset:
            # Use .get_status_display() to get the human-readable status, which is more reliable
            # than manually accessing the dictionary.
            status_display = order.get_status_display()

            row = [
                order.id,
                order.first_name,
                order.last_name,
                order.email,
                order.phone_number,
                order.address,
                # Fix: Use the .get_status_display() method
                status_display,
                "بله" if order.paid else "خیر",
                order.get_total_price(),
                order.order_notes or '-',
                order.datetime_created.strftime('%Y/%m/%d %H:%M'),
                order.datetime_modified.strftime('%Y/%m/%d %H:%M'),
            ]
            worksheet.append(row)

        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="orders_export.xlsx"'
        return response


class AdminOrderManageView(AdminRequiredMixin, LoginRequiredMixin, generic.ListView):
    template_name = 'adminpanel/admin/admin_orders.html'
    model = Order
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        qs = self.model.objects.select_related('user').all()

        # --- Search Filter ---
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(id__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        # --- Status Filter ---
        status = self.request.GET.get('status', '')
        if status in ['pending', 'processing', 'shipped', 'completed', 'cancelled']:
            qs = qs.filter(status=status)

        # --- Date Filter ---
        date_filter = self.request.GET.get('date', '')
        now = datetime.now()
        if date_filter == 'today':
            qs = qs.filter(datetime_created__date=now.date())
        elif date_filter == 'week':
            week_ago = now - timedelta(days=7)
            qs = qs.filter(datetime_created__gte=week_ago)
        elif date_filter == 'month':
            month_ago = now - timedelta(days=30)
            qs = qs.filter(datetime_created__gte=month_ago)
        elif date_filter == 'year':
            year_ago = now - timedelta(days=365)
            qs = qs.filter(datetime_created__gte=year_ago)

        return qs.order_by('-datetime_created')

    def get(self, request, *args, **kwargs):
        # اگر درخواست از HTMX است فقط partial رندر شود
        if 'HX-Request' in request.headers:
            self.template_name = 'adminpanel/admin/partials/orders_list.html'
            return super().get(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_orders'] = self.model.objects.count()
        context['processing_orders'] = self.model.objects.filter(status='processing').count()
        context['completed_orders'] = self.model.objects.filter(status='completed').count()
        context['cancelled_orders'] = self.model.objects.filter(status='cancelled').count()
        return context


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    model = Order
    template_name = "adminpanel/user/user_order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        """
        Only allow the logged-in user to see their own orders
        unless the user is a staff member.
        """
        qs = super().get_queryset()
        if 'admin' not in self.request.user.profile.role:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        """
        Add order items and total price to the template context.
        """
        context = super().get_context_data(**kwargs)
        order = self.object
        items = order.items.select_related("product")  # Prefetch product for efficiency
        total_price = order.get_total_price()

        context["items"] = items
        context["total_price"] = total_price
        return context


class OrderCreateView(AdminRequiredMixin, LoginRequiredMixin, generic.CreateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = 'adminpanel/admin/admin_create_order.html'
    context_object_name = "order"

    def get_success_url(self):
        return reverse_lazy('panel_order_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        """
        Provide products and the inline formset.
        On GET: empty formset bound to a fresh Order() so the template can render rows.
        On invalid POST: reuse the bound formset passed in kwargs.
        """
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()

        if 'formset' in kwargs:
            context['formset'] = kwargs['formset']
        else:
            # fresh instance so inline formset renders empty forms on GET
            context['formset'] = OrderItemFormSet(instance=Order())
        return context

    def post(self, request, *args, **kwargs):
        """
        Validate parent form and formset together.
        We bind the formset to form.instance (unsaved) for validation, then save atomically.
        """
        self.object = None
        form = self.get_form()
        # Bind formset to the (unsaved) parent so validation can run
        formset = OrderItemFormSet(self.request.POST, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Save parent first (ensure it has a PK)
                self.object = form.save(commit=False)

                # If your form doesn't expose 'user' and you want creator as owner by default:
                if not self.object.user_id:
                    self.object.user = self.request.user

                self.object.save()

                # Now save the items against the saved parent
                formset.instance = self.object
                formset.save()

            return redirect(self.get_success_url())

        # invalid: re-render with errors
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def form_invalid(self, form):
        """
        Keep parity with UpdateView’s behavior if Django routes here.
        Make sure a bound formset is present.
        """
        formset = OrderItemFormSet(self.request.POST, instance=form.instance)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class OrderUpdateView(AdminRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = 'adminpanel/admin/admin_editorder.html'
    context_object_name = "order"

    def get_success_url(self):
        return reverse_lazy('panel_order_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        if self.request.method == 'POST':
            context['formset'] = OrderItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = OrderItemFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class OrderDeleteView(AdminRequiredMixin, generic.View):
    success_url = reverse_lazy("admin_order_manage")

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        order_id = order.pk
        order.delete()
        messages.success(request, f"سفارش {order_id} با موفقیت حذف شد.")
        return redirect(self.success_url)


class BulkProductActionView(AdminRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        product_ids = request.POST.getlist('product_ids[]')
        action = request.POST.get('action', '').strip()

        if not product_ids:
            messages.error(request, "هیچ محصولی انتخاب نشده است.")
            return redirect('admin_product_manage')

        qs = Product.objects.filter(id__in=product_ids)

        if action == 'avl':  # mark available
            updated = qs.update(status='avl')
            messages.success(request, f"{updated} محصول به «موجود» تغییر یافت.")
        elif action == 'una':  # mark unavailable
            updated = qs.update(status='una')
            messages.success(request, f"{updated} محصول به «ناموجود» تغییر یافت.")
        elif action == 'delete':
            count = qs.count()
            qs.delete()
            messages.success(request, f"{count} محصول حذف شد.")
        else:
            messages.error(request, "عملیات نامعتبر است.")

        return redirect('admin_product_manage')


class AdminProductManageView(AdminRequiredMixin, generic.ListView):
    template_name = 'adminpanel/admin/admin_products.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        qs = self.model.objects.select_related('category').all()

        # --- Search Filter ---
        search = (self.request.GET.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(id__icontains=search) |
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        # --- Status Filter ---
        status = (self.request.GET.get('status') or '').strip()
        if status in ['avl', 'una']:  # موجود / ناموجود
            qs = qs.filter(status=status)

        # --- Date Filter ---
        date_filter = (self.request.GET.get('date') or '').strip()
        now = datetime.now()
        if date_filter == 'today':
            qs = qs.filter(datetime_created__date=now.date())
        elif date_filter == 'week':
            qs = qs.filter(datetime_created__gte=now - timedelta(days=7))
        elif date_filter == 'month':
            qs = qs.filter(datetime_created__gte=now - timedelta(days=30))
        elif date_filter == 'year':
            qs = qs.filter(datetime_created__gte=now - timedelta(days=365))

        return qs.order_by('-datetime_created')

    def get(self, request, *args, **kwargs):
        # HTMX partial rendering
        if 'HX-Request' in request.headers:
            self.template_name = 'adminpanel/admin/partials/product_list.html'
            return super().get(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = self.model.objects.count()
        context['available_products'] = self.model.objects.filter(status='avl').count()
        context['unavailable_products'] = self.model.objects.filter(status='una').count()
        return context


class AdminProductDetailView(AdminRequiredMixin, generic.DetailView):
    model = Product
    template_name = 'adminpanel/admin/admin_product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        # همه نظرات (برای نمایش)
        all_comments_qs = Comment.objects.select_related('user').order_by('-datetime_created')
        # فقط نظرات تاییدشده (برای آمار امتیاز)
        verified_qs = Comment.verified_comments.select_related('user').order_by('-datetime_created')

        return (
            Product.objects
            .select_related('category')
            .prefetch_related(
                Prefetch('comments', queryset=all_comments_qs, to_attr='all_comments_list'),
                Prefetch('comments', queryset=verified_qs, to_attr='verified_comments_list'),
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.object

        # آمار فقط از نظرات تاییدشده
        base_qs = Comment.verified_comments.filter(product=p)
        rating_avg = base_qs.aggregate(avg=Avg(Cast('stars', IntegerField())))['avg'] or 0
        rating_count = base_qs.count()

        ctx.update({
            'has_discount': p.discount_percent > 0,
            'final_price': p.get_discounted_price,
            'verified_comments': getattr(p, 'verified_comments_list', []),  # اگر جایی نیاز شد
            'all_comments': getattr(p, 'all_comments_list', []),  # برای رندر همه نظرات
            'rating_avg': round(rating_avg, 1),
            'rating_count': rating_count,  # تعداد نظرات تاییدشده
        })
        return ctx


class AdminProductUpdateView(AdminRequiredMixin, generic.UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "adminpanel/admin/admin_product_edit.html"
    context_object_name = "product"

    def get_success_url(self):
        return reverse_lazy("admin_product_detail", kwargs={"pk": self.object.pk})

    def get_formset(self):
        if self.request.method == "POST":
            return CommentInlineFormSet(self.request.POST, instance=self.object)
        return CommentInlineFormSet(
            instance=self.object,
            queryset=Comment.objects.filter(product=self.object)
            .select_related("user")
            .order_by("-datetime_created")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            ctx['comments_formset'] = CommentInlineFormSet(self.request.POST, instance=self.object,
                                                           queryset=Comment.objects.select_related('user').order_by(
                                                               '-datetime_created'))
        else:
            ctx['comments_formset'] = CommentInlineFormSet(instance=self.object,
                                                           queryset=Comment.objects.select_related('user').order_by(
                                                               '-datetime_created'))
        return ctx

    def form_valid(self, form):
        formset = self.get_formset()
        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                # Re-render with errors
                return self.render_to_response(self.get_context_data(form=form, formset=formset))
        messages.success(self.request, "محصول و نظرات با موفقیت به‌روزرسانی شدند.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "خطا در فرم. لطفاً موارد را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form, formset=self.get_formset()))


class AdminProductDeleteView(AdminRequiredMixin, generic.View):
    success_url = reverse_lazy("admin_product_manage")

    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        product_id = product.pk
        product.delete()
        messages.success(request, f"محصول {product_id} با موفقیت حذف شد.")
        return redirect(self.success_url)


class AdminCategoryManageView(AdminRequiredMixin, generic.ListView):
    template_name = 'adminpanel/admin/admin_categories.html'
    model = Category
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        qs = self.model.objects.all()
        search = (self.request.GET.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(slug__icontains=search)
            )
        # optional date filter (if you add created field later)
        return qs.order_by('name')

    def get(self, request, *args, **kwargs):
        if request.headers.get('HX-Request'):
            self.template_name = 'adminpanel/admin/partials/categories_list.html'
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_categories'] = self.model.objects.count()
        return ctx


class _CategoryModalBase(AdminRequiredMixin):
    model = Category
    form_class = CategoryForm
    template_name = 'adminpanel/admin/partials/category_modal.html'
    context_object_name = 'category'

    def form_valid(self, form):
        self.object = form.save()
        # 204 with HX-Trigger to refresh list + toast
        resp = HttpResponse(status=204)
        resp['HX-Trigger'] = json.dumps({
            'refreshCategoryList': True,
            'toast': {'type': 'success', 'message': 'تغییرات با موفقیت ذخیره شد.'}
        })
        return resp

    def form_invalid(self, form):
        # Return the modal with form errors
        return self.render_to_response(self.get_context_data(form=form))


class AdminCategoryCreateModalView(_CategoryModalBase, generic.CreateView):
    pass


class AdminCategoryUpdateModalView(_CategoryModalBase, generic.UpdateView):
    pass


class AdminCategoryDeleteModalView(AdminRequiredMixin, generic.DeleteView):
    model = Category
    template_name = 'adminpanel/admin/partials/category_delete_modal.html'
    context_object_name = 'category'
    success_url = reverse_lazy("admin_category_manage")

    def form_valid(self, form):
        obj = self.get_object()
        name = obj.name
        obj.delete()
        messages.success(self.request, f'«{name}» حذف شد.')

        if self.request.headers.get('HX-Request'):
            resp = HttpResponse(status=204)
            resp['HX-Redirect'] = str(self.get_success_url())
            return resp

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


def _date_range(rng: str):
    today = timezone.localdate()
    if rng == 'today':
        return today, today
    if rng == '30days':
        return today - timedelta(days=29), today
    # default 7 days
    return today - timedelta(days=6), today


class AdminReportsView(generic.TemplateView):
    template_name = 'adminpanel/admin/admin_reports.html'
    partial_template = 'adminpanel/admin/partials/reports_body.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        rng = (self.request.GET.get('range') or '7days').lower()
        start, end = _date_range(rng)

        base_orders = (
            Order.objects
            .filter(datetime_created__date__gte=start, datetime_created__date__lte=end)
            .exclude(status__in=['cancelled'])
        )

        # Build calendar days
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]

        # Orders per day
        oqs = (
            base_orders
            .annotate(day=TruncDate('datetime_created'))
            .values('day')
            .annotate(c=Count('id'))
        )
        orders_map = {r['day']: r['c'] for r in oqs}
        orders_series = [orders_map.get(d, 0) for d in days]

        # Revenue per day (from OrderItem)
        line_total = ExpressionWrapper(
            F('quantity') * F('price'),
            output_field=IntegerField()
        )
        rqs = (
            OrderItem.objects
            .filter(order__datetime_created__date__gte=start,
                    order__datetime_created__date__lte=end)
            .exclude(order__status__in=['cancelled'])
            .annotate(day=TruncDate('order__datetime_created'))
            .values('day')
            .annotate(amount=Sum(line_total))
        )
        rev_map = {r['day']: int(r['amount'] or 0) for r in rqs}
        revenue_series = [rev_map.get(d, 0) for d in days]

        # AOV per day
        aov_series = []
        for d in days:
            c = orders_map.get(d, 0)
            aov_series.append(int(rev_map.get(d, 0) / c) if c else 0)

        # Cancellations per day (optional chart)
        cqs = (
            Order.objects
            .filter(datetime_created__date__gte=start,
                    datetime_created__date__lte=end,
                    status='cancelled')
            .annotate(day=TruncDate('datetime_created'))
            .values('day')
            .annotate(c=Count('id'))
        )
        cancel_map = {r['day']: r['c'] for r in cqs}
        cancellations_series = [cancel_map.get(d, 0) for d in days]

        # Status distribution (donut)
        sdist = (
            Order.objects
            .filter(datetime_created__date__gte=start,
                    datetime_created__date__lte=end)
            .values('status')
            .annotate(c=Count('id'))
            .order_by('-c')
        )
        status_display_map = {code: gettext(label) for code, label in Order.STATUS_CHOICES}
        status_labels_fa = [status_display_map.get(r['status'], r['status']) for r in sdist]
        status_values = [r['c'] for r in sdist]

        total_revenue = sum(revenue_series)
        total_orders = sum(orders_series)
        aov = int(total_revenue / total_orders) if total_orders else 0

        payload = {
            'labels': [d.strftime('%Y-%m-%d') for d in days],
            'orders': orders_series,
            'revenue': revenue_series,
            'aov': aov_series,
            'cancellations': cancellations_series,
            'status_dist': {'labels': status_labels_fa, 'values': status_values},
        }

        ctx.update({
            'range': rng,
            'kpis': {'revenue': total_revenue, 'orders': total_orders, 'aov': aov},
            'chartjs_payload_json': json.dumps(payload, ensure_ascii=False),
            'start': start, 'end': end,
        })
        return ctx

    def get(self, request, *args, **kwargs):
        # HTMX = return partial only
        if request.headers.get('HX-Request'):
            return self.response_class(
                request=request,
                template=self.partial_template,
                context=self.get_context_data()
            )
        return super().get(request, *args, **kwargs)


class AdminNotificationsView(AdminRequiredMixin, generic.TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AdminSettingsView(AdminRequiredMixin, generic.TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
