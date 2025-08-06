
import jdatetime
from django import template

register = template.Library()

@register.filter
def to_jalali(value):
    if not value:
        return ""
    try:
        return jdatetime.datetime.fromgregorian(datetime=value).strftime('%H:%M - %Y/%m/%d')
    except:
        return value