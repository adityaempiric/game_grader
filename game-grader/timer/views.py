from django.shortcuts import render, redirect
from django.views import View
from core.models import NewPlan

class ClockTimer(View):
    def get(self, request, id, *args, **kwargs):
        PlanData = NewPlan.objects.get(id=id)
        context = {
            "plandata":1,
        }
        return render(request, 'timer/clock.html')