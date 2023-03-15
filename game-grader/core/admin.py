from django.contrib import admin
from core.models import User, InviteTeam, TeamDetail, ActiveTeam, TeamMember, NewGame, NewPlan, Period, Event

# admin.site.register(NewPlan)
# admin.site.register(Period)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('uuid','email','password','role')

@admin.register(TeamDetail)
class InviteTeamAdmin(admin.ModelAdmin):
    list_display = ('id','user','team_name','team_code')

@admin.register(InviteTeam)
class TeamDetailAdmin(admin.ModelAdmin):
    list_display = ('id','invite_by','invite_to','team')

@admin.register(ActiveTeam)
class ActiveTeamAdmin(admin.ModelAdmin):
    list_display = ('id','user','active_team')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('id','user',"teamname","member")

@admin.register(NewGame)
class NewGameAdmin(admin.ModelAdmin):
    list_display = ('user','title','event','eventdate','get_sharewith')

    def get_sharewith(self,obj):
        return [sharewith.username for sharewith in obj.sharewith.all()]

@admin.register(NewPlan)
class NewPlanAdmin(admin.ModelAdmin):
    list_display = ('id','user','planname','plantype','scheduledate','scheduletime','notification','status','get_period','events', 'timerTravel_status')

    def get_period(self,obj):
        return [periods.periodname for periods in obj.periods.all()]

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('id','periodname','duration','status','incompleteduration','starttime','created','updated')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id','user','plantitle','foldertype','eventdate')