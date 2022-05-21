from django.db import models

# Create your models here.
from api.models import Employer, JobsPost, Employee, Staff, User
from interview.models import EmploymentRequest


class Employment(models.Model):
    STATUS = [
        ['active', 'active'],
        ['cancelled', 'cancelled'],
        ['suspended', 'suspended'],
    ]
    req = models.ForeignKey(EmploymentRequest, on_delete=models.CASCADE, related_name='processed_employment')
    currency = models.CharField(max_length=4)
    salary = models.PositiveIntegerField()
    resumption = models.DateField()
    employees_email = models.TextField()
    job = models.ForeignKey(JobsPost, on_delete=models.CASCADE, related_name='employed_job')
    status = models.CharField(max_length=255, choices=STATUS, default='active')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['job', 'employees_email']


class Payroll(models.Model):
    JOB_STATUS = [
        ['active', 'active'],
        ['cancelled', 'cancelled'],
        ['suspended', 'suspended'],
    ]
    PAYMENT_STATUS = [
        ['active', 'active'],
        ['completed', 'completed'],
        ['suspended', 'suspended'],
    ]
    job = models.ForeignKey(JobsPost, on_delete=models.CASCADE, related_name='payroll_job')
    payment_key = models.CharField(max_length=16)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employed')
    currency = models.CharField(max_length=4)
    salary = models.PositiveIntegerField()
    monthly_charge = models.PositiveIntegerField()
    resumption = models.DateField()
    resignation = models.DateField(null=True)
    payment = models.PositiveIntegerField()
    balance = models.PositiveIntegerField(default=0)
    job_status = models.CharField(max_length=200, choices=JOB_STATUS, default='active')
    payment_status = models.CharField(max_length=200, choices=PAYMENT_STATUS, default='active')
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['job', 'employee']


class PayrollHistory(models.Model):
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='payroll_history')
    amount = models.PositiveIntegerField()
    balance = models.PositiveIntegerField()
    transaction = models.CharField(max_length=255)
    payer = models.ForeignKey(Staff, on_delete=models.ForeignKey)
    created = models.DateTimeField(auto_now=True)


class AdminNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_notes')
    note = models.TextField()
    writer = models.ForeignKey(Staff, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class UserLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_logs')
    note = models.TextField()
    created = models.DateTimeField()


class JobLogs(models.Model):
    LOG = [
        ['post', 'post'],
        ['interview', 'interview'],
        ['shortlist', 'shortlist'],
        ['close', 'close'],
        ['update', 'update'],
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_logs')
    log = models.CharField(max_length=200, choices=LOG)
    note = models.TextField()
    created = models.DateTimeField()


class AdminLog(models.Model):
    LOG = [
        ['post', 'post'],
        ['request', 'support'],
        ['support', 'support'],
        ['delete', 'delete'],
        ['upgrade', 'upgrade'],
        ['payment', 'payment'],
        ['joined', 'joined'],
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    log = models.CharField(max_length=200, choices=LOG)
    note = models.TextField()
    created = models.DateTimeField()
