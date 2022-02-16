from django.contrib import admin
from .models import User, Skills, WorkExperience, Employee, Employer, JobsPost, ApplyJob,Language,Education

admin.site.register(User)
admin.site.register(Skills)
admin.site.register(WorkExperience)
admin.site.register(Employee)
admin.site.register(Employer)
admin.site.register(JobsPost)
admin.site.register(ApplyJob)
admin.site.register(Language)
admin.site.register(Education)