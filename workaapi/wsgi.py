"""
WSGI config for workaapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

import gunicorn as gunicorn
from django.core.wsgi import get_wsgi_application

t = gunicorn

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workaapi.settings')

application = get_wsgi_application()
