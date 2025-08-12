from datetime import datetime,date

import jdatetime
from django import template

register = template.Library()


@register.filter
def to_jalali(value):
    if not value:
        return ""
    try:
        if isinstance(value, str):
            # سعی کن رشته را به date تبدیل کنی
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                # اگر فرمت متفاوت است می‌توانی اینجا اصلاح کنی یا برگردانی همان مقدار
                return value

        # اگر datetime یا date بود
        if isinstance(value, (datetime, date)):
            return jdatetime.date.fromgregorian(date=value).strftime('%Y/%m/%d')

        return value
    except Exception:
        return value

@register.filter
def mul(value, arg):
    try:
        return int(value) * int(arg)
    except:
        return 0