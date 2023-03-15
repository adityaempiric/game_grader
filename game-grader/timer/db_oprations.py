from channels.db import database_sync_to_async
from core.models import NewPlan,Period
from django.core import serializers
import json
from django.contrib import messages
from datetime import datetime
from datetime import datetime


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("===>>>",current_time)


@database_sync_to_async
def check_start_flag(id):
    planData = NewPlan.objects.get(id=id)
    # print("^^^^^^^^^^^",planData.is_start)
    print("--------------------------------",planData.id)

    if planData.is_start==False:
        # print("^^^^#$#^^^^^",planData.is_start)
        planData.is_start = True
        planData.save()

        msg = {
            "msg" : "The clock timer begins."
        }

        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # print("===>>>",current_time)


        all_periods = NewPlan.objects.get(id=id).periods.all().order_by("created")
        periods = serializers.serialize("json", all_periods)
        # print("\n\n\n\n")
        print("===>>>",periods)
        # print("\n\n\n\n")
        data = json.dumps({
                "type":"start-clock",
                "context":periods,
                "message":msg,
                "start_time":planData.clockstart_time,
                "time_status":planData.timerTravel_status,
                # "current_time":current_time,
            })
        return data
    else:
        msg = {
            "msg" : "Clock is already start."
        }
        newplanobj = NewPlan.objects.get(id=id)
        all_periods = newplanobj.periods.all().order_by("created")
        periods = serializers.serialize("json", all_periods)
        # messages.error("Clock is already start.")
        data = json.dumps({""
                "type":"start-clock",
                "context":periods,
                "message":msg,
                "start_time":planData.clockstart_time,
                "time_status":planData.timerTravel_status,
                # "actual_start":str(newplanobj.actual_start)
                # "actual_start":datetime.timestamp(newplanobj.actual_start)
                # "actual_start":newplanobj.actual_start.split(" ")
            })
        return data
    
@database_sync_to_async
def updatePeriodStatus(params):
    print(params["periodId"])
    period = Period.objects.filter(id=params["periodId"]).update(status=params["status"])
    return 1


@database_sync_to_async
def flagstatus(id):
    planData = NewPlan.objects.get(id=id)
    return planData.is_start

@database_sync_to_async
def updatePeriodincompleteduration(params):
    print(params["incompleteduration"])
    period = Period.objects.filter(id=params["periodId"]).update(incompleteduration=params["incompleteduration"])
    return True

@database_sync_to_async
def updatePeriodDuration(params):
    period = Period.objects.filter(id=params["periodId"]).update(incompleteduration=params["timeRemaining"])
    return 1

import datetime
@database_sync_to_async
def savestarttime(id, time):
    plan = NewPlan.objects.get(id=id)
    plan.clockstart_time = time
    plan.save()
    return 1

@database_sync_to_async
def checkperiod(id):
    period = Period.objects.get(id=id)
    print("###########",period.status)
    
    return 1

@database_sync_to_async
def periodstarttime(params):
    # print("=======",params['ctime'])
    # print("=======",params['periodsId'])
    # if params['periodsId']:
        period = Period.objects.get(id=params['periodsId'])
        period.starttime = params['ctime']
        period.save()
    # else:
    #     plan = NewPlan.objects.get(id=planid)
    #     for pd in plan.periods.all():
    #         pd.starttime = params['ctime']
    #         pd.save()
    #         break
