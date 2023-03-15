import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .models import Message
from core.models import ActiveTeam, TeamMember, NewPlan

# Create your views here.


def index(request, id, *args, **kwargs):
    plan_info = NewPlan.objects.get(id=id)

    plan = {}
    plan['planname'] = plan_info.planname
    plan['plantype'] = plan_info.plantype
    plan['scheduledatetime'] = {
        'year': plan_info.scheduledate.year,
        'month': plan_info.scheduledate.month,
        'day': plan_info.scheduledate.day,
        'hour': plan_info.scheduletime.hour,
        'minute': plan_info.scheduletime.minute,
        'second': plan_info.scheduletime.second
    }
    plan['notification'] = str(plan_info.notification)
    periods = []
    for period_info in plan_info.periods.all():
        periods.append({
            'periodname': period_info.periodname,
            'duration': period_info.duration,
        })
    plan['periods'] = periods
    plan['events'] = {
        'plantitle': plan_info.events.plantitle,
        'foldertype': plan_info.events.foldertype,
        'eventdate': {
            'year': plan_info.events.eventdate.year,
            'month': plan_info.events.eventdate.month,
            'day': plan_info.events.eventdate.day
        }
    }

    return render(request, 'clock/index.html', {
        'id': id,
        'user': request.user,
        'plan': plan,
        'is_admin': request.user.is_authenticated and (request.user.role == 'Admin' or request.user.role == 'admin')
    })
