from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, '')

# @register.simple_tag(takes_context=True)
# def param_replace(context, **kwargs):
#     request = context['request']
#     params = request.GET.copy()
#     for key, value in kwargs.items():
#         if value is not None:
#             params[key] = value
#         else:
#             params.pop(key, None)
#     return params.urlencode()