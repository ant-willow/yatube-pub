from django import template


register = template.Library()


@register.filter
def addclass(field, css):
    """Фильтр для шаблонов"""
    return field.as_widget(attrs={"class": css})
