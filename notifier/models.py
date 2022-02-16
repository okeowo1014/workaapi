from django.db import models

# Create your models here.
from api.models import Employee, Employer, User


class RelatedJobsNotifier(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='related_jobs')
    job_title = models.CharField(max_length=255)
    job_id = models.PositiveIntegerField()
    receivers = models.PositiveIntegerField()
    readers = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)


class DirectEmployeeNotifier(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.TextField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_recieved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class HotEmployeeAlert(models.Model):
    LINK = [['profile', 'profile'],
            ['interview', 'interview'],
            ['inbox', 'inbox']]
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    link = models.CharField(max_length=200, choices=LINK)
    created = models.DateTimeField(auto_now_add=True)


class HotEmployerAlert(models.Model):
    LINK = [['profile', 'profile'],
            ['interview', 'interview'],
            ['inbox', 'inbox']]
    employer = models.OneToOneField(Employer, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    link = models.CharField(max_length=200, choices=LINK)
    created = models.DateTimeField(auto_now_add=True)


class DirectEmployerNotifier(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.TextField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_recieved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


class UserNotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_notification_settings')
    email = models.BooleanField(default=True)
    login = models.BooleanField(default=True)
    update = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
