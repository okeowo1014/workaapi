from django.urls import path

from .views import create_interview, create_obj_question, view_obj_questions, create_theory_question, \
    view_theory_questions, submit_objective_answer, submit_theory_answer, view_employee_interview, \
    view_submitted_interviews, view_posted_interviews

app_name = 'interview'
urlpatterns = [
    path('create_interview/<str:jobid>', create_interview, name='create_interview'),
    path('add_obj_question/<str:interview_id>', create_obj_question, name='add_obj_question'),
    path('add_theory_question/<str:interview_id>', create_theory_question, name='add_theory_question'),
    path('view_obj_questions/<str:interview_id>', view_obj_questions, name='view_obj_question'),
    path('view_theory_questions/<str:interview_id>', view_theory_questions, name='view_theory_question'),
    path('submit_obj_answer/<str:interview_id>', submit_objective_answer, name='submit_obj_answer'),
    path('submit_theory_answer/<str:interview_id>', submit_theory_answer, name='submit_theory_answer'),
    path('view_submitted_interviews/<str:interview_id>', view_submitted_interviews, name='view_submitted_interviews'),
    path('view_employee_interview/<str:interview_id>/<str:uid>', view_employee_interview,
         name='view_employee_interview'),
    path('view_posted_interviews/', view_posted_interviews, name='view_posted_interviews'),

]
