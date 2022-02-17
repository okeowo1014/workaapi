release: python manage.py migrate
web: gunicorn workaapi.asgi:application --timeout 10 -w 4 -k uvicorn.workers.UvicornWorker
worker: python manage.py runworker -v2
