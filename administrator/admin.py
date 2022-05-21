from django.contrib import admin

# Register your models here.
from administrator.models import Employment, Payroll

admin.site.register(Employment)
admin.site.register(Payroll)