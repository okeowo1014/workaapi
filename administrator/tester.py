import os

import requests
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from djoser.conf import django_settings
from django.shortcuts import render, redirect

# Create your views here.
from administrator.serializers import StaffSerializer
from api.extractor import generate_employer_key
from api.models import Employee, Employer, JobsPost, ApplyJob, Staff
from api.views import getuser
from chat.models import DMChatMessage
from chat.serializers import DMChatChannelSerializer
from chat.views import get_channel
from interview.models import Interviews, ObjectiveInterviewAnswers, TheoryInterviewAnswers
from interview.serializers import IEmployeeSerializer, ViewObjEmployeeInterviewSerializer, \
    ViewTheoryEmployeeInterviewSerializer, ViewObjInterviewSerializer, ViewTheoryInterviewSerializer
from interview.views import get_employee


def employee_list_card(request):
    if request.POST:
        param = request.POST['param']
        employees = Employee.objects.filter(
            Q(first_name__contains=param) | Q(last_name__contains=param) | Q(user__email__contains=param) | Q(
                location__contains=param) | Q(other_name__contains=param) | Q(
                gender__contains=param) | Q(phone__contains=param))
        return render(request, 'administrator/employee-list-card.html',
                      context={'employees': employees, 'search': True, 'found': employees.count()})

    employees = Employee.objects.all()
    return render(request, 'administrator/employee-list-card.html',
                  context={'employees': employees})


def employer_list_card(request):
    if request.POST:
        param = request.POST['param']
        employers = Employer.objects.filter(
            Q(first_name__contains=param) | Q(last_name__contains=param) | Q(user__email__contains=param) | Q(
                location__contains=param) | Q(company_email__contains=param) | Q(
                company_name__contains=param) | Q(phone__contains=param))
        return render(request, 'administrator/employer-list-card.html',
                      context={'employers': employers, 'search': True, 'found': employers.count()})

    employers = Employer.objects.all()
    return render(request, 'administrator/employer-list-card.html',
                  context={'employers': employers})


def employee_details(request, pid):
    employee = Employee.objects.get(uid=pid)
    skills = employee.skill.all()
    work_experiences = employee.work_experience.all()
    educations = employee.education.all()
    availabilities = employee.availability.all()
    languages = employee.language.all()
    transactions = employee.user.payment_record.all()
    employee_folder = os.path.join('/home/worka/media',str(employee.uid))
    print(employee_folder)
    applied_jobs = employee.job_applicant.all().count()
    shortlist = employee.job_applicant.filter(status='shortlist')
    shortlists = shortlist.count()
    # from interview filter jobs which employee is shortlisted
    interviews = Interviews.objects.filter(job__in=shortlist.values('job')).count()
    user_documents = []
    if os.path.isdir(employee_folder):
        for root, dirs, files in os.walk(employee_folder):
            for name in files:
                filename = os.path.join(root, name)
                filename = '/'.join(filename.split('/')[3:])
                file_url = '{0}://{1}/{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, filename)
                if name.endswith(('jpg', '.jpeg', '.png')):
                    doc_type = 'image'
                elif name.endswith('.pdf'):
                    doc_type = 'pdf'
                else:
                    doc_type = 'doc'
                file = {'url': file_url, 'name': name, 'type': doc_type}
                user_documents.append(file)
    return render(request, 'administrator/employee-details.html',
                  context={'applicant': employee, 'skills': skills, 'work_experiences': work_experiences,
                           'educations': educations, 'availabilities': availabilities, 'documents': user_documents,
                           'languages': languages, 'applied_jobs': applied_jobs, 'shortlists': shortlists,
                           'interviews': interviews,'transactions':transactions})


def employer_details(request, pid):
    employer = Employer.objects.get(uid=pid)
    posted_jobs = employer.job_employer.all()
    interviews = Interviews.objects.filter(job__employer=employer)
    employer_folder = os.path.join('/home/worka/media', str(employer.uid),'company-logo')
    user_documents = []
    transactions = employer.user.payment_record.all()
    if os.path.isdir(employer_folder):
        for root, dirs, files in os.walk(employer_folder):
            print(root)
            for name in files:
                filename = os.path.join(root, name)
                filename = '/'.join(filename.split('/')[3:])
                file_url = '{0}://{1}/{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, filename)
                if name.endswith(('jpg', '.jpeg', '.png')):
                    doc_type = 'image'
                elif name.endswith('.pdf'):
                    doc_type = 'pdf'
                else:
                    doc_type = 'doc'
                print(filename)
                file = {'url': file_url, 'name': name, 'type': doc_type}
                user_documents.append(file)
    return render(request, 'administrator/employer-details.html',
                  context={'employer': employer, 'posted_jobs': posted_jobs, 'interviews': interviews,
                           'documents': user_documents,'transactions':transactions})


def job_listing(request):
    jobs = JobsPost.objects.all()
    return render(request, 'administrator/job-card-list.html', context={'jobs': jobs})


def job_details(request, job_key):
    job = JobsPost.objects.get(job_key=job_key)
    requirements = job.requirement.splitlines()
    qualifications = job.qualification.splitlines()
    benefits = job.benefit.splitlines()
    return render(request, 'administrator/job-details.html',
                  context={'requirements': requirements, 'qualifications': qualifications, 'benefits': benefits,
                           'job': job})


def job_applications(request, job_key):
    applications = ApplyJob.objects.filter(job__job_key=job_key)
    return render(request, 'administrator/job-applications.html', context={'applications': applications})


def interview_list(request):
    interviews = Interviews.objects.all()
    return render(request, 'administrator/interview-list.html', context={'interviews': interviews})


def interview_submissions(request, uid):
    interview = Interviews.objects.get(interview_uid=uid)
    if interview.interview_type == 'objective':
        submitted =  ObjectiveInterviewAnswers.objects.filter(interview=interview).distinct('employee')

        # serializer = IEmployeeSerializer(submitted, many=True)
    elif interview.interview_type == 'theory':
        submitted = TheoryInterviewAnswers.objects.filter(interview=interview).distinct('employee')
        # serializer = IEmployeeSerializer(submitted, many=True)

    return render(request, 'administrator/interview-submission-list.html',
                  context={'submitted': submitted, 'interview': interview})


def view_employee_interview_answer(request, iid, uid):
    employee = Employee.objects.get(uid=uid)
    interview = Interviews.objects.get(interview_uid=iid)
    if interview.interview_type == 'objective':
        answer = ObjectiveInterviewAnswers.objects.filter(interview=interview, employee=employee)
        percent = round(answer.filter(status='correct').count() / answer.count() * 100)
        serializer = ViewObjEmployeeInterviewSerializer(answer, many=True)
    elif interview.interview_type == 'theory':
        answer = TheoryInterviewAnswers.objects.filter(interview=interview, employee=employee)
        serializer = ViewTheoryEmployeeInterviewSerializer(answer, many=True)
        percent = -1
    return render(request, 'administrator/interview-answers.html',
                  context={'items': serializer.data, 'percent': percent, 'interview': interview, 'applicant': employee})
    # return Response(dict(q_and_a=serializer.data, percent=percent), status=status.HTTP_200_OK)


def interview_questions(request, iid):
    interview = Interviews.objects.get(interview_uid=iid)
    if interview.interview_type == 'objective':
        serializer = ViewObjInterviewSerializer(interview, many=False)
    else:
        serializer = ViewTheoryInterviewSerializer(interview, many=False)
    return render(request, 'administrator/interview-questions.html',
                  context={'items': serializer.data, 'interview': interview})


def admin_chat(request):
    heads = DMChatMessage.objects.all().values('chatid').distinct()
    head_channels = [get_channel(head['chatid']) for head in heads]
    serializer = DMChatChannelSerializer(head_channels, many=True)
    print(serializer.data)
    return render(request, 'administrator/admin-chat.html', context={'heads': serializer.data})


def admin_read_chat(request, chat_id):
    head_channels = get_channel(chat_id)
    serializer = DMChatChannelSerializer(head_channels, many=True)
    print(serializer.data)
    return render(request, 'administrator/admin-chat.html', context={'heads': serializer.data})


def add_staff(request):
    if request.POST:
        serializer = StaffSerializer(data=request.POST)
        payload = {'email': request.POST['email'], 'password': request.POST['password'],
                   're_password': request.POST['confirm_password'],
                   'account_type': 'staff'}
        url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-list'))
        if serializer.is_valid():
            response = requests.post(url, data=payload)
            if response.status_code == 201:
                # print("{0} {1} {0}".format('hello', userid))
                serializer.save(user=getuser(response.json().get('id')), uid=generate_employer_key())
                messages.success(request, 'Account Created Successfully')
                return redirect('administrator:staff_login')
            else:
                return print(response.json())
        return print(serializer.errors)
    return render(request, 'administrator/staff-register.html')


def staff_login(request):
    if request.POST:
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('administrator:index')
        else:
            messages.error(request, 'Incorrect email or password')
            return redirect('administrator:staff_login')
    return render(request, 'administrator/staff-login.html')


today = timezone.now()
year, week, _ = now().isocalendar()


@login_required(login_url='administrator:req_login')
def index(request):
    jobs = JobsPost.objects.all()
    interviews = Interviews.objects.all()
    employees = Employee.objects.all()
    employers = Employer.objects.all()
    jobs_count = JobsPost.objects.all().count()
    interviews_count = Interviews.objects.all().count()
    employees_count = Employee.objects.all().count()
    employers_count = Employer.objects.all().count()
    jobs_this_month = jobs.filter(created__month=today.month).count()
    interviews_this_month = interviews.filter(created__month=today.month).count()
    employees_this_month = employees.filter(created__month=today.month).count()
    employers_this_month = employers.filter(created__month=today.month).count()
    jobs_this_week = jobs.filter(created__week=week).count()
    interviews_this_week = interviews.filter(created__week=week).count()
    employees_this_week = employees.filter(created__week=week).count()
    employers_this_week = employers.filter(created__week=week).count()
    staff_user = Staff.objects.get(user=request.user)
    return render(request, 'administrator/dashboard.html',
                  context={'job_count': jobs_count, 'employees_count': employees_count,
                           'employers_count': employers_count, 'interviews_count': interviews_count,
                           'job_month': jobs_this_month, 'employee_month': employees_this_month,
                           'interview_month': interviews_this_month, 'employer_month': employers_this_month,
                           'job_week': jobs_this_week, 'interview_week': interviews_this_week,
                           'employee_week': employees_this_week, 'employer_week': employers_this_week,
                           'profile': staff_user})


def req_login(request):
    if request.POST:
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
        else:
            messages.error(request, 'Incorrect email or password')
            return redirect('administrator:staff_login')
    return render(request, 'administrator/staff-login.html')


def staff_logout(request):
    logout(request)
    return redirect('administrator:staff_login')
