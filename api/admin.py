from django.contrib import admin

from api import models

admin.site.register(models.User)
admin.site.register(models.Skills)
admin.site.register(models.WorkExperience)
admin.site.register(models.Employee)
admin.site.register(models.Employer)
admin.site.register(models.JobsPost)
admin.site.register(models.ApplyJob)
admin.site.register(models.Language)
admin.site.register(models.Education)
admin.site.register(models.Plans)
admin.site.register(models.DeletedUsers)
admin.site.register(models.LikedJobs)
admin.site.register(models.Support)
admin.site.register(models.PlanUpgradeRecord)
admin.site.register(models.Staff)
