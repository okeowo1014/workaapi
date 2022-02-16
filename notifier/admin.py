from django.contrib import admin

# Register your models here.
from notifier.models import DirectEmployeeNotifier, HotEmployeeAlert, DirectEmployerNotifier, HotEmployerAlert

admin.site.register(HotEmployeeAlert)
admin.site.register(HotEmployerAlert)
admin.site.register(DirectEmployeeNotifier)
admin.site.register(DirectEmployerNotifier)
