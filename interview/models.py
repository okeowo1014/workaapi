from django.db import models

# Create your models here.
from api.models import JobsPost, Employee


class Interviews(models.Model):
    STATUS = [
        ['closed', 'closed'],
        ['open', 'open'],
        ['suspended', 'suspended']
    ]
    Q_TYPE = [
        ['objective', 'objective'],
        ['theory', 'theory']]
    job = models.ForeignKey(JobsPost, on_delete=models.CASCADE, related_name='job_interview')
    interview_uid = models.CharField(max_length=8, default='')
    title = models.CharField(max_length=255)
    note = models.TextField()
    status = models.CharField(max_length=255, choices=STATUS, default='open')
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    timer = models.BooleanField(default=False)
    submission = models.IntegerField(default=0)
    timer_sec = models.IntegerField(default=0)
    interview_type = models.CharField(max_length=20, choices=Q_TYPE)
    created = models.DateTimeField(auto_now_add=True)


class ObjectiveInterviewQuestions(models.Model):
    question_uid = models.CharField(max_length=7)
    interview = models.ForeignKey(Interviews, on_delete=models.CASCADE, related_name='obj_interview_question')
    question = models.TextField()
    options = models.TextField()
    sub_answer = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)


class TheoryInterviewQuestions(models.Model):
    question_uid = models.CharField(max_length=9)
    interview = models.ForeignKey(Interviews, on_delete=models.CASCADE, related_name='theory_interview_question')
    question = models.TextField()
    sub_answer = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)


class ObjectiveInterviewAnswers(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_obj_interview')
    interview = models.ForeignKey(Interviews, on_delete=models.CASCADE, related_name='obj_interview_answer')
    question = models.ForeignKey(ObjectiveInterviewQuestions, on_delete=models.CASCADE,
                                 related_name='obj_interview_question')
    answer = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)


class TheoryInterviewAnswers(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_theory_interview')
    interview = models.ForeignKey(Interviews, on_delete=models.CASCADE, related_name='theory_interview_answer')
    question = models.ForeignKey(TheoryInterviewQuestions, on_delete=models.CASCADE,
                                 related_name='theory_interview_question')
    answer = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)


class EmploymentRequest(models.Model):
    interview = models.ForeignKey(Interviews, on_delete=models.CASCADE)
    employees = models.TextField()
    note = models.TextField()
    created = models.DateTimeField()
