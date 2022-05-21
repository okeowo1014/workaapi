import datetime
import magic
import requests
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
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

from administrator.models import UserLogs, AdminLog, JobLogs
from api.extractor import extract_keywords, generate_job_key, generate_employer_key, generate_employee_key
from api.location import Place
from api.members import positions, Industries, RelativeJobTags
from api.models import Skills, User, WorkExperience, Education, Language, Availability, Employee, ApplyJob, JobsPost, \
    Employer, LikedJobs, DeletedUsers, Plans, PlanUpgradeRecord, PaymentTrackRecord
from api.permissions import IsEmployer, IsEmployee
from api.serializers import SkillsSerializer, WESerializer, EmployeeProfileSerializer, EducationSerializer, \
    LanguageSerializer, AvailabilitySerializer, EmployeeSerializer, EmployerSerializer, JobsPostSerializer, \
    JobViewSerializer, JobApplicantSerializer, ApplyJobSerializer, PositionSerializer, IndustriesSerializer, \
    JobApplicantListSerializer, FetchJobSerializer, RelativeJobTagSerializer, JobsPostListSerializer, \
    EmployeeDetailsSerializer, SupportSerializer, PlansSerializer, EmployerDetailsUpdateSerializer, \
    CreateEmployerSerializer, JobsUpdateSerializer
from automator.views import DefaultEmployeeSettings, DefaultEmployerSettings
from chat.views import CreateMessageChannel, GetMessageChannel
from interview.models import Interviews, EmploymentRequest
from interview.serializers import ListInterviewSerializer
from notifier.models import HotEmployeeAlert, UserNotificationSettings, HotEmployerAlert
from notifier.serializers import EmployeeNotificationSerializer, EmployerNotificationSerializer, \
    HotEmployeeAlertSerializer, UserNotificationSettingsSerializer, HotEmployerAlertSerializer
from notifier.views import EmailNotifier, jobapplynotifier, employee_notifications, employer_notifications, \
    jobappliednotifier


def adduserlog(user, note):
    UserLogs.objects.create(user=user, note=note)
    return True


def addadminlog(user, log, note):
    AdminLog.objects.create(user=user, note=note, log=log)
    return True


def addjoblog(user, log, note):
    JobLogs.objects.create(user=user, note=note, log=log)
    return True


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
        adduserlog(serializer.user, 'login')
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
            emp = Plans.objects.get(pk=20220322)
            plan_serialize = PlansSerializer(emp, many=False)
            plan = plan_serialize.data
            if not already_login:
                DefaultEmployeeSettings(employee.uid)
        elif serializer.user.account_type == 'employer':
            employer = Employer.objects.get(user=serializer.user)
            Firstname = employer.first_name
            Lastname = employer.last_name
            Dp = employer.company_logo
            plan_serialize = PlansSerializer(employer.plan, many=False)
            plan = plan_serialize.data
            if not already_login:
                DefaultEmployerSettings(employer.uid)
        return Response(
            data=dict(token_serializer_class(token).data, user=serializer.user.account_type, firstname=Firstname,
                      lastname=Lastname, dp=Dp, plan=plan), status=status.HTTP_200_OK
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
            return redirect(reverse('utility:emailsuccess'))
        else:
            return Response(response.json())


@api_view(['GET', 'POST'])
def reset_password(request, uid, token):
    if request.POST:
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        payload = {'uid': uid, 'token': token, 'new_password': password, 're_new_password': confirm_password}
        url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-reset'
                                                                                              '-password-confirm'))
        response = requests.post(url, data=payload)
        if response.status_code == 204:
            adduserlog(request.user, 'change password')
            return Response({}, response.status_code)
        else:
            return Response(response.json())
    return render(request, 'workaapi/password_reset_page.html', context={'uid': uid, 'token': token})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    if request.POST:
        if request.user.account_type == 'employee':
            employee = get_employee(request)
        elif request.user.account_type == 'employer':
            employer = get_employer(request)
        else:
            pass

        password = request.POST['password']
        payload = {'current_password': password}
        url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-me'))
        response = requests.delete(url, data=payload, headers={'AUTHORIZATION': 'TOKEN {}'.format(str(request.auth))})
        if response.status_code == 204:
            addadminlog(request.user, 'delete', '{} deleted his account'.format(requests.user.email))
            if request.user.account_type == 'employee':
                DeletedUsers.objects.create(email=request.user.email, firstname=employee.first_name,
                                            lastname=employee.last_name, location=employee.location,
                                            about=employee.about, account_type=request.user.account_type,
                                            phone=employee.phone)
                return Response({}, status=status.HTTP_200_OK)
            elif request.user.account_type == 'employer':
                DeletedUsers.objects.create(email=request.user.email, firstname=employer.first_name,
                                            lastname=employer.last_name, location=employer.location,
                                            about=employer.company_profile, account_type=request.user.account_type,
                                            phone=employer.phone)
                return Response({}, status=status.HTTP_200_OK)
            else:
                pass

        else:
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)


# work experience crud

@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def add_work_experience(request):
    serializer = WESerializer(data=request.data)
    if serializer.is_valid():
        adduserlog(request.user, 'add work experience')
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
            adduserlog(request.user, 'update work experience')
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
            adduserlog(request.user, 'delete experience')
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
        adduserlog(request.user, 'add skills')
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
            adduserlog(request.user, 'update skill')
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
            adduserlog(request.user, 'delete skills')
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
        adduserlog(request.user, 'add education history')
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
            adduserlog(request.user, 'update education history')
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
            adduserlog(request.user, 'delete education history')
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
        adduserlog(request.user, 'add language')
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
            adduserlog(request.user, 'update language')
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
            adduserlog(request.user, 'delete language')
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
        try:
            prev = Availability.objects.filter(user=get_employee(request))
            prev.delete()
        except:
            pass
        serializer.save(user=get_employee(request))
        adduserlog(request.user, 'add availability')
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
            adduserlog(request.user, 'update availability')
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
            adduserlog(request.user, 'delete availability')
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
        if response.status_code == 201:
            serializer.save(user=getuser(response.json().get('id')), uid=generate_employee_key())
            addadminlog(getuser(response.json().get('id')), 'joined', 'registered as employee')
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(response.text, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def planchoice(id):
    return Plans.objects.get(pk=id)


@api_view(['POST'])
def add_employer(request):
    serializer = CreateEmployerSerializer(data=request.data)
    payload = {'email': request.data['email'], 'password': request.data['password'],
               're_password': request.data['re_password'],
               'account_type': 'employer'}
    url = '{0}://{1}{2}'.format(django_settings.PROTOCOL, django_settings.DOMAIN, reverse('api:user-list'))
    if serializer.is_valid():
        response = requests.post(url, data=payload)
        if response.status_code == 201:
            # print("{0} {1} {0}".format('hello', userid))
            serializer.save(user=getuser(response.json().get('id')), uid=generate_employer_key())
            addadminlog(getuser(response.json().get('id')), 'joined', 'registered as employer')
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, ])
def employee_details(request):
    employee = Employee.objects.get(user=request.user)
    if request.method == 'POST':
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            adduserlog(request.user, 'updated profile')
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
        adduserlog(request.user, 'posted job')
        addjoblog(request.user, 'post',
                  '{0} posted the vancancy of {1}'.format(employer.company_name, serializer.job.title))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated, IsEmployer])
def update_job(request, job_id):
    job = get_job(job_id)
    if request.user == job.employer.user:
        if request.method == 'GET':
            serializer = JobsUpdateSerializer(job, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            serializer = JobsUpdateSerializer(job, data=request.data)
            if serializer.is_valid():
                serializer.save();
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            job.delete()
            return Response({'response': 'deleted'}, status=status.HTTP_200_OK)
    else:
        return Response({'response': 'you are not the owner'}, status=status.HTTP_400_BAD_REQUEST)


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
        fss = FileSystemStorage(location='media/{}/display-picture'.format(employee.uid))
        file = fss.save(picture.name, picture)
        employee.display_picture = 'https://api.workanetworks.com/{}'.format(
            '{}/{}'.format(fss.base_location, picture.name))
        try:
            employee.save()
            adduserlog(request.user, 'change display picture')
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
    job = JobsPost.objects.get(job_key=request.data['jobid'])
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
            adduserlog(request.user, 'applied for {}'.format(job.title))
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
    applicant = Employee.objects.get(uid=uid)
    serializer = JobApplicantSerializer(applicant, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def job_application_list(request, jobid):
    ApplyJob.objects.filter(job=get_job(jobid), created__lt=get_job(jobid).shortlist_date, is_new=True).update(
        is_new=False)
    applications = ApplyJob.objects.filter(job=get_job(jobid))
    employer = get_employer(request)
    max_choices = employer.plan.max
    serializer = JobApplicantListSerializer(applications, many=True)
    return Response(dict(applications=serializer.data, max_choices=max_choices), status=status.HTTP_200_OK)


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
        adduserlog(request.user, 'changed password')
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
    if len(shortlist) <= job.employer.plan.max:
        if job.employer == get_employer(request):
            applicant = [get_employee_by_id(x) for x in shortlist]
            ApplyJob.objects.filter(job=job, applicant__in=applicant).update(status='shortlist')
            ApplyJob.objects.exclude(job=job, applicant__in=applicant).update(status='decline')
            msg_channel = CreateMessageChannel(request, group=shortlist, name=job.employer.company_name)
            msg_channel.push_shortlist_message()
            job.message_channel = msg_channel.chat_uid
            job.shortlist_date = timezone.now()
            job.save()
            adduserlog(request.user, 'create shortlist for {}'.format(job.title))
            addjoblog(request.user, 'shortlist', 'created shortlist for {}'.format(job.title))
            return Response({'response': 'shortlist created successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'response': 'you are not the employer'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'response': 'You cant shortlist more than {} per job'.format(job.employer.plan.max)},
                        status=status.HTTP_400_BAD_REQUEST)


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
        fss = FileSystemStorage(location='media/{}/company-logo'.format(employer.uid))
        fss.save(picture.name, picture)
        employer.company_logo = 'https://api.workanetworks.com/{}'.format(
            '{}/{}'.format(fss.base_location, picture.name))
        try:
            employer.save()
            adduserlog(request.user, 'change Company logo')
            try:
                JobsPost.objects.filter(employer=employer).update(employer_logo=employer.company_logo)
            except:
                pass
            return Response(employer.company_logo, status=status.HTTP_200_OK)
        except:
            return Response('cannot upload', status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        return Response(employer.company_logo, status=status.HTTP_200_OK)


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
            jobinterview = Interviews.objects.filter(job=each.job, questioned=True).order_by('-created')
            interviewlist.extend(jobinterview)
        except:
            pass
    serializer = ListInterviewSerializer(interviewlist, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_hot_alert(request):
    if request.user.account_type == 'employee':
        hot_note = HotEmployeeAlert.objects.filter(employee=get_employee(request))
        serializer = HotEmployeeAlertSerializer(hot_note, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.user.account_type == 'employer':
        hot_note = HotEmployerAlert.objects.filter(employer=get_employer(request))
        serializer = HotEmployerAlertSerializer(hot_note, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        pass


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, IsEmployer])
def employer_details(request):
    employer = Employer.objects.get(user=request.user)
    if request.method == 'POST':
        serializer = EmployerDetailsUpdateSerializer(employer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            adduserlog(request.user, 'update profile')
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        serializer = EmployerSerializer(employer, many=False)
        return Response(dict(serializer.data, email=request.user.email), status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        try:
            employer.delete()
            adduserlog(request.user, 'delete profile')
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


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def hot_jobs(request):
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
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_email_notify(request, action):
    if action == 'on':
        us = UserNotificationSettings.objects.get(user=request.user)
        us.email = True
        us.save()
        return Response('on', status=status.HTTP_200_OK)

    elif action == 'off':
        us = UserNotificationSettings.objects.get(user=request.user)
        us.email = False
        us.save()
        return Response('off', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_login_notify(request, action):
    if action == 'on':
        us = UserNotificationSettings.objects.get(user=request.user)
        us.login = True
        us.save()
        return Response('on', status=status.HTTP_200_OK)
    elif action == 'off':
        us = UserNotificationSettings.objects.get(user=request.user)
        us.login = False
        us.save()
        return Response('off', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_update_notify(request, action):
    if action == 'on':
        us = UserNotificationSettings.objects.get(user=request.user)
        us.update = True
        us.save()
        return Response('on', status=status.HTTP_200_OK)
    elif action == 'off':
        us = UserNotificationSettings.objects.get(user=request.user)
        us.update = False
        us.save()
        return Response('off', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def set_newsletter_notify(request, action):
    if action == 'on':
        us = UserNotificationSettings.objects.get(user=request.user)
        us.newsletter = True
        us.save()
        return Response('on', status=status.HTTP_200_OK)

    elif action == 'off':
        us = UserNotificationSettings.objects.get(user=request.user)
        us.newsletter = False
        us.save()
        return Response('off', status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def send_employment_request(request, interview_id):
    job = Interviews.objects.get(interview_uid=interview_id).job
    employees = request.data['employees']
    note = request.data['note']
    shortlist = employees.split(',')
    if job.employer == get_employer(request):
        if job.employer.plan.name == 'silver':
            EmploymentRequest.objects.create(mode='interview', mode_key=interview_id, employees=employees, note=note)
            channel = GetMessageChannel(job.message_channel)
            channel.push_employment_message(job.title)
            adduserlog(request.user, 'requested {0} applicant for {1}'.format(len(employees), job.title))
            addadminlog(request.user, 'request', 'requested {0} applicant for {1}'.format(len(employees), job.title))
            return Response({'response': 'successfull'}, status=status.HTTP_200_OK)
        else:
            allowable = job.employer.plan.max - job.employer.hired
            if allowable >= len(shortlist):
                EmploymentRequest.objects.create(mode='interview', mode_key=interview_id, employees=employees,
                                                 note=note)
                channel = GetMessageChannel(job.message_channel)
                channel.push_employment_message(job.title)
                adduserlog(request.user, 'requested {0} applicant for {1}'.format(len(employees), job.title))
                addadminlog(request.user, 'request',
                            'requested {0} applicant for {1}'.format(len(employees), job.title))
                return Response({'response': 'successfull'}, status=status.HTTP_200_OK)
            else:
                return Response({'response': 'maximum hired number exceeded! You can only employ {}'.format(allowable)},
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'response': 'not the owner'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def send_direct_employment_request(request, job_id):
    job = get_job(job_id)
    employees = request.data['employees']
    shortlist = employees.split(',')
    if job.employer == get_employer(request):
        if job.employer.plan.name == 'silver':
            applicant = [get_employee_by_id(x) for x in shortlist]
            ApplyJob.objects.filter(job=job, applicant__in=applicant).update(status='shortlist')
            ApplyJob.objects.exclude(job=job, applicant__in=applicant).update(status='decline')
            msg_channel = CreateMessageChannel(request, group=shortlist, name=job.employer.company_name)
            msg_channel.push_employment_message(job.title)
            job.message_channel = msg_channel.chat_uid
            job.availability = 'hide'
            job.access = 'closed'
            job.save()
        note = request.data['note']
        EmploymentRequest.objects.create(mode='direct', mode_key=job_id, employees=employees, note=note)
        adduserlog(request.user, 'requested {0} applicant for {1}'.format(len(applicant), job.title))
        addadminlog(request.user, 'request', 'requested {0} applicant for {1}'.format(len(applicant), job.title))
        return Response({'response': 'successful'}, status=status.HTTP_200_OK)
    else:
        allowable = job.employer.plan.max - job.employer.hired
        if allowable > len(shortlist):
            if job.employer == get_employer(request):
                applicant = [get_employee_by_id(x) for x in shortlist]
                ApplyJob.objects.filter(job=job, applicant__in=applicant).update(status='shortlist')
                ApplyJob.objects.exclude(job=job, applicant__in=applicant).update(status='decline')
                msg_channel = CreateMessageChannel(request, group=shortlist, name=job.employer.company_name)
                msg_channel.push_employment_message(job.title)
                job.message_channel = msg_channel.chat_uid
                job.availability = 'hide'
                job.access = 'closed'
                job.save()
            note = request.data['note']
            EmploymentRequest.objects.create(mode='direct', mode_key=job_id, employees=employees, note=note)
            adduserlog(request.user, 'requested {0} applicant for {1}'.format(len(applicant), job.title))
            addadminlog(request.user, 'request', 'requested {0} applicant for {1}'.format(len(applicant), job.title))
            return Response({'response': 'successful'}, status=status.HTTP_200_OK)
        else:
            Response({'response': 'maximum hired number exceeded! You can only employ {}'.format(allowable)},
                     status=status.HTTP_400_BAD_REQUEST)


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
            adduserlog(job.employer.user, 'close application for {}'.format(job.title))
            return Response('closed', status=status.HTTP_200_OK)
    else:
        return Response('error', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    NoticeUser = UserNotificationSettings(user=request.user)
    serializer = UserNotificationSettingsSerializer(NoticeUser, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def support_message(request):
    serializer = SupportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def planUpgrade(request, plan, trans_id):
    plan = planchoice(plan)
    employer = get_employer(request)
    employer.plan = plan
    employer.plan_active = True
    employer.save()
    PlanUpgradeRecord.objects.create(plan=plan, transaction=trans_id)
    serializer = PlansSerializer(employer.plan, many=False)
    adduserlog(employer.user, 'upgrade to {}'.format(plan.name))
    addadminlog(employer.user, 'upgrade', 'upgraded to {}'.format(plan.name))
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_records(request, trans_id):
    PaymentTrackRecord.objects.create(payer=request.user, payer_account=request.user.account_type, transaction=trans_id,
                                      narration='Account Upgrade')
    adduserlog(request.user, 'make payment')
    addadminlog(request.user, 'payment', 'make payment, trans. id is {}'.format(trans_id))
    return Response({"response": "successfull"}, status=status.HTTP_200_OK)


def get_mime_type(file):
    """
    Get MIME by reading the header of the file
    """
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(initial_pos)
    return mime_type


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def upload_cv(request):
    employee = Employee.objects.get(user=request.user)
    if request.method == 'POST' and request.FILES:
        cv = request.FILES['cv_file']
        if get_mime_type(cv) == 'application/pdf':
            fss = FileSystemStorage(location='media/{}/cv'.format(employee.uid))
            fss.save(cv.name, cv)
            employee.cv = 'https://api.workanetworks.com/{}'.format(
                '{}/{}'.format(fss.base_location, cv.name))
            try:
                employee.save()
                return Response({'response': '{}'.format(employee.cv)}, status=status.HTTP_200_OK)
            except:
                return Response({'response': 'cannot upload'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'response': 'un supported file type'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        return Response({'response': employee.cv}, status=status.HTTP_200_OK)
