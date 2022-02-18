release: python manage.py makemigrations && python manage.py migrate
web: gunicorn workaapi.asgi:application --timeout 200 --preload --workers 3 -w 4 -k uvicorn.workers.UvicornWorker
worker: python manage.py runworker -v2
