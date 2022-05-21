from django.contrib import admin

# Register your models here.
from interview.models import Interviews, ObjectiveInterviewAnswers, TheoryInterviewAnswers, ObjectiveInterviewQuestions, \
    TheoryInterviewQuestions, EmploymentRequest

admin.site.register(Interviews)
admin.site.register(ObjectiveInterviewAnswers)
admin.site.register(TheoryInterviewAnswers)
admin.site.register(ObjectiveInterviewQuestions)
admin.site.register(TheoryInterviewQuestions)
admin.site.register(EmploymentRequest)
