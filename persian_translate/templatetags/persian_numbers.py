from django import template

register = template.Library()


@register.filter
def translate_number(value):
    value = str(value)
    e_to_p_table = value.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')
    return value.translate(e_to_p_table)

