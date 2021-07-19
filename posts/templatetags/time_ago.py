from django import template
from django.utils import timezone

register = template.Library()


period_dict = {
    'minute': ('минута', 'минуты', 'минут'),
    'hour': ('час', 'часа', 'часов'),
    'day': ('день', 'дня', 'дней'),
}

def proper_ending(value, period):
    mod = value % 10
    if 5 <= mod <= 9 or mod == 0 or 11 <= value <= 14:
        res = period_dict[period][2]
    elif mod == 1:
        res = period_dict[period][0]
    else:
        res = period_dict[period][1]
    return f'{value} {res} назад'


@register.filter
def time_ago(value):
    """Возвращает количество прошедших дней/часов/минут"""
    if not value:
        return 'Никогда'
    now = timezone.now()
    delta = now - value
    minutes_ago = delta.seconds//60
    hours_ago = delta.seconds//3600
    days_ago = delta.days
    return (days_ago and proper_ending(days_ago, 'day')
            or hours_ago and proper_ending(hours_ago, 'hour')
            or minutes_ago and proper_ending(minutes_ago, 'minute')
            or 'Только что')
