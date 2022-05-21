from datetime import datetime

from django import template
from django.db.models import Sum

from administrator.models import Payroll
from api.models import ApplyJob, Employee, Employer, JobsPost, Staff, User
from interview.models import Interviews, ObjectiveInterviewAnswers, TheoryInterviewAnswers

register = template.Library()


@register.filter
def get_shortlist(value):
    if value:
        shortlist = ApplyJob.objects.filter(job__job_key=value, status='shortlist').count()
        return shortlist
    else:
        return 0


@register.filter
def get_interviewed(value):
    if value:
        interviewed = Interviews.objects.filter(job__job_key=value).aggregate(Sum('submission'))
        print(interviewed)
        return interviewed['submission__sum']
    else:
        return 0


@register.filter
def get_options(value):
    if value:
        options = value.split(',')
        return options
    else:
        return []


@register.filter
def sort_employment_request(value):
    if value.mode == 'interview':
        intr = Interviews.objects.get(interview_uid=value.mode_key)
        employer = intr.job.employer
        job = intr.job
    else:
        job = JobsPost.objects.get(job_key=value.mode_key)
        employer = job.employer
    return {'job': job, 'employer': employer}


@register.filter
def get_chat_head(value):
    try:
        employee = Employee.objects.get(uid=value)
        return employee
    except:
        employer = Employer.objects.get(uid=value)
        return employer


@register.filter
def get_chat_dp(value):
    if value.user.account_type == 'employee':
        return value.display_picture
    elif value.user.account_type == 'employer':
        return value.company_logo


@register.filter
def get_req_employee(value):
    return [Employee.objects.get(uid=x) for x in value.split(',')]


@register.filter
def get_employees(value):
    return [Employee.objects.get(user__email=x) for x in value.split(',')]


@register.filter
def check_payroll(value, args):
    try:
        Payroll.objects.get(job__job_key=value, employee__uid=args)
        return True
    except:
        False


@register.filter
def get_roles(value):
    return value.split(',')


@register.filter
def get_staff_roles(value):
    return Staff.objects.get(user=value).roles


@register.filter
def get_support_sender(value):
    try:
        t_user = User.objects.get(email=value)
        if t_user.account_type == 'employee':
            utype = Employee.objects.get(user=t_user)

        elif t_user.account_type == 'employer':
            utype = Employer.objects.get(user=t_user).fullname
        else:
            container = {'registered': True, 'fullname': value, 'last_login': t_user.last_login,
                         'created': t_user.created, 'account_type': t_user.account_type, 'phone': 'not set',
                         'location': 'not set', 'status': t_user.is_active}
        container = {'registered': True, 'fullname': utype.fullname, 'last_login': t_user.last_login,
                     'created': t_user.created, 'account_type': t_user.account_type, 'phone': utype.phone,
                     'location': utype.location, 'status': t_user.is_active}
    except:
        container = {'registered': False}
    return container


@register.filter
def convert_str_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()


@register.filter
def staff_profile(value):
    return Staff.objects.get(user=value).fullname


@register.filter
def objective_score(value, args):
    answer = ObjectiveInterviewAnswers.objects.filter(interview=value, employee=Employee.objects.get(uid=args))
    percent = round(answer.filter(status='correct').count() / answer.count() * 100)
    return '{}%'.format(percent)


@register.filter
def interview_data(value, args):
    if value.interview_type == 'objective':
        answer = ObjectiveInterviewAnswers.objects.filter(interview=value, employee=Employee.objects.get(uid=args))
        percent = '{}%'.format(round(answer.filter(status='correct').count() / answer.count() * 100))
    else:
        answer = TheoryInterviewAnswers.objects.filter(interview=value, employee__uid=args)
        percent = ''
    return {'s_date': answer[0].created, 'percent': percent}


@register.filter
def get_fullname(value):
    if value.account_type == 'employee':
        return Employee.objects.get(user=value).fullname
    else:
        return Employer.objects.get(user=value).fullname
