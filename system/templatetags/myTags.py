from django import template
register = template.Library()

@register.simple_tag
def get_value(dict, key):
    return dict[key]

@register.filter
def modulo(loopnum, value):
    return loopnum % value
