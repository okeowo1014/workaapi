from rest_framework import serializers

from api.models import Staff
from interview.models import ObjectiveInterviewAnswers
from interview.serializers import IEmployeeSerializer


class SubmittedInterviewObjSerializer(serializers.ModelSerializer):
    employee = IEmployeeSerializer(many=False, read_only=True)

    class Meta:
        model = ObjectiveInterviewAnswers
        fields = ['employee', ]


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['uid', 'first_name', 'last_name', 'phone', 'location', 'about', 'gender',
                  'display_picture']
