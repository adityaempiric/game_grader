from django.urls import path

from timer.views import ClockTimer

urlpatterns = [
    path('timer/<int:id>/', ClockTimer.as_view(), name='clockTimer'),
]
