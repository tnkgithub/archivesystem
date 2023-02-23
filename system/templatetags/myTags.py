from django import template
register = template.Library()

@register.simple_tag
def get_value(dict, key):
    return dict[key]

@register.simple_tag
def for_text(value):
    if value >= 0.5:
        return 100
    else :
        return 0

@register.filter
def modulo(loopnum, value):
    return loopnum % value

@register.filter
def multiplication(value1, value2):
    return value1 * value2
