from django.shortcuts import render, redirect
from django.views import View
from core.models import User, TeamDetail, InviteTeam, TeamMember, ActiveTeam, NewGame, Period, NewPlan, Event
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse,HttpResponseBadRequest
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

# Create your views here.
def clock(request):
    return render(request, 'clock.html')

class SignupView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'signup.html')
     
    def post(self, request, *args, **kwargs):
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        confirm_pass = request.POST['confirm_password']
        code = request.POST['team_code']

        if firstname !='':
            if lastname !='':
                if email !='':
                    if not User.objects.filter(email=email).exists():
                        if password !='':
                            if confirm_pass !='':
                                if password == confirm_pass:
                                    uu_id = str(uuid.uuid4().hex[:8])
                                    if code=='':
                                        user = User.objects.create(first_name=firstname,last_name=lastname,email=email, password=password, uuid=uu_id, role='Admin')
                                        user.set_password(password)
                                        user.is_superuser = True
                                        user.is_staff = True
                                        user.is_active = True 
                                        user.save()
                                        messages.success(request, 'User created successfully.')
                                        return redirect('login')
                                    else:
                                        if TeamDetail.objects.filter(team_code=code).exists():
                                            user = User.objects.create(first_name=firstname,last_name=lastname,email=email, password=password, uuid=uu_id)
                                            user.set_password(password)
                                            user.save()
                                            team_detail = TeamDetail.objects.get(team_code=code)
                                            invite_team = InviteTeam.objects.create(invite_by=team_detail.user, invite_to=user, team=team_detail)
                                            invite_team.save()
                                            messages.success(request, 'User created successfully.')
                                            return redirect('login')
                                        else:
                                            messages.error(request, 'ERROR: Please Enter Valid Team-Code.')
                                else:
                                    messages.error(request, "ERROR: Password and Confirm Password are not same.")
                            else:
                                messages.error(request, "ERROR: Please Enter Confirm Password.")
                        else:
                            messages.error(request, "ERROR: Please Enter Password.")
                    else:
                        messages.error(request, "ERROR: User already exist with this email.")
                else:
                    messages.error(request, "ERROR: Please Enter Email.")
            else:
                messages.error(request, "ERROR: Please Enter Lastname.")
        else:
            messages.error(request, "ERROR: Please Enter Firstname.")
        return redirect('signup')

class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        try:
            user = User.objects.get(uuid=request.GET.get('uuid'))
            password = user.password
            # print("&&&&@-@&&&&",password)
            # password = request.GET['password']
            if password=='':
                messages.info(request, 'Generate your New-Password.')
                # print("-->Password: ",password)
                return render(request, 'invited_user_set_password.html')
            return render(request, 'signin.html')
            
        except:
            return render(request, 'signin.html')

    def post(self, request, *args, **kwargs):
        passwords = request.GET.get('password')
        # print("&&&&&&&&",passwords)
        if passwords=='':
            id = request.GET['uuid']
            pass_word = request.POST['password-1']
            conf_pass = request.POST['confirmpassword-1']
            if pass_word==conf_pass:
                user = User.objects.get(uuid=id)
                # user.password=pass_word
                user.set_password(pass_word)
                user.save()
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Login successfully.')
                    return redirect("home")
            else:
                messages.error(request, "Error: Password and Confirm Password  are not same.")
                return render(request, 'invited_user_set_password.html')
        else:
            email = request.POST['email']
            password = request.POST['pass_word']

            user = authenticate(email=email, password=password)
            # print("^^^^^^^^^^^^",user)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successfully.')
                return redirect('home')
            else:
                messages.error(request, "Error: Invalide Login Credential.")
                return render(request, 'signin.html') 


def send_invite_mail(request, user_mail, user):
    current_domain = request.META['HTTP_HOST']
    # print("^^^^^^^^^^^^^^^^^^^^^^^^^",current_domain)
    link = f'http://{current_domain}/login/?password={user.password}&uuid={user.uuid}'
    gmail_user = settings.EMAIL_HOST_USER
    to = [user_mail]
    subject = 'Email Verification'
    body = f"For joining the team Click the link: {link}"
    send_mail(subject=subject, from_email = gmail_user , message=body ,recipient_list =to, fail_silently=False)


class NewteamView(LoginRequiredMixin,UserPassesTestMixin,View):

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        return render(request, 'newteam.html')
    
    def post(self, request, *args, **kwargs):
        team_code = str(uuid.uuid4().hex[:8])
        user = request.user
        team_name = request.POST['new_team_name']
        description = request.POST['new_team_desc']
        sport = request.POST['sport']
        coverpic = request.FILES.get('cover-pic')
        iconpic = request.FILES.get('icon-pic')

        if team_name != '':
            if description != '':
                if sport != '':
                    team = TeamDetail.objects.create(user=user, team_code=team_code, team_name=team_name, team_description=description, sport=sport, team_coverpic=coverpic, team_iconpic=iconpic)
                    team.save()
                    messages.success(request, 'Successfully created a new team.')
                    return render(request, 'newteam.html')
                else:
                    messages.error(request, "ERROR : Please Enter Sport...")
            else:
                messages.error(request, "ERROR : Please Enter Team-Description...")
        else:
            messages.error(request, "ERROR : Please Enter Team-Name...")
        return render(request, 'newteam.html')
        

class InviteTeamView(LoginRequiredMixin,UserPassesTestMixin,View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        # if request.user.is_authenticated:
        #     user = request.user
        #     if user=="Admin":
        if not TeamDetail.objects.filter(user=request.user).exists():
            messages.info(request,"Create team first")
            return redirect("newteam")
        return render(request, 'new_team_member.html')
            # else:
            #     return render(request, 'dashboard.html',{'error':'Error: You are not Admin...'}) 

    def post(self, request, *args, **kwargs):
        f_name = request.POST['f_name']
        l_name = request.POST['l_name']
        email = request.POST['email_address']
        phone = request.POST['phone_number']
        role = request.POST.get('role')
        # print("ROLE:-",role)
        if request.POST['height'] != '': 
            try:
                height = float(request.POST.get('height'))
            except ValueError:
                messages.error(request, 'Invalid input: please enter a number in  Height field')
                return redirect("invite_team")
        else:
            height = None
        # height = float(request.POST['height'])
        if request.POST['weight'] != '':
            try:
                weight = float(request.POST.get('weight'))
            except ValueError:
                messages.error(request, 'Invalid input: please enter a number in  Weight field')
                return redirect("invite_team")
        else:
            weight = None
        # weight = float(request.POST['weight'])
        if request.POST['graduation_year'] != '':
            graduation_year = int(request.POST['graduation_year'])
        else:
            graduation_year = None
        seasons = request.POST.get('basic')
        biography = request.POST['Biography']
        position = request.POST.getlist('position-check')
        tags = request.POST.get('groupsortags')
        coverpic = request.FILES.get('cover-pic')
        transcripts = request.FILES.get('Transcripts')
        document = request.FILES.get('drop-img')
        otherposition = request.POST['other-option']
        if otherposition != '':
            op = otherposition.split(",")
            for i in op:
                position.append(i)

        if f_name != '':
            if l_name != '':
                if email != '':
                    if not User.objects.filter(email=email).exists():
                        if phone != '':
                            if role != None:
                                uu_id = str(uuid.uuid4().hex[:8])
                                user = User.objects.create(uuid=uu_id, first_name=f_name, last_name=l_name, email=email, role=role, phone=phone, height=height, weight=weight, graduation=graduation_year, seasonofaccess=seasons, biography=biography, positions=position, tags=tags, coverpic=coverpic, transcript=transcripts, document=document) 
                                if role=='Admin':
                                    user.is_superuser = True
                                    user.is_staff = True
                                    user.is_active = True
                                    user.save()
                                    messages.success(request, 'User created successfully.')
                                else:
                                    user.save()
                                    messages.success(request, 'User created successfully.')
                                if user is not None:
                                    send_invite_mail(request, email, user)
                                    messages.success(request, f'Invitation sent "{email}" successfully.')
                                    active_team = ActiveTeam.objects.get(user=request.user)
                                    invite_team = InviteTeam.objects.create(invite_by=request.user, invite_to=user, team=active_team.active_team)
                                    invite_team.save()
                                    team_member = TeamMember.objects.create(user=request.user, teamname=active_team.active_team, member=user)
                                    team_member.save()
                                    return redirect('manage_team')
                                else:
                                    messages.error(request, 'ERROR: Try again...Invite not sent.')
                            else:
                                messages.error(request, "ERROR: Please Select Role.")
                        else:
                            messages.error(request, "ERROR: Please Enter Phone-Number.")
                    else:
                        messages.error(request, "ERROR: User already exist with this email.")        
                else:
                    messages.error(request, "ERROR: Please Enter Email.")
            else:
                messages.error(request, "ERROR: Please Enter Last-name.")
        else:
            messages.error(request, "ERROR: Please Enter First-name.")
        return render(request, 'new_team_member.html')


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        user=request.user
        if user.role == 'Admin':   
            
     
            if TeamMember.objects.filter(member=request.user).exists():
                act_teamname = TeamMember.objects.filter(member=request.user)
              
                tm_name = TeamMember.objects.get(member=request.user)
                if tm_name:
                    team_name = tm_name.teamname        
                    context ={
                        "actteamname":act_teamname,
                        "teamname":team_name,
                    }
               
                    return render(request,'profile.html',context=context)
                else:
                    return render(request,'profile.html')    
                
                   
            if TeamDetail.objects.filter(user=request.user).exists():        
                team = TeamDetail.objects.filter(user=request.user)
                if ActiveTeam.objects.filter(user=request.user).exists():
                    
                    acteam = ActiveTeam.objects.get(user=request.user)
                    active_team = acteam.active_team
                    context = {
                        "team":team,
                        "activeTeam":active_team,
                        # "cover_pic" : request.user.coverpic.url
                    }
                    return render(request, 'profile.html',  context=context)
                else:
                    team = TeamDetail.objects.filter(user=request.user)
                    context = {
                        "team":team,
                    }
                    return render(request, 'profile.html',  context=context)
                         
            else:
                messages.error(request,"ERROR: It looks like you don't have any TEAM, so create one first.")
                return render(request, 'profile.html')
            
            
        else:
            teamMemberdetail = InviteTeam.objects.get(invite_to=user)
            team = TeamDetail.objects.filter(team_name=teamMemberdetail.team)
            context = {
                        "team":team,
                    }
            return render(request, 'profile.html',  context=context)
        
        
        
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            if request.FILES['file']:
                user.coverpic = request.FILES['file']
                user.save() 
                print("---------------",user.coverpic)
                pro_img= user.coverpic
                context = {
                "cover_pic":pro_img.url
            }
            return render(request, 'profile.html',  context=context)
        except:
                user.save()
        
       
        try:
            if request.POST['firstname']:
                user.first_name = request.POST['firstname']
                user.save()
                messages.success(request, 'Successfully updated the FirstName.') 
        except:
                user.save()
        try:
            if request.POST['lastname']:
                user.last_name = request.POST['lastname']
                user.save()
                messages.success(request, 'Successfully updated the LastName.') 
        except:
                user.save()
        try:
           
            tm_data = TeamDetail.objects.get(user=request.user, team_name=request.POST['team'])
          
          
            
            if tm_data != None or tm_data != '':
                
                if ActiveTeam.objects.filter(user=request.user).exists():
                    acteam = ActiveTeam.objects.get(user=request.user)
                    
                    acteam.active_team = tm_data
                    acteam.save()
                    messages.success(request, f'Your Active-Team is {tm_data}.')
                else:
                    
                    activeteam = ActiveTeam.objects.create(user=request.user,active_team=tm_data)
                    activeteam.save()
                    
            else:
                
                messages.error(request, "ERROR: It looks like you don't have any TEAM, so create one first.")

        except:
            # print("end----------------")
            pass
        return render(request, 'profile.html')
      
class ManageTeamView(LoginRequiredMixin,UserPassesTestMixin,View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        if ActiveTeam.objects.filter(user=request.user).exists():
            active_team = ActiveTeam.objects.get(user=request.user)
            # teamname=active_team.active_team
            # team_members = TeamMember.objects.filter(user=request.user, teamname=active_team.active_team)
            team_members = TeamMember.objects.filter(user=request.user)
            admin_c = []
            staff_c = []
            Athletes_c = []
            for i in team_members:
                # print(i.member.role)
                if i.member.role == "Admin":
                    admin_c.append(i.member.first_name)
                elif i.member.role == "Staff":
                    staff_c.append(i.member.first_name)
                else:
                    Athletes_c.append(i.member.first_name) 
            context = {
                'active_team': active_team.active_team,
                'team_member':len(team_members),
                'team_members':team_members,
                'admins': len(admin_c),
                'staff' : len(staff_c),
                'athletes': len(Athletes_c)
            }
            return render(request, 'manageteam.html', context=context)
        else:
            return render(request, 'manageteam.html')
    
class HomeView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        print("*****###****",request.user.role)
        user = request.user
        team_members = TeamMember.objects.filter(user=request.user)
    # if request.user.is_authenticated:
        if user.role == 'Staff' or user.role == 'Athlete':
                print("*********",request.user.role)
                findtm = TeamMember.objects.get(member=request.user)
                # for i in findtm:
                print("^^^^^^^^",findtm.teamname)
                print("^^^^^^^^",findtm.user)

                today = datetime.datetime.now().date()
                week_start = today - datetime.timedelta(days=today.weekday())
                week_end = week_start + datetime.timedelta(days=6)
                dates_in_week = [week_start + datetime.timedelta(days=i) for i in range(7)]

                planData = NewPlan.objects.filter(user=findtm.user).order_by("scheduledate")
                date_range = f"{week_start.strftime('%-d %b')} - {week_end.strftime('%-d %b')}"

                today = datetime.date.today()
                formatted_date = today.strftime('%Y-%m-%d')

                if NewPlan.objects.filter(user=findtm.user, scheduledate=formatted_date).exists():
                    today_plan = NewPlan.objects.filter(user=findtm.user, scheduledate=formatted_date)
                    # for i in today_plan:
                        # print("*******#####*******",i.planname)
                    final_duration = 0
                    for plan_duration in today_plan:
                        for i in plan_duration.periods.all():
                            final_duration += i.duration

                        total_min = final_duration
                        plan_hours = total_min // 60
                        plan_minutes = total_min % 60
                        plan_times = "{} hr {} min".format(plan_hours, plan_minutes)
                else:
                    plan_times = "0 hr 0 min"

                plan_list = []
                for PD in planData:
                    # print("###^^",PD.planname)
                    total_duration = 0
                    if PD.scheduledate in dates_in_week:
                        print("*********",PD.scheduledate)
                        for i in PD.periods.all():
                            total_duration += i.duration

                        total_minutes = total_duration
                        hours = total_minutes // 60
                        minutes = total_minutes % 60
                        times = "{} hr {} min".format(hours, minutes)

                        date = datetime.datetime.strptime(str(PD.scheduledate), "%Y-%m-%d")
                        day_name = date.strftime("%A")
                        month_name = date.strftime("%B")
                        rowdate = str(PD.scheduledate).split("-")
                        formated_dates = "{}, {} {}, {}".format(day_name, month_name, rowdate[2], rowdate[0])

                        plan_list.append({
                            "plan":PD,
                            "date":formated_dates,
                            "duration":times
                        })
                context = {
                "team_member":len(team_members),
                "plan_duration":plan_times,
                "current_week":date_range,
                "plan_list":plan_list
                }
                # print("--------",context)
                return render(request, 'home.html', context=context)

        else:
            today = datetime.datetime.now().date()
            week_start = today - datetime.timedelta(days=today.weekday())
            week_end = week_start + datetime.timedelta(days=6)
            dates_in_week = [week_start + datetime.timedelta(days=i) for i in range(7)]

            date_range = f"{week_start.strftime('%-d %b')} - {week_end.strftime('%-d %b')}"

            today = datetime.date.today()
            formatted_date = today.strftime('%Y-%m-%d')

            if InviteTeam.objects.filter(invite_to=request.user).exists():
                user = InviteTeam.objects.get(invite_to=request.user)
                # print("****",user.invite_by)
                planobj = NewPlan.objects.filter(user=user.invite_by).order_by("scheduledate")
                # for i in planobj:
                #     print("^^^^^^",i.planname)
                today_plan = NewPlan.objects.filter(user=user.invite_by, scheduledate=formatted_date)
                final_duration = 0
                for plan_duration in today_plan:
                    for i in plan_duration.periods.all():
                        final_duration += i.duration

                    total_min = final_duration
                    plan_hours = total_min // 60
                    plan_minutes = total_min % 60
                    plan_time = "{} hr {} min".format(plan_hours, plan_minutes)

                if not today_plan:
                    plan_time = "0 hr 0 min"

                plan_list = []
                for plan in planobj:
                    total_duration = 0
                    if plan.scheduledate in dates_in_week:
                        # print("*********",plan.scheduledate)
                        for i in plan.periods.all():
                            total_duration += i.duration

                        total_minutes = total_duration
                        hours = total_minutes // 60
                        minutes = total_minutes % 60
                        time = "{} hr {} min".format(hours, minutes)

                        date = datetime.datetime.strptime(str(plan.scheduledate), "%Y-%m-%d")
                        day_name = date.strftime("%A")
                        month_name = date.strftime("%B")
                        rowdate = str(plan.scheduledate).split("-")
                        formated_date = "{}, {} {}, {}".format(day_name, month_name, rowdate[2], rowdate[0])

                        plan_list.append({
                            "plan":plan,
                            "date":formated_date,
                            "duration":time
                        })
                context = {
                    "team_member":len(team_members),
                    "plan_duration":plan_time,
                    "current_week":date_range,
                    "plan_list":plan_list
                }
                return render(request, 'home.html', context=context)
            else:
                planobj = NewPlan.objects.filter(user=request.user).order_by("scheduledate")

                today_plan = NewPlan.objects.filter(user=request.user, scheduledate=formatted_date)
                # for i in today_plan:
                #     print("*******#####*******",i.planname)
                final_duration = 0
                for plan_duration in today_plan:
                    for i in plan_duration.periods.all():
                        final_duration += i.duration

                    total_min = final_duration
                    plan_hours = total_min // 60
                    plan_minutes = total_min % 60
                    plan_time = "{} hr {} min".format(plan_hours, plan_minutes)

                if not today_plan:
                    plan_time = "0 hr 0 min"

                plan_list = []
                for plan in planobj:
                    total_duration = 0
                    if plan.scheduledate in dates_in_week:
                        # print("*********",plan.scheduledate)
                        for i in plan.periods.all():
                            total_duration += i.duration

                        total_minutes = total_duration
                        hours = total_minutes // 60
                        minutes = total_minutes % 60
                        time = "{} hr {} min".format(hours, minutes)

                        date = datetime.datetime.strptime(str(plan.scheduledate), "%Y-%m-%d")
                        day_name = date.strftime("%A")
                        month_name = date.strftime("%B")
                        rowdate = str(plan.scheduledate).split("-")
                        formated_date = "{}, {} {}, {}".format(day_name, month_name, rowdate[2], rowdate[0])
                        plan_list.append({
                            "plan":plan,
                            "date":formated_date,
                            "duration":time
                        })
                context = {
                    "team_member":len(team_members),
                    "plan_duration":plan_time,
                    "current_week":date_range,
                    "plan_list":plan_list
                }
                return render(request, 'home.html', context=context)


@method_decorator(csrf_exempt, name='dispatch')
class PeriodDataView(LoginRequiredMixin,View):
    def get(self, request, id, *args, **kwargs):
        if request.user.is_authenticated:
            plan_data = NewPlan.objects.get(id=id)
            data = plan_data.periods.all().order_by("created")
            total_duration = 0
            for i in data:
                total_duration += i.duration
            total_minutes = total_duration
            hours = total_minutes // 60
            minutes = total_minutes % 60
            time = "{} hr {} min".format(hours, minutes)
            context = {
                "id": id,
                "plan_data":plan_data,
                "period_data":data,
                "duration":time
            }
            return render(request, 'monday.html', context=context)
        else:
            return redirect("login")

    def post(self, request, id, *args, **kwargs):
        # try:
        if request.POST.get('Travelstatus') != '':
            print("+===============>",request.POST['id'])
            print("+===============>",request.POST.get('Travelstatus'))
            
            id = request.POST['id']
            status = request.POST.get('Travelstatus')
            
            N_Plan = NewPlan.objects.get(id=request.POST['id'])
            N_Plan.timerTravel_status=status
            N_Plan.save()
            return render(request, 'monday.html')
            
        # except:
        #     pass
        else:
            period_id = request.POST['id']
            # status = request.POST.get('status')
            period_title = request.POST['periodtitle']
            period_duration = request.POST['periodduration'].split(" ")
            plan_data_id = request.POST['planid']
            
            

            plan_data = NewPlan.objects.filter(user=request.user, id=plan_data_id)
            for i in plan_data:
                for pd in i.periods.filter(id=period_id):
                    pd.periodname = period_title
                    pd.duration = period_duration[0]
                    pd.save()
            return render(request, 'monday.html')
    
    # def home(self,request):
    #     t,created = NewPlan.objects.get(id=request.POST.get('id'))
    #     print("||||||||||||||||||||",t)
    #     return render(request,'monday.html',{'timetravel':t})

    # def toggle(request):
    #     t = NewPlan.objects.get(id = request.POST['id'])
    #     t.timerTravel_status =request.POST['status'] =='True'
    #     print("getting the t ",t)
    #     t.save()
        
    #     return HttpResponse('success on toggle')  
        
        
@method_decorator(csrf_exempt, name='dispatch')
class PlannerView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(user=request.user)
        team_members = TeamMember.objects.filter(user=request.user)
        context = {
            "team_member":len(team_members),
            "eventlen":len(events),
            "events":events,
        }
        return render(request, 'planner.html', context=context)

    def post(self, request, *args, **kwargs):
        
        evetobj = Event.objects.get(id=request.POST['id'])
        planobj = NewPlan.objects.filter(user=request.user, events=evetobj)

        response_data = []
        for pd in planobj:
            # print("*******",pd.scheduletime)
            # print("*******",pd.periods.all())
            total_duration = 0
            for i in pd.periods.all():
                total_duration += i.duration

            total_minutes = total_duration
            hours = total_minutes // 60
            minutes = total_minutes % 60
            time = "{} hr {} min".format(hours, minutes)
            # print(time)
            # date = pd.scheduledate
            date = datetime.datetime.strptime(str(pd.scheduledate), "%Y-%m-%d")
            day_name = date.strftime("%A")
            month_name = date.strftime("%B")
            rowdate = str(pd.scheduledate).split("-")
            formated_date = "{}, {} {}, {}".format(day_name, month_name, rowdate[2], rowdate[0])

            response_data.append({
                "status":pd.status,
                "planid":pd.id,
                "planname":pd.planname,
                "plantype":pd.plantype,
                "starttime":pd.scheduletime, 
                "duration":time, 
                "date":formated_date, 
                "evetobj":evetobj.plantitle
                })
        # print(response_data)
        return JsonResponse(response_data, safe=False)

class NewPlanView(LoginRequiredMixin,UserPassesTestMixin,View):
    
    def test_func(self):
        return self.request.user.is_superuser

    def convert_12_to_24(self,time_str):
        time_obj = datetime.datetime.strptime(time_str, '%I:%M %p')
        return time_obj.strftime('%H:%M:%S')

    def check_date(self,input_date):
        current_date = datetime.datetime.now().date()
        if input_date < current_date:
            return False
        else:
            return True

    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(user=request.user)
        context = {
            "events":events
        }
        return render(request, 'new_plan.html', context=context)

    def post(self, request, *args, **kwargs):
        title = request.POST['plan_title']
        ptype = request.POST.get('plan_type')
        schedule_date = request.POST['schedule_date']
        schedule_time = request.POST['schedule_time']
        name = request.POST.getlist('Name[]')
        durations = request.POST.getlist('Duration[]')
        eventid = request.POST.get('event_name')

        if request.POST.get('Released') != None:
            status = request.POST.get('Released')  
        else:
            status = request.POST.get('Draft')

        if request.POST.get('notifications') == 'on':
            notification = True
        else:
            notification = False

        if title != '':
            if ptype != None:
                if eventid != 'Select Event':
                    eventobj = Event.objects.get(user=request.user, id=eventid)
                    if schedule_date != '':
                        input_date = datetime.datetime.strptime(str(schedule_date), "%Y-%m-%d").date()
                        result = self.check_date(input_date)
                        if result:
                            if schedule_time != '':
                                schedule_time = self.convert_12_to_24(schedule_time)
                                # print("^^^^^^^^^^",schedule_time)
                                if name != '':
                                    if durations != '':
                                        newplan = NewPlan.objects.create(user=request.user, planname=title, plantype=ptype, events=eventobj, scheduledate=schedule_date, scheduletime=schedule_time.split(" ")[0], notification=notification, status=status)
                                        for i in range(len(durations)):
                                            priod = Period(periodname=name[i], duration=int(durations[i]))
                                            priod.save()
                                            newplan.periods.add(priod)
                                            newplan.save()
                                            messages.success(request, 'New-Plan created successfully.')   
                                        return redirect("plan_data",id=newplan.id)
                                    else:
                                        messages.error(request, "ERROR: Please Enter atleast one Period-Duration.")
                                else:
                                    messages.error(request, "ERROR: Please Enter Period-Name.")
                            else:
                                messages.error(request, "ERROR: Please Select Schedule-Time.")
                        else:
                            messages.error(request, "ERROR: You can not select past date for new event.")
                    else:
                        messages.error(request, "ERROR: Please Select Schedule-Date.")
                else:
                    messages.error(request, "ERROR: Please Select Event.")
            else:
                messages.error(request, "ERROR: Please Select Plan-Type.")
        else:
            messages.error(request, "ERROR: Please Enter Title.")
        return redirect('new_plan')

# class NewTimerView(LoginRequiredMixin,View):
#      def get(self, request, *args, **kwargs):
#         user=request.user
#         print("got the user/////////////",user)
#         if user.role == 'Admin':   
                      
#             if NewPlan.objects.filter(user=request.user).exists():
#                 timer_user = NewPlan.objects.filter(user=request.user)
#                 print("",timer_user)
#                 # tm_name = TeamMember.objects.get(member=request.user)
#                 # if tm_name:
#                 #     team_name = tm_name.teamname        
#                 #     context ={
#                 #         "actteamname":act_teamname,
#                 #         "teamname":team_name,
#                 #     }
               
#                 return render(request,'timer.html')
#             else:
#                 return render(request,'timer.html')    

class NewEventView(LoginRequiredMixin,UserPassesTestMixin,View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        return render(request, 'new_event.html')

    def post(self, request, *args, **kwargs):
        plantitle = request.POST['title_name']
        foldertype = request.POST.get('plan_type')
        eventdate = request.POST['event_date']
        if plantitle != '':
            if foldertype != None:
                if eventdate != '':
                    if Event.objects.filter(plantitle=plantitle).exists():
                        messages.error(request, "ERROR: Plan-Title already exists.Please you can choose another title. ")
                        return render(request, 'new_event.html')
                    else:
                        event = Event.objects.create(user=request.user, plantitle=plantitle, foldertype=foldertype, eventdate=eventdate)
                        event.save()
                        messages.success(request, 'New-Event created successfully.')   
                        return redirect("planner")
                else:
                    messages.error(request, "ERROR: Please Enter Event-Date.")
            else:
                messages.error(request, "ERROR: Please Select Folder-Type.")
        else:
            messages.error(request, "ERROR: Please Enter Plan-Title.")
        return render(request, 'new_event.html')


def log_out(request):
        logout(request)
        messages.success(request, 'You have successfully logged out.')   
        return redirect('login')

# # Change user coverpic
class ChangeUserCoverpicView(LoginRequiredMixin,View):
    def post(self,request):
        # if request.method == 'POST':
        #     uploaded_file = request.FILES['uploaded_file']
        #     update_profile = User.objects.get(uuid=request.user.uuid)
        #     update_profile.coverpic = uploaded_file
        #     update_profile.save()
        #     return HttpResponse(update_profile.coverpic.url)
        try:
            uploaded_file = request.FILES['uploaded_file']
            user = get_object_or_404(User, uuid=request.user.uuid)
            user.coverpic = uploaded_file
            user.save()
            return HttpResponse(user.coverpic.url)
        except (KeyError, User.DoesNotExist):
            return HttpResponseBadRequest("Invalid request or user does not exist") 