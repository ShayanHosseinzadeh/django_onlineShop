
import jdatetime
from django import template

register = template.Library()

@register.filter
def to_jalali(value):
    if not value:
        return ""
    try:
        return jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d')
    except:
        return value


@register.filter
def mul(value, arg):
    try:
        return int(value) * int(arg)
    except:
        return 0