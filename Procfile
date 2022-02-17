release: python manage.py migrate
web: uvicorn workaapi.asgi:application uvicorn.workers.UvicornWorker --timeout 10
worker: python manage.py runworker -v2