# products/templatetags/product_filters.py
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext as _
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='split')
@stringfilter
def split(value, key):
    """
    Returns the value split by a key.
    Usage: {{ value|split:" " }}
    """
    return value.split(key)


@register.filter(name='timesince_persian')
def timesince_persian(value):
    now = timezone.now()
    diff = now - value

    if diff.days > 365:
        years = diff.days // 365
        return _('%(years)s سال پیش') % {'years': years}
    elif diff.days > 30:
        months = diff.days // 30
        return _('%(months)s ماه پیش') % {'months': months}
    elif diff.days > 0:
        return _('%(days)s روز پیش') % {'days': diff.days}
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return _('%(hours)s ساعت پیش') % {'hours': hours}
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return _('%(minutes)s دقیقه پیش') % {'minutes': minutes}
    else:
        return _('لحظاتی پیش')

import hashlib


# Predefined Tailwind CSS background colors
COLOR_CLASSES = [
    'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-yellow-500',
    'bg-lime-500', 'bg-green-500', 'bg-emerald-500', 'bg-teal-500',
    'bg-cyan-500', 'bg-blue-500', 'bg-indigo-500', 'bg-violet-500',
    'bg-purple-500', 'bg-fuchsia-500', 'bg-pink-500', 'bg-rose-500'
]

@register.filter
def avatar_color(username):
    if not username:
        return 'bg-gray-400'
    # Create a stable hash based on the username
    index = int(hashlib.md5(username.encode()).hexdigest(), 16) % len(COLOR_CLASSES)
    return COLOR_CLASSES[index]