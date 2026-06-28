from django import template

register = template.Library()

@register.filter
def get_key(dictionary, key):
    """Fetches the value for a given key from a dictionary in Django template."""
    return dictionary.get(key, 0)  # Default to 0 if key not found
