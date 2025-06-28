from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='intcomma', is_safe=True)
def intcomma(value):
    """
    Convert an integer to a string containing spaces every three digits.
    For example, 3000 becomes '3 000' and 45000 becomes '45 000'.
    """
    if value is None:
        return ''
    try:
        return "{:,}".format(int(value)).replace(",", " ")
    except (ValueError, TypeError):
        return str(value)
