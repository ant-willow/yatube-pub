from datetime import datetime as dt
from datetime import timedelta as td

from django.conf import settings
from django.utils import timezone

from dateutil.parser import parse

from ..models import Activity


def user_activity(get_response):

    def middleware(request):

        response = get_response(request)
        key = "last-activity"

        if request.user.is_authenticated:
            last_activity = request.session.get(key)
            too_old_time = (timezone.now()
                            - td(seconds=settings.LAST_ACTIVITY_INTERVAL_SECS))
            if not last_activity or parse(last_activity) < too_old_time:
                seen, created = (Activity.objects
                                 .get_or_create(user=request.user))
                seen.time = timezone.now()
                seen.save()
            request.session[key] = timezone.now().isoformat()
        return response

    return middleware
