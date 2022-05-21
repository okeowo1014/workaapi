from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManage(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    TYPE_OF_ACCOUNT = [
        ('employee', 'employee'),
        ('employer', 'employer'),
        ('staff', 'staff'),
        ('administrator', 'administrator'),
    ]
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )

    account_type = models.CharField(max_length=13, choices=TYPE_OF_ACCOUNT)
    REQUIRED_FIELDS = ['account_type']
    USERNAME_FIELD = 'email'
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['email', 'account_type']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    objects = UserManage()


# Create your models here.

class Employee(models.Model):
    GENDER = [
        ['male', 'male'],
        ['female', 'female']
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    other_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=GENDER)
    phone = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default='')
    about = models.TextField(default='')
    cv = models.URLField(default='')
    date_of_birth = models.DateField(null=True, blank=True)
    display_picture = models.URLField(default='https://api.workanetworks.com/media/display-picture/7/download.png')
    uid = models.CharField(max_length=12, unique=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    @property
    def fullname(self):
        return '{} {} {}'.format(self.last_name, self.first_name, self.other_name)


class Staff(models.Model):
    GENDER = [
        ['male', 'male'],
        ['female', 'female']
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_admin')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=GENDER)
    phone = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default='')
    about = models.TextField(default='')
    display_picture = models.URLField(default='https://api.workanetworks.com/media/display-picture/7/download.png')
    uid = models.CharField(max_length=12, unique=True, null=True)
    roles = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

    @property
    def fullname(self):
        return '{} {}'.format(self.last_name, self.first_name)


class Skills(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='skill')
    skill_name = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    year_of_experience = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class WorkExperience(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_experience')
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    current = models.BooleanField(default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True)


class Education(models.Model):
    SCHOOL_LEVEL = [['elementary', 'elementary'],
                    ['high school', 'High School'],
                    ['technician', 'Technician'],
                    ['college', 'College'],
                    ['polytechnic', 'Polytechnic'],
                    ['university', 'University']]
    CERTIFICATION = [('leaving school', 'leaving school'),
                     ('o level', 'o level'),
                     ('nce', 'NCE'),
                     ('diploma', 'Diploma'),
                     ('ond', 'National Diploma'),
                     ('technician', 'Technician'),
                     ('hnd', 'Higher National Diploma'),
                     ('bsc', 'Bachelor of Science'),
                     ('bseng', 'Bachelor of Engineering'),
                     ('btech', 'Bachelor of Technology'),
                     ('bedu', 'Bachelor of Education')
                     ]
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='education')
    school_name = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=SCHOOL_LEVEL)
    certificate = models.CharField(max_length=255, choices=CERTIFICATION)
    course = models.CharField(max_length=255, default='')
    current = models.BooleanField(default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True)


class Language(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='language')
    language = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class Availability(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='availability')
    full_time = models.BooleanField(default=True)
    part_time = models.BooleanField(default=True)
    contract = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)


class Plans(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    max = models.PositiveIntegerField()
    note = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employer(models.Model):
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='registered_plan', default='20220322')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employer', null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(default='')
    company_website = models.CharField(default='', max_length=255)
    position = models.CharField(max_length=255)
    business_scale = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    uid = models.CharField(max_length=10, unique=True, null=True)
    company_logo = models.URLField(default='https://api.workanetworks.com/media/company-logo/b32g3zvg2y/1024.png')
    company_profile = models.TextField(default='')
    reviews = models.DecimalField(max_digits=2, decimal_places=1, default=1.0)
    hired = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255, default='')
    address = models.TextField(default='')
    plan_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

    @property
    def fullname(self):
        return '{} {}'.format(self.last_name, self.first_name)


def joblogofile(instance, filename):
    return '/'.join(['images', str(instance.id), filename])


class JobsPost(models.Model):
    AVAILABILITY = [['available', 'available'],
                    ['hide', 'hide'],
                    ['delete', 'deleted']]
    ACCESS = [['open', 'open'],
              ['closed', 'closed'],
              ['pending', 'pending'],
              ['delete', 'deleted']]
    SALARY_TYPE = [['hourly', 'hour'],
                   ['daily', 'day'],
                   ['weekly', 'week'],
                   ['monthly', 'month'],
                   ['annually', 'annual']]
    JOB_TYPE = [['full time', 'full time'],
                ['part time', 'part time'],
                ['contract', 'contract'],
                ['internship', 'internship'],
                ['voluntary', 'voluntary']]
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='job_employer')
    job_key = models.CharField(max_length=16, unique=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    qualification = models.TextField()
    requirement = models.TextField()
    benefit = models.TextField(default='')
    categories = models.TextField()
    job_type = models.CharField(max_length=255, choices=JOB_TYPE)
    tags = models.TextField(default='')
    validity = models.BooleanField(default=True)
    availability = models.CharField(choices=AVAILABILITY, default='available', max_length=255)
    expiry = models.DateField(null=True)
    applications = models.PositiveIntegerField(default=0)
    access = models.CharField(choices=ACCESS, default='open', max_length=255)
    currency = models.CharField(max_length=10, default='NGN')
    budget = models.CharField(max_length=255)
    is_remote = models.BooleanField(default=False)
    location = models.CharField(max_length=255)
    salary_type = models.CharField(max_length=10, choices=SALARY_TYPE)
    employer_logo = models.URLField(default='')
    message_channel = models.CharField(max_length=16, default='')
    shortlist_date = models.DateTimeField(auto_now_add=True)
    refusal_note = models.TextField(default='Not refused')
    refusal_date = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)


class ApplyJob(models.Model):
    JOB_STATUS = [['processing', 'processing'],
                  ['accept', 'accepted'],
                  ['shortlist', 'shortlisted'],
                  ['decline', 'declined'],
                  ['suspend', 'suspend']]
    applicant = models.ForeignKey(to=Employee, on_delete=models.CASCADE, related_name='job_applicant')
    job = models.ForeignKey(to=JobsPost, on_delete=models.CASCADE, related_name='apply_job')
    status = models.CharField(choices=JOB_STATUS, default='processing', max_length=255)
    note = models.TextField(default='')
    is_new = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}-{}'.format(self.applicant.fullname, self.job.title)


class LikedJobs(models.Model):
    job = models.ForeignKey(JobsPost, on_delete=models.CASCADE, related_name='job_like')
    liker = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='liker')
    created = models.DateTimeField(auto_now_add=True)


class DeletedUsers(models.Model):
    email = models.EmailField()
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    account_type = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    about = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class Support(models.Model):
    email = models.EmailField()
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    title = models.TextField()
    message = models.TextField()
    status = models.CharField(max_length=255, default='open')
    read = models.BooleanField(max_length=255, default=False)
    created = models.DateTimeField(auto_now_add=True)


# api-key: bb3c1e.98f2c0ba5b76933dd5c3e47b01bbc87c

class PlanUpgradeRecord(models.Model):
    STATUS = [['pending', 'pending'],
              ['reject', 'reject'],
              ['confirmed', 'confirmed']]
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='upgrade_record')
    transaction = models.CharField(max_length=225)
    status = models.CharField(choices=STATUS, default='pending', max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class PaymentTrackRecord(models.Model):
    STATUS = [['pending', 'pending'],
              ['reject', 'reject'],
              ['confirmed', 'confirmed']]
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_record')
    payer_account = models.CharField(max_length=225)
    transaction = models.CharField(max_length=225)
    narration = models.CharField(max_length=255)
    status = models.CharField(choices=STATUS, default='pending', max_length=255)
    created = models.DateTimeField(auto_now_add=True)
