import os
import re

import requests
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from djoser.conf import django_settings

from administrator.models import Employment, Payroll, PayrollHistory, AdminNote, JobLogs, AdminLog
from administrator.permissions import can_view
from administrator.serializers import StaffSerializer
from api.extractor import generate_employer_key, generate_payment_key
from api.models import Employee, Employer, JobsPost, ApplyJob, Staff, PaymentTrackRecord, Support, User
from api.views import getuser
from chat.models import DMChatMessage
from chat.serializers import DMChatChannelSerializer
from chat.views import get_channel
from interview.models import Interviews, ObjectiveInterviewAnswers, TheoryInterviewAnswers, EmploymentRequest
from interview.serializers import IEmployeeSerializer, ViewObjEmployeeInterviewSerializer, \
    ViewTheoryEmployeeInterviewSerializer, ViewObjInterviewSerializer, ViewTheoryInterviewSerializer
from interview.views import get_employee
from workaapi.settings import BASE_DIR

# Create your views here.

api_key = 'bb3c1e.98f2c0ba5b76933dd5c3e47b01bbc87c'


# def myuser_login_required(f):
#     def wrap(request, *args, **kwargs):
#         # this check the session if userid key exist, if not it will redirect to login page
#         if 'userid' not in request.session.keys():
#             return HttpResponseRedirect
#         return f(request, *args, **kwargs)
#
#     wrap.__doc__ = f.__doc__
#     wrap.__name__ = f.__name__
#     return wrap
@can_view('applicant')
def employee_list_card(request):
    if request.POST:
        param = request.POST['param']
        employees = Employee.objects.filter(
            Q(first_name__icontains=param) | Q(last_name__icontains=param) | Q(user__email__icontains=param) | Q(
                location__icontains=param) | Q(other_name__icontains=param) | Q(
                gender__icontains=param) | Q(phone__icontains=param))
        return render(request, 'administrator/employee-list-card.html',
                      context={'employees': employees, 'search': True, 'found': employees.count()})

    employees = Employee.objects.all()
    return render(request, 'administrator/employee-list-card.html',
                  context={'employees': employees})


@can_view('employer')
def employer_list_card(request):
    if request.POST:
        param = request.POST['param']
        employers = Employer.objects.filter(
            Q(first_name__icontains=param) | Q(last_name__icontains=param) | Q(user__email__icontains=param) | Q(
                location__icontains=param) | Q(company_email__icontains=param) | Q(
                company_name__icontains=param) | Q(phone__icontains=param))
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
    employee_folder = os.path.join(BASE_DIR, 'media', str(employee.uid))
    applied_jobs = employee.job_applicant.all().count()
    shortlist = employee.job_applicant.filter(status='shortlist')
    shortlists = shortlist.count()
    transactions = employee.user.payment_record.all()
    # from interview filter jobs which employee is shortlisted
    interviews = Interviews.objects.filter(job__in=shortlist.values('job')).count()
    activities = employee.user.user_logs.all()
    user_documents = []
    if os.path.isdir(employee_folder):
        for root, dirs, files in os.walk(employee_folder):
            for name in files:
                filename = os.path.join(root, name)
                filename = '/'.join(filename.split('\\')[5:])
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
                           'interviews': interviews, 'transactions': transactions,
                           'admin_notes': employee.user.admin_notes.all().order_by('-created'),
                           'activities': activities})


def employer_details(request, pid):
    employer = Employer.objects.get(uid=pid)
    posted_jobs = employer.job_employer.all()
    interviews = Interviews.objects.filter(job__employer=employer)
    employer_folder = os.path.join(BASE_DIR, 'media', str(employer.uid))
    transactions = employer.user.payment_record.all()
    employment_history = Payroll.objects.filter(job__employer=employer)
    activities = employer.user.user_logs.all()
    user_documents = []
    if os.path.isdir(employer_folder):
        for root, dirs, files in os.walk(employer_folder):
            for name in files:
                filename = os.path.join(root, name)
                filename = '/'.join(filename.split('\\')[5:])
                file_url = '{0}://{1}/{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, filename)
                if name.endswith(('jpg', '.jpeg', '.png')):
                    doc_type = 'image'
                elif name.endswith('.pdf'):
                    doc_type = 'pdf'
                else:
                    doc_type = 'doc'
                file = {'url': file_url, 'name': name, 'type': doc_type}
                user_documents.append(file)
    return render(request, 'administrator/employer-details.html',
                  context={'employer': employer, 'posted_jobs': posted_jobs, 'interviews': interviews,
                           'documents': user_documents, 'transactions': transactions,
                           'employment_history': employment_history,
                           'admin_notes': employer.user.admin_notes.all().order_by('-created'),
                           'activities': activities})


@can_view('jobs')
def job_listing(request, status=''):
    if status == 'open':
        jobs = JobsPost.objects.filter(access='open')
    elif status == 'closed':
        jobs = JobsPost.objects.filter(access='closed')
    elif status == 'blocked':
        jobs = JobsPost.objects.filter(access='pending')
    else:
        jobs = JobsPost.objects.all()

    if request.POST:
        param = request.POST['param']
        jobs = JobsPost.objects.filter(
            Q(employer__company_name__icontains=param) | Q(title__icontains=param) | Q(
                description__icontains=param) | Q(
                qualification__icontains=param) | Q(requirement__icontains=param) | Q(
                categories__icontains=param) | Q(tags__icontains=param) | Q(job_type__iexact=param) | Q(
                budget__icontains=param) | Q(currency__iexact=param) | Q(location__icontains=param))
        return render(request, 'administrator/job-card-list.html', context={'jobs': jobs, 'status': 'result matched'})
    return render(request, 'administrator/job-card-list.html', context={'jobs': jobs, 'status': status})


def job_details(request, job_key):
    job = JobsPost.objects.get(job_key=job_key)
    requirements = job.requirement.splitlines()
    qualifications = job.qualification.splitlines()
    benefits = job.benefit.splitlines()
    return render(request, 'administrator/job-details.html',
                  context={'requirements': requirements, 'qualifications': qualifications, 'benefits': benefits,
                           'job': job})


@can_view('jobs')
def job_applications(request, job_key):
    applications = ApplyJob.objects.filter(job__job_key=job_key)
    return render(request, 'administrator/job-applications.html', context={'applications': applications})


@can_view('interview')
def interview_list(request):
    interviews = Interviews.objects.all()
    return render(request, 'administrator/interview-list.html', context={'interviews': interviews})


@can_view('interview')
def interview_submissions(request, uid):
    interview = Interviews.objects.get(interview_uid=uid)
    if interview.interview_type == 'objective':
        submitted = [get_employee(e['employee']) for e in
                     ObjectiveInterviewAnswers.objects.filter(interview=interview).values('employee').distinct()]

        serializer = IEmployeeSerializer(submitted, many=True)
    elif interview.interview_type == 'theory':
        submitted = [get_employee(e['employee']) for e in
                     TheoryInterviewAnswers.objects.filter(interview=interview).values('employee').distinct()]
        serializer = IEmployeeSerializer(submitted, many=True)

    return render(request, 'administrator/interview-submission-list.html',
                  context={'submitted': serializer.data, 'interview': interview})


@can_view('interview')
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


def add_super_staff(request):
    if request.POST:
        serializer = StaffSerializer(data=request.POST)
        payload = {'email': request.POST['email'], 'password': request.POST['password'],
                   're_password': request.POST['confirm_password'],
                   'account_type': 'administrator'}
        url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-list'))
        if serializer.is_valid():
            response = requests.post(url, data=payload)
            if response.status_code == 201:
                roles = 'employer,applicant,interview,employment,payroll,support,jobs,staffs'
                # print("{0} {1} {0}".format('hello', userid))
                serializer.save(user=getuser(response.json().get('id')), uid=generate_employer_key(), roles=roles)
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
    job_activities = JobLogs.objects.all()
    admin_activities = AdminLog.objects.all()
    return render(request, 'administrator/dashboard.html',
                  context={'job_count': jobs_count, 'employees_count': employees_count,
                           'employers_count': employers_count, 'interviews_count': interviews_count,
                           'job_month': jobs_this_month, 'employee_month': employees_this_month,
                           'interview_month': interviews_this_month, 'employer_month': employers_this_month,
                           'job_week': jobs_this_week, 'interview_week': interviews_this_week,
                           'employee_week': employees_this_week, 'employer_week': employers_this_week,
                           'job_logs': job_activities, 'admin_logs': admin_activities})


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


@can_view('jobs')
def approve_job(request, job_id):
    job = JobsPost.objects.get(job_key=job_id)
    job.availability = 'available'
    job.access = 'open'
    job.validity = True
    job.refusal_note = request.POST['note']
    job.refusal_date = timezone.now()
    job.save()
    messages.success(request, 'Job successfully be Approved')
    return redirect('administrator:job_details', job_key=job_id)


@can_view('jobs')
def decline_job(request, job_id):
    job = JobsPost.objects.get(job_key=job_id)
    job.access = 'pending'
    job.availability = 'hide'
    job.validity = False
    job.refusal_note = request.POST['note']
    job.refusal_date = timezone.now()
    job.save()
    messages.success(request, 'Job successfully be declined')
    return redirect('administrator:job_details', job_key=job_id)


@can_view('interview')
def suspend_interview(request, iid):
    if request.POST:
        interview = Interviews.objects.get(interview_uid=iid)
        interview.status = 'suspended'
        interview.refusal_note = request.POST['note']
        interview.refusal_date = timezone.now()
        interview.save()
        messages.success(request, 'Interview Successfully Suspended')
        return redirect('administrator:interviews')


def download_pdf(request):
    response = requests.post(
        'https://api.restpdf.io/v1/pdf',
        headers={
            'X-API-KEY': api_key,
            'content-type': 'application/json'
        },
        json={
            "output": "data",
            "url": "http://www.designstub.com/demos/onepageresume/"
        }
    )

    if response.status_code == 200:
        with open(os.path.join(BASE_DIR, 'gogle.pdf'), 'wb') as file:
            file.write(response.content)
            print('done')
    else:
        print("There was an error converting the PDF")


def preview_cv(request, pid):
    employee = Employee.objects.get(uid=pid)
    return render(request, 'administrator/cv-preview.html', context={'applicant': employee})


@can_view('support')
def support_messages(request):
    all_messages = Support.objects.all()
    active_messages = all_messages.filter(status='open')
    closed = all_messages.filter(status='closed')
    return render(request, 'administrator/support-message.html',
                  context={'all': all_messages, 'actives': active_messages, 'closed': closed})


def read_support_messages(request, mid):
    the_message = Support.objects.get(pk=mid)
    try:
        sender = User.objects.get(email=the_message.email)
        reg_sender = True
    except:
        sender = the_message.email
        reg_sender = False
    all_messages = Support.objects.all()
    active_messages = all_messages.filter(status='open')
    closed = all_messages.filter(status='closed')
    return render(request, 'administrator/read-support-message.html',
                  context={'all': all_messages, 'actives': active_messages, 'closed': closed, 'tsm': the_message,
                           'sender': sender, 'reg_sender': reg_sender})


@can_view('employment')
def employment_form(request):
    return render(request, 'administrator/employment-form.html')


@can_view('employment')
def employment_requests(request):
    emplement_req = EmploymentRequest.objects.all()
    return render(request, 'administrator/employment-requests.html', context={'employment_list': emplement_req})


@can_view('employment')
def process_employment(request, req_id):
    req = EmploymentRequest.objects.get(pk=req_id)
    if req.mode == 'interview':
        intr = Interviews.objects.get(interview_uid=req.mode_key)
        job = intr.job
    else:
        job = JobsPost.objects.get(job_key=req.mode_key)
    if request.POST:
        currency = request.POST['currency']
        salary = request.POST['salary']
        resumption = request.POST['resumption']
        employees = ','.join(request.POST.getlist('employees'))
        Employment.objects.create(req=req, job=job, currency=currency, salary=int(salary), resumption=resumption,
                                  employees_email=employees)
        req.status = 'processed'
        req.save()
        messages.success(request, 'Employment Sucessfully Created!')
        return redirect('administrator:employments')
    return render(request, 'administrator/employment-form.html', context={'req': req, 'job': job, })


@can_view('employment')
def employments(request):
    return render(request, 'administrator/employments.html', context={'items': Employment.objects.all()})


@can_view('payroll')
def process_payroll(request, req_id):
    item = Employment.objects.get(pk=req_id)
    return render(request, 'administrator/payroll.html', context={'item': item})


@can_view('payroll')
def create_payroll(request, job_id, uid):
    if request.POST:
        job = JobsPost.objects.get(job_key=job_id)
        employee = Employee.objects.get(uid=uid)
        salary = request.POST['salary']
        payment = request.POST['charges']
        resumption = request.POST['resumption_date']
        currency = request.POST['currency']
        monthly_charge = request.POST['monthly_charge']
        try:
            Payroll.objects.create(job=job, employee=employee, salary=salary, currency=currency, resumption=resumption,
                                   payment_key=generate_payment_key(), monthly_charge=monthly_charge, payment=payment)
            return JsonResponse({'result': 'successful'})
        except:
            return JsonResponse({'result': 'error'}, status=400)


@can_view('payroll')
def payroll_list(request):
    items = Payroll.objects.all()
    return render(request, 'administrator/payroll-list.html', context={'items': items})


def re_int(num):
    return int(re.sub("[^\d\.]", "", num))


@can_view('payroll')
@can_view('finance')
def make_payroll_payment(request, pay_id):
    item = Payroll.objects.get(payment_key=pay_id)
    if request.POST:
        amount = request.POST['amount']
        narration = request.POST['narration']
        item.balance += re_int(amount)
        item.save()
        PaymentTrackRecord.objects.create(payer=item.employee.user, payer_account=request.user.email,
                                          transaction=narration,
                                          narration='payroll payment for {}'.format(item.payment_key),
                                          status='confirmed')
        PayrollHistory.objects.create(payroll=item, amount=re_int(amount), balance=item.balance,
                                      payer=Staff.objects.get(user=request.user), transaction=narration)
        messages.success(request, 'payment Added successfully')
        return redirect('administrator:payrolls')
    return render(request, 'administrator/make-payroll-payment.html', context={'item': item})


@can_view('payroll')
def payroll_payments(request, pay_id):
    items = PayrollHistory.objects.filter(payroll__payment_key=pay_id)
    return render(request, 'administrator/payroll-history.html', context={'items': items})


@can_view('staff')
def staff_list(request):
    staffs = Staff.objects.filter(user__account_type='staff')
    return render(request, 'administrator/staff-list.html', context={'items': staffs})


@can_view('staff')
def update_staff(request, uid):
    staff = Staff.objects.get(pk=uid)
    if request.POST:
        access = request.POST['access']
        roles = request.POST.getlist('roles')
        if access == 'active':
            staff.user.is_active = True
        else:
            staff.user.is_active = False
        staff.user.save()
        staff.roles = ','.join(roles)
        staff.save()
        messages.success(request, '{} profiles is updated successfully'.format(staff.fullname))
        return redirect('administrator:staff_list')
    return render(request, 'administrator/update-staff.html', context={'item': staff})


def access_denied(request):
    return render(request, 'administrator/access-denied.html')


@can_view('support')
def toggle_support_message(request, mid):
    message = Support.objects.get(pk=mid)
    if message.status == 'closed':
        message.status = 'open'
    else:
        message.status = 'closed'
    message.save()
    print('closed')
    return JsonResponse({'result': 'closed'})


@can_view('report')
def report(request):
    if request.POST:
        dated_from = request.POST['from']
        dated_to = request.POST['to']
        jobs = JobsPost.objects.filter(created__date__gte=dated_from, created__date__lte=dated_to).count()
        applications = ApplyJob.objects.filter(created__date__gte=dated_from, created__date__lte=dated_to).count()
        employed_jobs = Employment.objects.filter(created__date__gte=dated_from, created__date__lte=dated_to).count()
        applicants = Employee.objects.filter(created__date__gte=dated_from, created__date__lte=dated_to).count()
        employers = Employer.objects.filter(created__date__gte=dated_from, created__date__lte=dated_to).count()
        employment_request = EmploymentRequest.objects.filter(created__date__gte=dated_from,
                                                              created__date__lte=dated_to).count()
        supports = Support.objects.filter(created__date__gte=dated_from, created__date__lte=dated_to).count()
        payroll = Payroll.objects.filter(created__date__gte=dated_from, created__date__lte=dated_to).count()
        interview = Interviews.objects.filter(created__date__gte=dated_from, created__date__lte=dated_to).count()

        return render(request, 'administrator/report-details.html',
                      context={'dated_from': dated_from, 'dated_to': dated_to, 'jobs': jobs,
                               'applications': applications, 'applicants': applicants, 'employments': employed_jobs,
                               'employers': employers, 'employment_requests': employment_request, 'supports': supports,
                               'employed': payroll, 'interviews': interview})
    return render(request, 'administrator/report.html')


@can_view('report')
def print_report(request, start_date, end_date):
    jobs = JobsPost.objects.filter(created__date__gte=start_date, created__date__lte=end_date).count()
    applications = ApplyJob.objects.filter(created__date__gte=start_date, created__date__lte=end_date).count()
    employed_jobs = Employment.objects.filter(created__date__gte=start_date, created__date__lte=end_date).count()
    applicants = Employee.objects.filter(created__date__gte=start_date, created__date__lte=end_date).count()
    employers = Employer.objects.filter(created__date__gte=start_date, created__date__lte=end_date).count()
    employment_request = EmploymentRequest.objects.filter(created__date__gte=start_date,
                                                          created__date__lte=end_date).count()
    supports = Support.objects.filter(created__date__gte=start_date, created__date__lte=end_date).count()
    payroll = Payroll.objects.filter(created__date__gte=start_date, created__date__lte=end_date).count()
    interview = Interviews.objects.filter(created__date__gte=start_date, created__date__lte=end_date).count()
    return render(request, 'administrator/report-print.html',
                  context={'dated_from': start_date, 'dated_to': end_date, 'jobs': jobs,
                           'applications': applications, 'applicants': applicants, 'employments': employed_jobs,
                           'employers': employers, 'employment_requests': employment_request, 'supports': supports,
                           'employed': payroll, 'interviews': interview})


@can_view('job')
def suspend_application(request, aid):
    if request.POST:
        application = ApplyJob.objects.get(pk=aid)
        note = request.POST['note']
        application.status = 'suspended'
        application.note = note
        application.save()
        messages.success(request, 'Application successful Suspended')
        return redirect('administrator:job_applications', job_key=application.job.job_key)


@can_view('job')
def approve_application(request, aid):
    if request.POST:
        application = ApplyJob.objects.get(pk=aid)
        note = request.POST['note']
        application.status = 'processing'
        application.note = note
        application.save()
        messages.success(request, 'Application successful Approved')
        return redirect('administrator:job_applications', job_key=application.job.job_key)


@can_view('interview')
def approve_interview(request, iid):
    if request.POST:
        interview = Interviews.objects.get(interview_uid=iid)
        interview.status = 'open'
        interview.refusal_note = request.POST['note']
        interview.refusal_date = timezone.now()
        interview.save()
        messages.success(request, 'Interview Successfully Approved')
        return redirect('administrator:interviews')


@can_view('interview')
def delete_answers(request, iid, uid):
    interview = Interviews.objects.get(interview_uid=iid)
    if interview.interview_type == 'objective':
        ObjectiveInterviewAnswers.objects.filter(interview=interview, employee__uid=uid).delete()
    else:
        TheoryInterviewAnswers.objects.filter(interview=interview, employee__uid=uid).delete()
    interview.submission -= 1
    interview.save()
    messages.success(request, 'Answers Successfully Deleted')
    return redirect('administrator:interview_submitted', uid=iid)


def suspend_user(request, uid):
    user = User.objects.get(pk=uid)
    user.is_active = False
    note = request.POST['note']
    user.save()
    messages.success(request, 'Users account has been successfully Suspended')
    if user.account_type == 'employee':
        return redirect('administrator:employee_list')
    else:
        return redirect('administrator:employer_list')


def approve_user(request, uid):
    user = User.objects.get(pk=uid)
    user.is_active = True
    note = request.POST['note']
    user.save()
    messages.success(request, 'Users account has been successfully Approved')
    if user.account_type == 'employee':
        return redirect('administrator:employee_list')
    else:
        return redirect('administrator:employer_list')


@can_view('employment')
def employment_update(request, uid):
    employment = Employment.objects.get(pk=uid)
    applicants = employment.job.apply_job.all()
    if request.POST:
        employment.status = request.POST['status']
        employment.salary = request.POST['salary']
        employment.currency = request.POST['currency']
        employment.resumption = request.POST['resumption']
        employment.employees = ','.join(request.POST.getlist('employees'))
        employment.save()
        messages.success(request, 'Employment successfully updated')
        messages.info(request, 'Re-process employment to create payroll, if changes in employee')
        return redirect('administrator:employments')
    return render(request, 'administrator/employment-update.html',
                  context={'item': employment, 'applicants': applicants})


@can_view('payroll')
@can_view('finance')
def update_payroll(request, pid):
    payroll = Payroll.objects.get(payment_key=pid)
    if request.POST:
        payroll.salary = re_int(request.POST['salary'])
        payroll.payment = re_int(request.POST['charges'])
        payroll.resumption = request.POST['resumption']
        payroll.currency = request.POST['currency']
        payroll.monthly_charge = re_int(request.POST['monthly_charge'])
        payroll.job_status = request.POST['job_status']
        payroll.payment_status = request.POST['payment_status']
        payroll.save()
        messages.success(request, '{} payroll successfully updated'.format(payroll.employee.fullname))
        return redirect('administrator:payrolls')
    return render(request, 'administrator/payroll-update.html', context={'item': payroll})


def add_note(request, uid):
    if request.POST:
        user = User.objects.get(pk=uid)
        AdminNote.objects.create(user=user, note=request.POST['note'],
                                 writer=Staff.objects.get(user=request.user))
        messages.success(request, 'Note Added Successfully')
        if user.account_type == 'employee':
            return redirect('administrator:employee_details', pid=Employee.objects.get(user=user).uid)
        else:
            return redirect('administrator:employer_details', pid=Employer.objects.get(user=user).uid)


def delete_note(request, account, nid, uid):
    AdminNote.objects.get(pk=nid).delete()
    messages.success(request, 'Note Successfully Deleted')
    if account == 'employee':
        return redirect('administrator:employee_details', pid=uid)
    else:
        return redirect('administrator:employer_details', pid=uid)


@can_view('payroll')
def payroll_histories(request):
    items = PayrollHistory.objects.all()
    return render(request, 'administrator/payroll-histories.html', context={'items': items})
