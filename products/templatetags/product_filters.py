# products/templatetags/product_filters.py

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
