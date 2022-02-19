from django.urls import path, include

from .views import index, checkauth, add_work_experience, view_employeeprofile, \
    work_experience_details, view_work_experiences, add_skill, skill_details, view_skills, add_education, \
    education_details, view_educations, add_language, language_details, view_languages, add_availability, \
    availability_details, view_availabilitys, add_employee, add_employer, post_job, employee_details, check_tag, \
    display_picture, view_job, apply_job, job_application_view, change_password, get_my_job, CustomLogin, get_positions, \
    get_industries, get_posted_jobs, job_application_list, create_shortlist, fetch_jobs, \
    get_relative_job_tags, company_logo, get_notifications, cv_preview, search_jobs, profile_preview, get_nearest_job, \
    get_my_interview, get_hot_alert, profile_details, employer_details, like_job, dislike_job, \
    filter_jobs, set_update_notify, set_newsletter_notify, set_email_notify, set_login_notify, send_employment_request, \
    notification_settings

app_name = 'api'
urlpatterns = [
    path('checkserver/', index, name='checksever'),
    path('checkauth/', checkauth, name='checkauth'),
    path('addskill/', add_skill, name='addskill'),
    path('addworkexperince/', add_work_experience, name='addworkexperience'),
    path('viewworkexperiences/', view_work_experiences, name='viewworkexperiences'),
    path('viewskills/', view_skills, name='viewskills'),
    path('view_employeeprofile/', view_employeeprofile, name='view_employeeprofile'),
    path('workexperiencedetails/<pk>', work_experience_details, name='work_experience_details'),
    path('skilldetails/<pk>', skill_details, name='skill_details'),
    path('addeducation/', add_education, name='addeducation'),
    path('educationdetails/<pk>', education_details, name='education_details'),
    path('vieweducations/', view_educations, name='vieweducations'),
    path('addlanguage/', add_language, name='addlanguage'),
    path('languagedetails/<pk>', language_details, name='language_details'),
    path('viewlanguages/', view_languages, name='viewlanguages'),
    path('addavailability/', add_availability, name='addavailability'),
    path('availabilitydetails/<pk>', availability_details, name='availability_details'),
    path('viewavailabilities/', view_availabilitys, name='viewavalabilitys'),
    path('addemployee/', add_employee, name='addemployee'),
    path('employeedetails/', employee_details, name='employee_details'),
    path('employerdetails/', employer_details, name='employer_details'),
    path('profile_details/', profile_details, name='profile_details'),
    path('addemployer/', add_employer, name='addemployer'),
    path('checktags/', check_tag, name='checktags'),
    path('postjob/', post_job, name='postjob'),
    path('viewjob/<str:jobid>', view_job, name='viewjob'),
    path('view_job_application/<str:uid>', job_application_view, name='viewjobapplication'),
    path('applyjob/', apply_job, name='applyjob'),
    path('display_picture/', display_picture, name='display_picture'),
    path('change_password/', change_password, name='change_password'),
    path('get_my_job/', get_my_job, name='getmyjob'),
    path('auth/login/', CustomLogin.as_view()),
    path('get_positions/', get_positions),
    path('get_industries/', get_industries),
    path('get_posted_jobs/', get_posted_jobs),
    path('fetch_jobs/', fetch_jobs),
    path('cv_preview/', cv_preview),
    path('profile_preview/', profile_preview),
    path('get_nearest_job/', get_nearest_job),
    path('search/', search_jobs),
    path('filter/', filter_jobs),
    # path('locate/', get_location),
    path('relative_job_tags/', get_relative_job_tags),
    path('company_logo/', company_logo),
    path('job_application_list/<str:jobid>', job_application_list),
    path('create_shortlist/<str:jobid>', create_shortlist),
    path('like/<str:jobid>', like_job),
    path('dislike/<str:jobid>', dislike_job),
    path('fetch_notifications/', get_notifications),
    path('get_my_interview/', get_my_interview),
    path('notification_settings/', notification_settings),
    path('get_hot_alert/', get_hot_alert),
    path('set_newsletter_notify/<str:action>', set_newsletter_notify),
    path('set_login_notify/<str:action>', set_login_notify),
    path('set_email_notify/<str:action>', set_email_notify),
    path('set_update_notify/<str:action>', set_update_notify),
    path('send_employment_request/<str:interview_id>', send_employment_request),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]
