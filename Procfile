release: python manage.py migrate
web: uvicorn workaapi.asgi:application --timeout 10 uvicorn.workers.UvicornWorker --timeout-keep-alive
worker: python manage.py runworker -v2
