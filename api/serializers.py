from abc import ABC
from collections import OrderedDict

from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from api.models import User, Skills, WorkExperience, Education, Language, Availability, Employee, Employer, JobsPost, \
    ApplyJob,LikedJobs


class UserCreateSerializer(UserCreateSerializer):
    username = None

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'account_type')


class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = ['id','skill_name', 'level', 'year_of_experience']


class WESerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id','title', 'company_name', 'description','start_date', 'end_date', 'current']

    def to_representation(self, instance):
        result = super(WESerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'school_name', 'level', 'certificate', 'course', 'current', 'start_date', 'end_date']

    def to_representation(self, instance):
        result = super(EducationSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'language', 'level']


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'full_time', 'part_time', 'contract']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['uid', 'first_name', 'last_name', 'phone', 'other_name', 'location', 'about', 'gender','display_picture']


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'


class EmployeeProfileSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(many=True, read_only=True)
    skill = SkillsSerializer(many=True, read_only=True)
    work_experience = WESerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    language = LanguageSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'employee', 'skill', 'work_experience', 'education',
                  'language']

class EmployeeEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email']


class JobsPostSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(many=False, read_only=True)

    class Meta:
        model = JobsPost
        fields = ['employer', 'job_key', 'title', 'description', 'qualification', 'benefit', 'categories', 'job_type',
                  'budget', 'tags', 'is_remote', 'location', 'expiry', 'access', 'requirement',
                  'applications']

class JobsPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobsPost
        fields = ['job_key', 'title', 'description', 'qualification', 'benefit', 'categories', 'job_type',
                  'budget', 'tags', 'is_remote', 'location', 'expiry', 'access', 'requirement',
                  'applications']


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplyJob
        fields = '__all__'


class JobApplicantSerializer(serializers.ModelSerializer):
    skill = SkillsSerializer(many=True, read_only=True)
    work_experience = WESerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    language = LanguageSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = ['uid', 'first_name', 'last_name','display_picture', 'other_name', 'about', 'gender', 'location', 'skill',
                  'work_experience', 'education',
                  'language']


class ApplyJobSerializer(serializers.ModelSerializer):
    job = JobsPostSerializer(many=False, read_only=True)

    class Meta:
        model = ApplyJob
        fields = ['id', 'job', 'status', 'created']


class PositionSerializer(serializers.Serializer):
    position = serializers.CharField(max_length=200)


class IndustriesSerializer(serializers.Serializer):
    industry = serializers.CharField(max_length=200)


class CompanyName(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['company_name']


class MyJobsPostSerializer(serializers.ModelSerializer):
    employer = CompanyName(many=False, read_only=True)

    class Meta:
        model = JobsPost
        fields = ['employer', 'job_key', 'title', 'job_type',
                  'budget', ]


class MyJobSerializer(serializers.ModelSerializer):
    job = MyJobsPostSerializer(many=False, read_only=True)

    class Meta:
        model = ApplyJob
        fields = ['id', 'job', 'status', 'created']


class JobApplicantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['uid', 'first_name', 'last_name', 'other_name', 'about', 'gender','display_picture', 'location']


class AboutEmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['company_name', 'company_logo', 'company_profile', 'location', 'reviews', 'hired']


class FetchJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobsPost
        fields = ['employer_logo','title','job_key', 'description', 'is_remote', 'job_type', 'location', 'budget',
                  'salary_type']


class RelativeJobTagSerializer(serializers.Serializer):
    tag = serializers.CharField(max_length=200)


class JobViewSerializer(serializers.ModelSerializer):
    employer = AboutEmployerSerializer(many=False, read_only=True)

    class Meta:
        model = JobsPost
        fields = ['employer', 'job_key', 'title', 'description', 'is_remote', 'job_type', 'location',
                  'budget', 'benefit', 'qualification', 'requirement', 'salary_type', 'categories', 'is_remote','employer_logo','expiry']


class EmployeeDetailsSerializer(serializers.ModelSerializer):
    user=EmployeeEmailSerializer(many=False,read_only=True)
    skill = SkillsSerializer(many=True, read_only=True)
    work_experience = WESerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    language = LanguageSerializer(many=True, read_only=True)
    availability=AvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = ['uid', 'first_name', 'last_name','display_picture', 'other_name','phone', 'about', 'gender', 'location', 'user','skill',
                  'work_experience', 'education','availability',
                  'language']

class LikedJobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikedJobs
        fields = ['liker']