from rest_framework import serializers
from api.models import Employee,JobsPost

from interview.models import Interviews, ObjectiveInterviewQuestions, TheoryInterviewQuestions, \
    ObjectiveInterviewAnswers, TheoryInterviewAnswers

class JobInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobsPost
        fields = ['employer_logo', 'title', 'budget']


class CreateInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interviews
        exclude = ['job']

class ListInterviewSerializer(serializers.ModelSerializer):
    job= JobInterviewSerializer(read_only=True, many=False)

    class Meta:
        model = Interviews
        fields = ["id","interview_uid","title","note","status","start_date","end_date","timer","timer_sec","interview_type","job"]

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interviews
        exclude = ['submission', 'created', 'job']


class CreateObjectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveInterviewQuestions
        exclude = ['interview', 'question_uid']


class CreateTheoryQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoryInterviewQuestions
        exclude = ['interview', 'question_uid']


class ObjectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveInterviewQuestions
        exclude = ['created', 'interview', 'id']


class EObjectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveInterviewQuestions
        fields = ['question']


class TheoryQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoryInterviewQuestions
        exclude = ['created', 'interview', 'id']


class ETheoryQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoryInterviewQuestions
        fields = ['question']


class ViewObjInterviewSerializer(serializers.ModelSerializer):
    obj_interview_question = ObjectiveQuestionSerializer(read_only=True, many=True)

    class Meta:
        model = Interviews
        fields = ['interview_uid', 'title', 'note', 'status', 'start_date', 'end_date', 'timer', 'timer_sec',
                  'interview_type',
                  'obj_interview_question']


class ViewTheoryInterviewSerializer(serializers.ModelSerializer):
    theory_interview_question = TheoryQuestionSerializer(read_only=True, many=True)

    class Meta:
        model = Interviews
        fields = ['interview_uid', 'title', 'note', 'status', 'start_date', 'end_date', 'timer', 'timer_sec',
                  'interview_type',
                  'theory_interview_question']


class SubmitObjectiveAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectiveInterviewAnswers
        fields = '__all__'


class SubmitTheoryAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheoryInterviewAnswers
        fields = '__all__'


class ViewObjEmployeeInterviewSerializer(serializers.ModelSerializer):
    question = EObjectiveQuestionSerializer(read_only=True, many=False)

    class Meta:
        model = ObjectiveInterviewAnswers
        fields = ['question', 'answer']


class ViewTheoryEmployeeInterviewSerializer(serializers.ModelSerializer):
    question = ETheoryQuestionSerializer(read_only=True, many=False)

    class Meta:
        model = TheoryInterviewAnswers
        fields = ['question', 'answer']


class IEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['uid', 'first_name', 'last_name', 'location']


class SubmittedInterviewObjSerializer(serializers.ModelSerializer):
    employee = IEmployeeSerializer(many=False, read_only=True)

    class Meta:
        model = ObjectiveInterviewAnswers
        fields = ['employee']


class SubmittedInterviewTheorySerializer(serializers.ModelSerializer):
    employee = IEmployeeSerializer(many=False, read_only=True)

    class Meta:
        model = TheoryInterviewAnswers
        fields = ['employee']

class PostedInterviewSerializer(serializers.ModelSerializer):
    job=JobInterviewSerializer(read_only=True, many=False)
    class Meta:
        model = Interviews
        fields = ['interview_uid', 'title', 'note', 'status', 'start_date', 'end_date', 'timer', 'timer_sec',
                  'interview_type','submission','job']