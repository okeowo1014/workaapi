from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from api.models import Employee
from .models import DirectEmployeeNotifier, DirectEmployerNotifier


# Create your views here:
class EmailNotifier:
    def __init__(self, email):
        self.email = email

    def password_changed(self):
        subject = 'Password Reset Successfully'
        html_message = render_to_string('notifier/passwordchange.html', {'usermail': self.email})
        plain_message = strip_tags(html_message)
        from_email = 'okeowo1014@gmail.com'
        to = self.email

        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def job_application(self, job_title, company):
        subject = 'You have successfully applied for a job position'
        html_message = render_to_string('notifier/jobapplicationsubmited.html',
                                        {'job_title': job_title, 'company': company})
        plain_message = strip_tags(html_message)
        from_email = 'okeowo1014@gmail.com'
        to = self.email
        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def job_applied(self, job_title, fullname):
        subject = '{} successfully applied for a {}'.format(fullname, job_title)
        html_message = render_to_string('notifier/jobapplied.html',
                                        {'job_title': job_title, 'fullname': fullname})
        plain_message = strip_tags(html_message)
        from_email = 'okeowo1014@gmail.com'
        to = self.email
        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def interview_alert(self, text, company):
        subject = "Interview invitation from {}".format(company)
        html_message = render_to_string('notifier/interviewinvitation.html',
                                        {'text': text, 'company': company})
        plain_message = strip_tags(html_message)
        from_email = 'okeowo1014@gmail.com'
        to = self.email
        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def welcome_employee_activation(self, fullname):
        subject = "Welcome to Worka"
        html_message = render_to_string('notifier/welcomeemployee.html',
                                        {'fullname': fullname})
        plain_message = strip_tags(html_message)
        from_email = 'okeowo1014@gmail.com'
        to = self.email
        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def welcome_employer_activation(self, company):
        subject = "Welcome to Worka"
        html_message = render_to_string('notifier/welcomeemployer.html',
                                        {'company': company})
        plain_message = strip_tags(html_message)
        from_email = 'okeowo1014@gmail.com'
        to = self.email
        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def employee_interview_submitted(self, fullname, company):
        subject = 'Interview answers submitted'
        html_message = render_to_string('notifier/employeeinterviewnotice.html',
                                        {'fullname': fullname, 'company': company})
        plain_message = strip_tags(html_message)
        from_email = 'okeowo1014@gmail.com'
        to = self.email
        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def employer_interview_submitted(self, fullname, company):
        subject = '{} submitted Interview answers '.format(fullname)
        html_message = render_to_string('notifier/employerinterviewnotice.html',
                                        {'fullname': fullname, 'company': company})
        plain_message = strip_tags(html_message)
        from_email = 'okeowo1014@gmail.com'
        to = self.email
        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def jobapplynotifier(employee, job_title, company):
    title = "Job Application Sent Successfully"
    message = """
    Your Application for the post of {} has been sent to {}.
    We wish you best of luck!!!
    """.format(job_title, company)
    DirectEmployeeNotifier.objects.create(employee=employee, title=title, message=message)
    EmailNotifier(employee.user.email).job_application(job_title, company)


def jobappliednotifier(employer, fullname, job_title):
    title = "{} Applied for {}".format(fullname, job_title)
    message = """
    {} submitted application for the post of {}.
    Kindly view this application.
    """.format(fullname, job_title)
    DirectEmployerNotifier.objects.create(employer=employer, title=title, message=message)
    if employer.user.email == employer.company_email:
        EmailNotifier(employer.company_email).job_applied(job_title, fullname)
    else:
        EmailNotifier(employer.user.email).job_applied(job_title, fullname)
        EmailNotifier(employer.company_email).job_applied(job_title, fullname)


def interview_invitation_notifier(group, text, company):
    employees = [Employee.objects.get(user=each) for each in group]
    title = "Interview Invitation "
    message = "Your are invited for an interview by {}. Check your inbox for details.".format(company)
    for each in employees:
        DirectEmployeeNotifier.objects.create(employee=each, title=title, message=message)
        EmailNotifier(each.user.email).interview_alert(text, company)


def employee_notifications(employee):
    notifications = DirectEmployeeNotifier.objects.filter(employee=employee)
    return notifications


def employer_notifications(employer):
    notifications = DirectEmployerNotifier.objects.filter(employer=employer)
    return notifications


def employer_interview_notice(employer, fullname, job_title):
    title = "{} submitted interview answers for {}".format(fullname, job_title)
    message = """
        {} submitted interview answers for the post of {}.
        Kindly view this answers""".format(fullname, job_title)
    DirectEmployerNotifier.objects.create(employer=employer, title=title, message=message)
    if employer.user.email == employer.company_email:
        EmailNotifier(employer.company_email).employer_interview_submitted(fullname, job_title)
    else:
        EmailNotifier(employer.user.email).employer_interview_submitted(fullname, job_title)
        EmailNotifier(employer.company_email).employer_interview_submitted(fullname, job_title)


def employee_interview_notice(employee, job_title, company):
    title = "your Interview answers has been submitted"
    message = """
        your Interview answers has for the post of {} has been sent to {}.
        We wish you best of luck!!!""".format(job_title, company)
    DirectEmployeeNotifier.objects.create(employee=employee, title=title, message=message)
    EmailNotifier(employee.user.email).employee_interview_submitted(employee.fullname, company)
