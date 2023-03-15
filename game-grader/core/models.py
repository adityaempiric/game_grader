from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext as _
import uuid


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # if not username:
        #     raise ValueError('The UserName field must be set')
        if not email:
            raise ValueError(_('Users must have an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email,
            uuid=str(uuid.uuid4().hex[:8]),
            role="Admin",
            **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


ROLE_CHOISE = (
    ('Admin', 'Admin'),
    ('Staff', 'Staff'),
    ('Athlete', 'Athlete'),
)
POSITION_CHOISE = (
    ('QB', 'QB'),
    ('RB', 'RB'),
    ('SB', 'SB'),
    ('FB', 'FB'),
    ('WR', 'WR'),
    ('TE', 'TE'),
    ('OL', 'OL'),
    ('DL', 'DL'),
    ('LB', 'LB'),
    ('NIC', 'NIC'),
    ('SAF', 'SAF'),
    ('CB', 'CB'),
    ('K', 'K'),
    ('P', 'P'),
    ('LS', 'LS'),
)


class User(AbstractUser):
    uuid = models.CharField(max_length=50, primary_key=True)
    # uuid = models.UUIDField(auto_created=True ,max_length=8, primary_key=True, default=uuid.uuid4)
    # uuid = models.UUIDField(primary_key=True, max_length=8, default=uuid.uuid4)
    username = None
    # username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255,unique=True) 
    phone = models.CharField(max_length=12, null=True, blank=True)
    role = models.CharField(
        max_length=10, choices=ROLE_CHOISE, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    graduation = models.IntegerField(null=True, blank=True)
    seasonofaccess = models.CharField(max_length=500, null=True, blank=True)
    biography = models.CharField(max_length=500, null=True, blank=True)
    # positions = models.CharField(max_length=500, null=True, blank=True)
    # positions = ArrayField(models.CharField(
    #     max_length=200, null=True, blank=True), null=True, blank=True)
    positions = ArrayField(models.CharField(
        max_length=200, choices=POSITION_CHOISE, null=True, blank=True), null=True, blank=True)
    tags = models.CharField(max_length=500, null=True, blank=True)
    coverpic = models.ImageField(upload_to='cover_pic', null=True, blank=True)
    transcript = models.FileField(
        upload_to='transcript_pic', null=True, blank=True)
    document = models.FileField(
        upload_to='document_pic', null=True, blank=True)
    # profile_pic = models.ImageField(upload_to='profile', null=True, blank=True)
    # code = models.CharField(max_length = 50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()
 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # def __str__(self):
    #     return "%s %s"%(self.first_name,self.last_name)
    # def __str__(self):
    #     return "%s"%(self.username)


class TeamDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team_code = models.CharField(max_length=50)
    team_name = models.CharField(max_length=50)
    team_description = models.CharField(max_length=500, null=True, blank=True)
    sport = models.CharField(max_length=50, null=True, blank=True)
    team_coverpic = models.ImageField(
        upload_to='team_cover_pic', null=True, blank=True)
    team_iconpic = models.ImageField(
        upload_to='team_icon_pic', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % (self.team_name)


class InviteTeam(models.Model):
    invite_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='invite_by')
    invite_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='invite_to')
    team = models.ForeignKey(TeamDetail, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class ActiveTeam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active_team = models.ForeignKey(TeamDetail, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class TeamMember(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user')
    teamname = models.ForeignKey(TeamDetail, on_delete=models.CASCADE)
    member = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='team_member')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return "%s"%(self.member)


class NewGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    event = models.CharField(max_length=100)
    eventdate = models.DateField(null=True, blank=True)
    sharewith = models.ManyToManyField(User, related_name='sharewith')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


EVENT_CHOISE = (
    ('Game Folder', 'Game Folder'),
    ('Training Phase', 'Training Phase'),
    ('Other', 'Other'),
)


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plantitle = models.CharField(max_length=100)
    foldertype = models.CharField(max_length=20, choices=EVENT_CHOISE)
    eventdate = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return "%s"%(self.plantitle)

STATUS_CHOISE = (
    ('Completed', 'Completed'),
    ('InProgress', 'InProgress'),
    ('Pending', 'Pending'),
    ('inComplete', 'inComplete'),
)
class Period(models.Model):
    periodname = models.CharField(max_length=100)
    duration = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOISE, default='inComplete')
    incompleteduration = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    starttime = models.CharField(max_length=20, null=True,blank=True) 
    


PLAN_CHOISE = (
    ('Practice Plan', 'Practice Plan'),
    ('Meeting Plan', 'Meeting Plan'),
    ('Workout Plan', 'Workout Plan'),
)

# == == == =
#         ('Practice Plan', 'Practice Plan'),
#         ('Meeting Plan', 'Meeting Plan'),
#         ('Workout Plan', 'Workout Plan'),
#     )
# >>>>>>> 881371796e06fee7903efaf3b6da88cf7efd38f1


class NewPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    planname = models.CharField(max_length=100)
    plantype = models.CharField(max_length=20, choices=PLAN_CHOISE)
    scheduledate = models.DateField()
    scheduletime = models.TimeField()
    notification = models.BooleanField(null=True, blank=True)
    periods = models.ManyToManyField(Period, related_name='p')
    events = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_start = models.BooleanField(default=False)
    clockstart_time = models.CharField(max_length=50, null=True, blank=True)
    timerTravel_status = models.BooleanField(default=False, blank=True)
    
    


# for i in NewGame.objects.filter(id=6):

#     print("----------",i,"----------")
    # print("----------",NewPlan.objects.filter(id=9).first().id,"----------")
