from django import template
from django.utils.text import slugify as django_slugify

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """
    Split a string by a delimiter.
    Usage: {{ "a,b,c"|split:"," }}
    """
    return [item.strip() for item in str(value).split(delimiter)]


@register.filter
def get_item(lst, index):
    """
    Get item from list by index.
    Usage: {{ my_list|get_item:0 }}
    """
    try:
        return lst[int(index)]
    except (IndexError, TypeError, ValueError):
        return ''


@register.filter
def rupees(value):
    """
    Format a number as Indian Rupees.
    Usage: {{ 1999|rupees }}  →  ₹1,999
    """
    try:
        val = int(float(value))
        return f'₹{val:,}'
    except (TypeError, ValueError):
        return f'₹{value}'


@register.filter
def stars(rating):
    """
    Return star string for a rating.
    Usage: {{ 4.2|stars }}  →  ★★★★☆
    """
    try:
        r = float(rating)
        full  = int(r)
        empty = 5 - full
        return '★' * full + '☆' * empty
    except (TypeError, ValueError):
        return '★★★★☆'


@register.simple_tag
def veg_icon(is_veg):
    """Return veg/non-veg indicator HTML."""
    color = '#1ba672' if is_veg else '#e74c3c'
    label = 'Veg' if is_veg else 'Non-veg'
    return f'<span style="color:{color};font-size:11px;font-weight:600;">{label}</span>'