
from urllib import quote_plus
from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def urlify(value):
    return quote_plus(value.encode('utf8'))
