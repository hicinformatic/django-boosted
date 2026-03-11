"""Template tags for django_boosted."""

from django import template

register = template.Library()


@register.filter
def getattr_filter(obj, attr_name):
    """Get attribute from object dynamically."""
    return getattr(obj, attr_name, None)


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary dynamically."""
    if dictionary is None:
        return None
    return dictionary.get(key)
