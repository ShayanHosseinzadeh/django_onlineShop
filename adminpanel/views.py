from datetime import date, timedelta, datetime
from io import BytesIO

import jdatetime
import openpyxl
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.db.models.fields import IntegerField
from django.db.models.functions.comparison import Cast
from django.db.models.query_utils import Q
from django.http.response import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.views import generic
from openpyxl.styles import Font, Alignment

from accounts.models import UserProfile
from adminpanel.forms import UserProfileForm
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
        # Check if the request is from HTMX
        if 'HX-Request' in request.headers:
            # If so, render only the partial template for the table
            self.template_name = 'adminpanel/admin/partials/user_list.html'
            return super().get(request, *args, **kwargs)

        # Otherwise, render the full page with the base template
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        user_model = self.model
        context['total_users'] = user_model.objects.count()
        context['users_registered_today'] = user_model.objects.filter(date_joined__date=today).count()
        return context


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


class AdminDashboardView(AdminRequiredMixin, generic.TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AdminUserManageView(AdminRequiredMixin, generic.TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AdminOrderManageView(AdminRequiredMixin, generic.TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
