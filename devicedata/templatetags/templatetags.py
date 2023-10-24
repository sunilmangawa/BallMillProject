from django import template

register = template.Library()

# @register.filter
# def reverse_katta_number(counter, paginator):
#     return paginator.count - (counter + (paginator.number - 1) * paginator.per_page) + 1

@register.filter
def reverse_katta_number(counter, milldata_page):
    return milldata_page.paginator.count - (counter + (milldata_page.number - 1) * milldata_page.paginator.per_page) + 1

@register.simple_tag
def querystring(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            updated[k] = v
        else:
            updated.pop(k, None)
    return updated.urlencode()

@register.filter
def max_value(value, arg):
    return max(value, arg)

# @register.filter
# def divide(value, arg):
#     try:
#         return float(value) / float(arg)
#     except (ValueError, TypeError, ZeroDivisionError):
#         return 0