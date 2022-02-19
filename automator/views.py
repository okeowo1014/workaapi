# Create your views here.
from api.models import User, Employee, Employer
from chat.models import ChatChannels
from notifier.models import DirectEmployeeNotifier, HotEmployeeAlert, DirectEmployerNotifier, HotEmployerAlert
from notifier.views import EmailNotifier

# pip install - r requirements.txt

default_admin = User.objects.get(email='admin@worka.com')
default_admin_dp = 'https://api.workanetworks.com/static/media/company-logo/krp5oktnm2/306424.png'


class DefaultEmployeeSettings:
    def __init__(self, uid):
        self.employee = Employee.objects.get(uid=uid)
        self.user = self.employee.user
        self.email = self.user.email
        self.fullname = self.employee.fullname
        self.send_hot_alert()
        self.send_welcome_notification()
        self.send_welcome_email()
        self.create_default_channel()

    def send_welcome_notification(self):
        message = 'Hello! {}, you account have successfully being Activated.'.format(self.fullname)
        DirectEmployeeNotifier.objects.create(employee=self.employee, title='Welcome to worka',
                                              message=message)

    def send_welcome_email(self):
        EmailNotifier(self.email).welcome_employee_activation(self.fullname)

    def create_default_channel(self):
        channel = ChatChannels.objects.create(sender=default_admin, sender_dp=default_admin_dp, chat_type='normal',
                                              chat_uid=self.employee.uid, name='Worka Admin')
        channel.group.add(self.user)

    def send_hot_alert(self):
        HotEmployeeAlert.objects.create(message='Welcome! setup your profile.', link='profile', employee=self.employee)


class DefaultEmployerSettings:
    def __init__(self, uid):
        self.employer = Employer.objects.get(uid=uid)
        self.user = self.employer.user
        self.email = self.user.email
        self.company = self.employer.company_name
        self.send_hot_alert()
        self.send_welcome_notification()
        self.send_welcome_email()
        self.create_default_channel()

    def send_welcome_notification(self):
        message = 'Hello! {}, you account have successfully being Activated.'.format(self.company)
        DirectEmployerNotifier.objects.create(employer=self.employer, title='Welcome to worka',
                                              message=message)

    def send_welcome_email(self):
        EmailNotifier(self.email).welcome_employer_activation(self.company)

    def create_default_channel(self):
        channel = ChatChannels.objects.create(sender=default_admin, sender_dp=default_admin_dp, chat_type='normal',
                                              chat_uid=self.employer.uid, name='Worka Admin')
        channel.group.add(self.user)

    def send_hot_alert(self):
        HotEmployerAlert.objects.create(message='Welcome! setup your profile.', link='profile', employer=self.employer)
