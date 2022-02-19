from django.urls import path

from utility.views import email_confirm_success, nearest_cities

app_name = 'utility'
urlpatterns = [
    path('email_confirm_success/', email_confirm_success, name='emailsuccess'),
    path('nearest_cities/<str:city>', nearest_cities, name='process'),

]
