from django.urls import path, include
from core.views import SignupView, LoginView, InviteTeamView, ProfileView, ManageTeamView, HomeView, NewPlanView, NewEventView, log_out, PeriodDataView, NewteamView , PlannerView, ChangeUserCoverpicView

urlpatterns = [
    path('', LoginView.as_view(),),
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('home/', HomeView.as_view(), name='home'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('newteam/',NewteamView.as_view(),name='newteam'),
    path('manageteam/', ManageTeamView.as_view(), name='manage_team'),
    path('inviteteam/', InviteTeamView.as_view(), name='invite_team'),
    path('newplan/', NewPlanView.as_view(), name='new_plan'),
    path('newevent/', NewEventView.as_view(), name='new_event'),
    path('monday/<int:id>',PeriodDataView.as_view(),name="plan_data"),
    path('planner/',PlannerView.as_view(),name="planner"),
    path('changecoverpic/',ChangeUserCoverpicView.as_view(),name="coverpic"),
    path('logout/', log_out, name='logout'),
    # path('dashboard/', DashboardView.as_view(), name='dashboard'),
    # path('addgame/', AddgameView.as_view(), name='addgame'),
]