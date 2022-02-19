import datetime

import requests
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from djoser import utils
from djoser.conf import django_settings
from djoser.conf import settings
from djoser.views import TokenCreateView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.extractor import extract_keywords, generate_job_key, generate_employer_key, generate_employee_key
from api.location import Place
from api.members import positions, Industries, RelativeJobTags
from api.models import Skills, User, WorkExperience, Education, Language, Availability, Employee, ApplyJob, JobsPost, \
    Employer, LikedJobs
from api.permissions import IsEmployer, IsEmployee
from api.serializers import SkillsSerializer, WESerializer, EmployeeProfileSerializer, EducationSerializer, \
    LanguageSerializer, AvailabilitySerializer, EmployeeSerializer, EmployerSerializer, JobsPostSerializer, \
    JobViewSerializer, JobApplicantSerializer, ApplyJobSerializer, PositionSerializer, IndustriesSerializer, \
    JobApplicantListSerializer, FetchJobSerializer, RelativeJobTagSerializer, JobsPostListSerializer, \
    EmployeeDetailsSerializer
from automator.views import DefaultEmployeeSettings, DefaultEmployerSettings
from chat.views import CreateMessageChannel
from interview.models import Interviews, EmploymentRequest
from interview.serializers import ListInterviewSerializer
from notifier.models import HotEmployeeAlert, UserNotificationSettings
from notifier.serializers import EmployeeNotificationSerializer, EmployerNotificationSerializer, \
    HotEmployeeAlertSerializer, UserNotificationSettingsSerializer
from notifier.views import EmailNotifier, jobapplynotifier, employee_notifications, employer_notifications, \
    jobappliednotifier


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'auth_token': token.key,
            'user_type': user.account_type
        })


class CustomLogin(TokenCreateView):
    def _action(self, serializer):
        already_login = False
        if serializer.user.last_login:
            already_login = True
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        if serializer.user.account_type == 'employee':
            employee = Employee.objects.get(user=serializer.user)
            Firstname = employee.first_name
            Lastname = employee.last_name
            Dp = employee.display_picture
            if already_login:
                print('already login')
            else:
                print('first time')
                DefaultEmployeeSettings(employee.uid)
        elif serializer.user.account_type == 'employer':
            employer = Employer.objects.get(user=serializer.user)
            Firstname = employer.first_name
            Lastname = employer.last_name
            Dp = employer.company_logo
            if already_login:
                print('already login')
            else:
                print('first time')
                DefaultEmployerSettings(employer.uid)
        return Response(
            data=dict(token_serializer_class(token).data, user=serializer.user.account_type, firstname=Firstname,
                      lastname=Lastname, dp=Dp), status=status.HTTP_200_OK
        )


@api_view(['GET'])
def index(request):
    message = 'Server is live now'
    return Response(message, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkauth(request):
    if request.user.is_active:
        message = 'you are activated'
    else:
        message = 'not yet activated'
    return Response(message, status=status.HTTP_200_OK)


class ActivateUser(GenericAPIView):

    def get(self, request, uid, token, format=None):
        payload = {'uid': uid, 'token': token}
        url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-activation'))
        response = requests.post(url, data=payload)
        if response.status_code == 204:
            print(self.request.user)
            print(request.user)
            return redirect(reverse('utility:emailsuccess'))
        else:
            return Response(response.json())


@api_view(['GET', 'POST'])
def reset_password(request, uid, token):
    if request.POST:
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        payload = {'uid': uid, 'token': token, 'new_password': password, 're_new_password': confirm_password}
        url = "https://worka.pythonanywhere.com/users/reset_password_confirm/"
        response = requests.post(url, data=payload)
        print(response)
        if response.status_code == 204:
            return Response({}, response.status_code)
        else:
            return Response(response.json())
    return render(request, 'workaapi/password_reset_page.html', context={'uid': uid, 'token': token})


# work experience crud

@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def add_work_experience(request):
    serializer = WESerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=get_employee(request))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def view_work_experiences(request):
    work_experience = WorkExperience.objects.filter(user=get_employee(request))
    serializer = WESerializer(work_experience, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def work_experience_details(request, pk):
    if request.method == 'POST':
        work_exp = WorkExperience.objects.get(pk=pk)
        serializer = WESerializer(work_exp, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        try:
            work_exp = WorkExperience.objects.get(pk=pk)
            serializer = WESerializer(work_exp, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except WorkExperience.DoesNotExist:
            return Response('There is no record of work Experience', status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            work_exp = WorkExperience.objects.get(pk=pk)
            work_exp.delete()
            return Response('deleted', status=status.HTTP_200_OK)
        except WorkExperience.DoesNotExist:
            return Response('There is no record of work Experience', status.HTTP_400_BAD_REQUEST)


# skill crud

@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def add_skill(request):
    serializer = SkillsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=get_employee(request))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def view_skills(request):
    skill = Skills.objects.filter(user=get_employee(request))
    serializer = SkillsSerializer(skill, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def skill_details(request, pk):
    if request.method == 'POST':
        skill = Skills.objects.get(pk=pk)
        serializer = SkillsSerializer(skill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        try:
            skill = Skills.objects.get(pk=pk)
            serializer = SkillsSerializer(skill, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Skills.DoesNotExist:
            return Response('There is no record of skill', status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            skill = Skills.objects.get(pk=pk)
            skill.delete()
            return Response({'message': 'deleted'}, status=status.HTTP_200_OK)
        except WorkExperience.DoesNotExist:
            return Response({'message': 'There is no record of skill'}, status.HTTP_400_BAD_REQUEST)


# skill crud

@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def add_education(request):
    serializer = EducationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=get_employee(request))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def view_educations(request):
    education = Education.objects.filter(user=get_employee(request))
    serializer = EducationSerializer(education, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def education_details(request, pk):
    if request.method == 'POST':
        education = Education.objects.get(pk=pk)
        serializer = EducationSerializer(education, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        try:
            education = Education.objects.get(pk=pk)
            serializer = EducationSerializer(education, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Education.DoesNotExist:
            return Response({'message': 'There is no record of education'}, status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            education = Education.objects.get(pk=pk)
            education.delete()
            return Response({'message': 'deleted'}, status=status.HTTP_200_OK)
        except WorkExperience.DoesNotExist:
            return Response({'message': 'There is no record of education'}, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def view_employeeprofile(request):
    user = User.objects.get(pk=request.user.id)
    serializer = EmployeeProfileSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def add_language(request):
    serializer = LanguageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=get_employee(request))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def language_details(request, pk):
    if request.method == 'POST':
        language = Language.objects.get(pk=pk)
        serializer = LanguageSerializer(language, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        try:
            language = Language.objects.get(pk=pk)
            serializer = LanguageSerializer(language, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Language.DoesNotExist:
            return Response('There is no record of language', status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            language = Language.objects.get(pk=pk)
            language.delete()
            return Response('deleted', status=status.HTTP_200_OK)
        except Language.DoesNotExist:
            return Response('There is no record of language', status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def view_languages(request):
    language = Language.objects.filter(user=get_employee(request))
    serializer = LanguageSerializer(language, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def add_availability(request):
    serializer = AvailabilitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=get_employee(request))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def availability_details(request, pk):
    if request.method == 'POST':
        availability = Availability.objects.get(pk=pk)
        serializer = AvailabilitySerializer(availability, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        try:
            availability = Availability.objects.get(pk=pk)
            serializer = AvailabilitySerializer(availability, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Availability.DoesNotExist:
            return Response('There is no record of availability', status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            availability = Availability.objects.get(pk=pk)
            availability.delete()
            return Response('deleted', status=status.HTTP_200_OK)
        except Availability.DoesNotExist:
            return Response('There is no record of availability', status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def view_availabilitys(request):
    availability = Availability.objects.filter(user=get_employee(request))
    serializer = AvailabilitySerializer(availability, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def getuser(pk):
    user = User.objects.get(pk=pk)
    return user


@api_view(['POST'])
def add_employee(request):
    serializer = EmployeeSerializer(data=request.data)
    payload = {'email': request.data['email'], 'password': request.data['password'],
               're_password': request.data['re_password'],
               'account_type': 'employee'}

    url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-list'))
    response = requests.post(url, data=payload)
    if serializer.is_valid():
        print(response.status_code)
        if response.status_code == 201:
            serializer.save(user=getuser(response.json().get('id')), uid=generate_employee_key())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(response.json())
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_employer(request):
    serializer = EmployerSerializer(data=request.data)
    payload = {'email': request.data['email'], 'password': request.data['password'],
               're_password': request.data['re_password'],
               'account_type': 'employer'}
    url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-list'))
    print('stage one completed')
    if serializer.is_valid():
        print('stage two uncompleted')
        response = requests.post(url, data=payload)
        if response.status_code == 201:
            print('stage 3 completed')
            print(response.status_code)
            # print("{0} {1} {0}".format('hello', userid))
            serializer.save(user=getuser(response.json().get('id')), uid=generate_employer_key())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print('stage 3 uncompleted')
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
    else:
        print('stage two uncompleted')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def employee_details(request):
    employee = Employee.objects.get(user=request.user)
    if request.method == 'POST':
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        try:
            serializer = EmployeeSerializer(employee, many=False)
            return Response(dict(serializer.data, email=request.user.email), status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response('There is no record of employee', status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            employee.delete()
            return Response('deleted', status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response('There is no record of employee', status.HTTP_400_BAD_REQUEST)


def get_employer(request):
    return Employer.objects.get(user=request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def post_job(request):
    serializer = JobsPostSerializer(data=request.data)
    employer = get_employer(request)
    if serializer.is_valid():
        serializer.save(employer=employer, job_key=generate_job_key(),
                        employer_logo=employer.company_logo)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_tag(request):
    data = request.POST
    text_content = data['content']
    keywords = extract_keywords(sequence=text_content)
    found = len(keywords)
    return JsonResponse({'found': found, 'keywords': keywords})


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def display_picture(request):
    employee = Employee.objects.get(user=request.user)
    if request.method == 'POST' and request.FILES:
        picture = request.FILES['display_picture']
        fss = FileSystemStorage(location='staticfiles/media/display-picture/{}'.format(request.user.id))
        file = fss.save(picture.name, picture)
        employee.display_picture = '{0}://{1}/{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN,
                                                          '{}/{}'.format(fss.base_location, picture.name).replace(
                                                              'staticfiles', 'static'))
        try:
            employee.save()
            return JsonResponse({'response': '{}'.format(employee.display_picture)})
        except:
            return JsonResponse({'response': 'cannot upload'})

    elif request.method == 'GET':
        return JsonResponse({'response': employee.display_picture})


def get_employee(request):
    return Employee.objects.get(user=request.user)

def get_job(jobid):
    return JobsPost.objects.get(job_key=jobid)


def get_employee_by_id(id):
    return Employee.objects.get(uid=id)


def get_user_by_id(id):
    return User.objects.get(pk=id)


# apply for job
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployee])
def apply_job(request):
    jobid = request.data['jobid'];
    job = JobsPost.objects.get(job_key=jobid)
    employee = get_employee(request)
    if job.availability == 'available':
        applicable = True
    else:
        return Response('sorry, the job is no more available, try another', status=status.HTTP_400_BAD_REQUEST)
    if job.expiry:
        if datetime.date.today() > job.expiry:
            applicable = False
            return Response('sorry, this job is closed', status=status.HTTP_400_BAD_REQUEST)
        else:
            applicable = True
    if applicable:
        try:
            ApplyJob.objects.get(job=job, applicant=employee)
            return Response('you have already applied for this job', status=status.HTTP_406_NOT_ACCEPTABLE)
        except ApplyJob.DoesNotExist:
            ApplyJob.objects.create(job=job, applicant=employee)
            job.applications += 1
            job.save()
            jobapplynotifier(employee, job.title, job.employer.company_name)
            jobappliednotifier(job.employer, employee.fullname, job.title)
            return Response('successfully applied', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_job(request, jobid):
    try:
        job = get_job(jobid)
        serializer = JobViewSerializer(job, many=False)
        try:
            ApplyJob.objects.get(job=job, applicant=get_employee(request))
            is_applied = True
        except ApplyJob.DoesNotExist:
            is_applied = False
        return Response({'job_data': serializer.data, 'applied': is_applied}, status=status.HTTP_200_OK)
    except job.DoesNotExist:
        return Response('job not found', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def job_application_view(request, uid):
    try:
        applicant = Employee.objects.get(uid=uid)
        serializer = JobApplicantSerializer(applicant, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ApplyJob.DoesNotExist:
        return Response('cannot view profile', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def job_application_list(request, jobid):
    try:
        applications = ApplyJob.objects.filter(job=get_job(jobid))
        serializer = JobApplicantListSerializer([x.applicant for x in applications], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ApplyJob.DoesNotExist:
        return Response('job not found')


@api_view(['POST'])
def change_password(request):
    new_password = request.POST['new_password']
    re_newpassword = request.POST['re_newpassword']
    current_password = request.POST['current_password']
    payload = {'new_password': new_password, 're_newpassword': re_newpassword, 'current_password': current_password}
    url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-set-password'))
    response = requests.post(url, data=payload, headers=request.headers)
    if response.status_code == 204:
        print(request.user.email)
        EmailNotifier(request.user.email).password_changed()
        return Response({"successful"}, status=status.HTTP_200_OK)
    else:
        return Response(response.json())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_job(request):
    my_job = ApplyJob.objects.filter(applicant=get_employee(request))
    serializer = ApplyJobSerializer(my_job, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class PositionClass:
    def __init__(self, position):
        self.position = position


@api_view(['GET'])
def get_positions(request):
    _positions = [PositionClass(position) for position in positions]
    serializer = PositionSerializer(_positions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class IndustryClass:
    def __init__(self, industry):
        self.industry = industry


@api_view(['GET'])
def get_industries(request):
    _industries = [IndustryClass(industry) for industry in Industries]
    serializer = IndustriesSerializer(_industries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def get_posted_jobs(request):
    jobs = JobsPost.objects.filter(employer=get_employer(request))
    serializer = JobsPostListSerializer(jobs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def create_shortlist(request, jobid):
    short = request.POST['shortlist_id']
    shortlist = short.split(',')
    job = get_job(jobid)
    if job.employer == get_employer(request):
        applicant = [get_employee_by_id(x) for x in shortlist]
        ApplyJob.objects.filter(job=job, applicant__in=applicant).update(status='shortlist')
        ApplyJob.objects.exclude(job=job, applicant__in=applicant).update(status='decline')
        msg_channel = CreateMessageChannel(request, group=shortlist, name=job.employer.company_name)
        msg_channel.push_shortlist_message()
        job.message_channel = msg_channel.chat_uid
        job.availability = 'hide'
        job.access = 'closed'
        job.save()
        return Response('shortlist created successfully', status=status.HTTP_200_OK)
    else:
        return Response('cannot shortlist', status=status.HTTP_400_BAD_REQUEST)


r = '09098051994'


# @api_view(['GET'])
# def fetch_jobs(request):
#     jobs = JobsPost.objects.all()
#     serializer = FetchJobSerializer(jobs, many=True)
#     new_serializer=[]
#     for serial in serializer.data:
#         serial['is_like']=True
#         new_serializer.append(serial)
#         print(serial)
#     print(new_serializer)
#     return Response(new_serializer, status=status.HTTP_200_OK)


class RelativeTagClass:
    def __init__(self, tag):
        self.tag = tag


@api_view(['GET'])
def get_relative_job_tags(request):
    _tags = [RelativeTagClass(tag) for tag in RelativeJobTags]
    serializer = RelativeJobTagSerializer(_tags, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def company_logo(request):
    employer = Employer.objects.get(user=request.user)
    if request.method == 'POST' and request.FILES:
        picture = request.FILES['company_logo']
        fss = FileSystemStorage(location='media/company-logo/{}'.format(employer.uid))
        file = fss.save(picture.name, picture)
        filename = '{}/{}'.format(fss.base_location, picture.name)
        employer.company_logo = '{0}://{1}/{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, filename)
        try:
            employer.save()
            response = "successful"
        except:
            response = 'cannot upload'
        return Response(response, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        pic = employer.company_logo
        if pic is None:
            response = 'not available'
        else:
            response = pic
        return Response(response, status=status.HTTP_200_OK)


# def get_location(request):
#     g = GeoIP2()
#     f = g.city()
#     print(f)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    if request.user.account_type == 'employee':
        notice = employee_notifications(get_employee(request))
        serializer = EmployeeNotificationSerializer(notice, many=True)
    elif request.user.account_type == 'employer':
        notice = employer_notifications(get_employer(request))
        serializer = EmployerNotificationSerializer(notice, many=True)
    else:
        notice = employee_notifications(get_employee(request))
        serializer = EmployeeNotificationSerializer(notice, many=True)
    print('account type')
    print(request.user.account_type)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def search_jobs(request):
    param = request.data['param']
    job = JobsPost.objects.filter(
        Q(title__contains=param) | Q(description__contains=param) | Q(job_type__contains=param) | Q(
            location__contains=param) | Q(employer__company_name__contains=param))
    serializer = FetchJobSerializer(job, many=True)
    print('found')
    if serializer.data:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        job = JobsPost.objects.all()
        serializer = FetchJobSerializer(job, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def cv_preview(request):
    profile = Employee.objects.get(user=request.user)
    serializer = JobApplicantSerializer(profile, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsEmployee])
def profile_preview(request):
    if request.method == 'GET':
        profile = Employee.objects.get(user=request.user)
        serializer = EmployeeProfileSerializer(profile, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if requests.method == 'POST':
        profile = Employee.objects.get(user=request.user)
        serializer = EmployeeProfileSerializer(profile, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_details(request):
    if request.user.account_type == 'employee':
        profile = Employee.objects.get(user=request.user)
        serializer = EmployeeDetailsSerializer(profile, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nearest_job(request):
    if request.user.account_type == 'employee':
        user_location = get_employee(request).location
    elif request.user.account_type == 'employer':
        user_location = get_employer(request).location
    nearest = Place(user_location).get_nearby_city()
    nearest_city = [each['name'] for each in nearest['geonames']]
    joblist = []
    jobs = JobsPost.objects.filter(availability='available', access='open')
    for search_term in nearest_city:
        jobs = jobs.filter(location__icontains=search_term)
        joblist.extend(jobs)
    serializer = FetchJobSerializer(joblist, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_my_interview(request):
    shortlistedjobs = ApplyJob.objects.filter(applicant=get_employee(request), status='shortlist')
    interviewlist = []
    for each in shortlistedjobs:
        try:
            jobinterview = Interviews.objects.filter(job=each.job).order_by('-created')
            interviewlist.extend(jobinterview)
        except:
            pass
    serializer = ListInterviewSerializer(interviewlist, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_hot_alert(request):
    hot_note = HotEmployeeAlert.objects.filter(employee=get_employee(request))
    serializer = HotEmployeeAlertSerializer(hot_note, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, IsEmployer])
def employer_details(request):
    employer = Employer.objects.get(user=request.user)
    if request.method == 'POST':
        serializer = EmployerSerializer(employer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        serializer = EmployerSerializer(employer, many=False)
        return Response(dict(serializer.data, email=request.user.email), status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        try:
            employer.delete()
            return Response('deleted', status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response('There is no record of employee', status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def like_job(request, jobid):
    job = get_job(jobid)
    LikedJobs.objects.create(job=job, liker=get_employee(request))
    return Response('liked', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def dislike_job(request, jobid):
    job = get_job(jobid)
    likejob = LikedJobs.objects.get(job=job, liker=get_employee(request))
    if likejob:
        likejob.delete()
        return Response('deleted', status=status.HTTP_200_OK)
    else:
        return Response('deleted', status=status.HTTP_200_OK)


def check_like(request, jobid):
    try:
        LikedJobs.objects.get(job__job_key=jobid, liker=get_employee(request))
        return True
    except:
        return False


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def fetch_jobs(request):
    jobs = JobsPost.objects.filter(availability='available', access='open')
    serializer = FetchJobSerializer(jobs, many=True)
    new_serializer = []
    for serial in serializer.data:
        if check_like(request, serial['job_key']):
            serial['is_like'] = True
        else:
            serial['is_like'] = False
        new_serializer.append(serial)
    return Response(new_serializer, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployee])
def filter_jobs(request):
    job_type = request.data['job_type']
    category = request.data['category']
    experience = request.data['experience']
    budget_start = request.data['budget_start']
    budget_end = request.data['budget_end']
    location = request.data['location']
    job = JobsPost.objects.filter(
        Q(description__contains=experience) | Q(categories__in=category) | Q(job_type__in=job_type) | Q(
            location__contains=location) | Q(requirement__contains=experience) | Q(
            qualification__contains=experience) | Q(
            budget__contains=budget_start) | Q(budget__contains=budget_end) | Q(
            access='open') | Q(availability='available'))
    serializer = FetchJobSerializer(job, many=True)
    print('found')
    if serializer.data:
        new_serializer = []
        for serial in serializer.data:
            if check_like(request, serial['job_key']):
                serial['is_like'] = True
            else:
                serial['is_like'] = False
            new_serializer.append(serial)
        return Response(new_serializer, status=status.HTTP_200_OK)
    else:
        job = JobsPost.objects.all()
        serializer = FetchJobSerializer(job, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_email_notify(request, action):
    if action == 'on':
        UserNotificationSettings.objects.get(user=request.user).update(email=True)
        return Response('on', status=status.HTTP_200_OK)

    elif action == 'off':
        UserNotificationSettings.objects.get(user=request.user).update(email=False)
        return Response('off', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_login_notify(request, action):
    if action == 'on':
        UserNotificationSettings.objects.get(user=request.user).update(login=True)
        return Response('on', status=status.HTTP_200_OK)
    elif action == 'off':
        UserNotificationSettings.objects.get(user=request.user).update(login=False)
        return Response('off', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_update_notify(request, action):
    if action == 'on':
        UserNotificationSettings.objects.get(user=request.user).update(update=True)
        return Response('on', status=status.HTTP_200_OK)
    elif action == 'off':
        UserNotificationSettings.objects.get(user=request.user).update(update=False)
        return Response('off', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_newsletter_notify(request, action):
    if action == 'on':
        UserNotificationSettings.objects.get(user=request.user).update(newsletter=True)
        return Response('on', status=status.HTTP_200_OK)

    elif action == 'off':
        UserNotificationSettings.objects.get(user=request.user).update(newsletter=False)
        return Response('off', status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def send_employment_request(request, interview_id):
    interview = Interviews.objects.get(interview_uid=interview_id)
    employees = request.data['employees']
    note = request.data['note']
    EmploymentRequest.objects.create(interview=interview, employees=employees, note=note)
    return Response('successful', status=status.HTTP_200_OK)


def job_close(job_id):
    try:
        JobsPost.objects.get(job_key=job_id).uodate(access='closed', availability='hide')
        return True
    except:
        return False


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def close_job(request, job_id):
    job = get_job(job_id)
    if job.employer.user == request.user:
        if job_close(job_id):
            return Response('closed', status=status.HTTP_200_OK)
    else:
        return Response('error', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def notification_settings(request):
    serializer = UserNotificationSettingsSerializer(request.user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)
