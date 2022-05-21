import json

from django.shortcuts import get_object_or_404
# Create your views here.
from django.utils.datetime_safe import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.extractor import generate_interview_key, generate_obj_question_key, generate_theory_question_key
from api.models import Employee
from api.permissions import IsEmployer, IsEmployee
from api.views import get_job, get_employer
from chat.views import GetMessageChannel
from interview.models import Interviews, ObjectiveInterviewQuestions, TheoryInterviewQuestions, \
    ObjectiveInterviewAnswers, TheoryInterviewAnswers
from interview.serializers import CreateInterviewSerializer, CreateObjectiveQuestionSerializer, \
    CreateTheoryQuestionSerializer, \
    ViewObjInterviewSerializer, ViewTheoryInterviewSerializer, ViewObjEmployeeInterviewSerializer, \
    ViewTheoryEmployeeInterviewSerializer, IEmployeeSerializer, PostedInterviewSerializer, InterviewSerializer
from notifier.views import employee_interview_notice, employer_interview_notice


def write_interview_mesage(data):
    print(datetime.strptime(data['start_date'], "%Y-%m-%d").strftime("%B %d,%Y"))
    text = 'You have been schedule for an interview on {}.'.format(
        datetime.strptime(data['start_date'], "%Y-%m-%d").strftime("%B %d,%Y"))
    if data['end_date']:
        text += ' The interview closes {}.'.format(datetime.strptime(data['end_date'], "%Y-%m-%d").strftime("%B %d,%Y"))
    if data['timer']:
        text += ' The interview will last for {} minutes.'.format(data['timer_sec'])
    text += " Please get prepared! Wish you best of luck!!."
    return text


def get_obj_interview(interview_id):
    return Interviews.objects.get(interview_uid=interview_id, interview_type='objective')


def get_theory_interview(interview_id):
    return Interviews.objects.get(interview_uid=interview_id, interview_type='theory')


def get_interview(interview_id):
    return Interviews.objects.get(interview_uid=interview_id)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def create_interview(request, jobid):
    job = get_job(jobid)
    if job.employer.user == request.user:
        serializer = CreateInterviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(job=job, interview_uid=generate_interview_key())
            text = write_interview_mesage(serializer.data)
            GetMessageChannel(job.message_channel).push_interview_alert(text, job.employer.company_name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def create_obj_question(request, interview_id):
    interview = get_obj_interview(interview_id)
    interview.questioned = True
    interview.save()
    serializer = CreateObjectiveQuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(interview=interview, question_uid=generate_obj_question_key())
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def create_theory_question(request, interview_id):
    interview = get_theory_interview(interview_id)
    interview.questioned = True
    interview.save()
    serializer = CreateTheoryQuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(interview=interview, question_uid=generate_theory_question_key())
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_obj_questions(request, interview_id):
    interview = get_interview(interview_id)
    serializer = ViewObjInterviewSerializer(interview, many=False)
    if request.user.account_type == 'employee':
        try:
            ObjectiveInterviewAnswers.objects.get(interview=interview, employee__user=request.user)
            is_submitted = True
        except:
            is_submitted = False
        return Response(data=dict(serializer.data, submitted=is_submitted), status=status.HTTP_200_OK)

    else:
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_theory_questions(request, interview_id):
    interview = get_interview(interview_id)
    serializer = ViewTheoryInterviewSerializer(interview, many=False)
    if request.user.account_type == 'employee':
        try:
            TheoryInterviewAnswers.objects.get(interview=interview, employee__user=request.user)
            is_submitted = True
        except:
            is_submitted = False
        return Response(data=dict(serializer.data, submitted=is_submitted), status=status.HTTP_200_OK)

    else:
        return Response(serializer.data, status=status.HTTP_200_OK)


def marker(answer, choice, option):
    options = option.split(',')
    mapper = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    if options[mapper.get(choice)] == answer:
        return 'correct'
    else:
        return 'incorrect'


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployee])
def submit_objective_answer(request, interview_id):
    employee = Employee.objects.get(user=request.user)
    answers = json.loads(request.data['answers'])
    interview = get_obj_interview(interview_id)
    for key, values in answers.items():
        question = get_object_or_404(ObjectiveInterviewQuestions, question_uid=key)
        ObjectiveInterviewAnswers.objects.create(employee=employee, question=question, interview=interview,
                                                 answer=values,
                                                 status=marker(values, question.answer, question.options))
    employee_interview_notice(employee, interview.job.title, interview.job.employer.company_name)
    employer_interview_notice(interview.job.employer, employee.fullname, interview.job.title)
    interview.submission += 1
    interview.save()
    return Response('success', status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployee])
def submit_theory_answer(request, interview_id):
    employee = Employee.objects.get(user=request.user)
    answers = json.loads(request.data['answers'])
    interview = get_theory_interview(interview_id)
    for key, values in answers.items():
        question = get_object_or_404(TheoryInterviewQuestions, question_uid=key)
        TheoryInterviewAnswers.objects.create(employee=employee, question=question, interview=interview,
                                              answer=values)
    employee_interview_notice(employee, interview.job.title, interview.job.employer.company_name)
    employer_interview_notice(interview.job.employer, employee.fullname, interview.job.title)
    interview.submission += 1
    interview.save()
    return Response('success', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def view_employee_interview(request, interview_id, uid):
    employee = get_object_or_404(Employee, uid=uid)
    interview = get_interview(interview_id)
    if interview.interview_type == 'objective':
        answer = ObjectiveInterviewAnswers.objects.filter(interview=interview, employee=employee)
        percent = round(answer.filter(status='correct').count / answer.count * 100)
        serializer = ViewObjEmployeeInterviewSerializer(answer, many=True)
    elif interview.interview_type == 'theory':
        answer = TheoryInterviewAnswers.objects.filter(interview=interview, employee=employee)
        serializer = ViewTheoryEmployeeInterviewSerializer(answer, many=True)
        percent = -1
    return Response(dict(q_and_a=serializer.data, percent=percent), status=status.HTTP_200_OK)


def get_employee(id):
    return Employee.objects.get(pk=id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_submitted_interviews(request, interview_id):
    interview = get_interview(interview_id)
    max_choices = interview.job.employer.plan.max
    if interview.interview_type == 'objective':
        submitted = [get_employee(e['employee']) for e in
                     ObjectiveInterviewAnswers.objects.filter(interview=interview).values('employee').distinct()]

        serializer = IEmployeeSerializer(submitted, many=True)
    elif interview.interview_type == 'theory':
        submitted = [get_employee(e['employee']) for e in
                     TheoryInterviewAnswers.objects.filter(interview=interview).values('employee').distinct()]
        serializer = IEmployeeSerializer(submitted, many=True)
    return Response(dict(submission=serializer.data, max_choices=max_choices), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def view_posted_interviews(request):
    interviews = Interviews.objects.filter(job__employer=get_employer(request)).order_by('-created')
    serializer = PostedInterviewSerializer(interviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def employee_view_interview(request, interview_id):
    interview = get_interview(interview_id)
    if interview.interview_type == 'objective':
        try:
            ObjectiveInterviewAnswers.objects.get(interview=interview, employee__user=request.user)
            is_submitted = True
        except:
            is_submitted = False
    else:
        try:
            TheoryInterviewAnswers.objects.get(interview=interview, employee__user=request.user)
            is_submitted = True
        except:
            is_submitted = False
    serializer = InterviewSerializer(interview, many=False)
    return Response(data=dict(serializer.data, submitted=is_submitted), status=status.HTTP_200_OK)
