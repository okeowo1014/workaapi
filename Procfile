release: python manage.py migrate
web: gunicorn workaapi.asgi:application -k --timeout 10 uvicorn.workers.UvicornWorker --timeout-keep-alive
worker: python manage.py runworker -v2
