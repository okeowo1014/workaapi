release: python manage.py makemigrations && python manage.py migrate
web: gunicorn workaapi.asgi:application --timeout 10 -w 4 -k uvicorn.workers.UvicornWorker --timeout-keep-alive 300
worker: python manage.py runworker -v2
