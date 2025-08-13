from datetime import date, timedelta, datetime
from io import BytesIO

import jdatetime
import openpyxl
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.db.models.fields import IntegerField
from django.db.models.functions.comparison import Cast
from django.db.models.query_utils import Q
from django.http.response import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls.base import reverse_lazy
from django.views import generic
from openpyxl.styles import Font, Alignment

from accounts.models import UserProfile
from adminpanel.forms import UserProfileForm, OrderUpdateForm, OrderItemFormSet
from orders.models import Order, OrderItem
from products.models import Product


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


class ExportOrdersToExcelView(AdminRequiredMixin, generic.View):

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


class AdminOrderManageView(AdminRequiredMixin, generic.ListView):
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


class AdminProductManageView(AdminRequiredMixin, generic.TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AdminReportsView(AdminRequiredMixin, generic.TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
