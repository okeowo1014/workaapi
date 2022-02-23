release: python manage.py makemigrations && python manage.py migrate
web: gunicorn workaapi.asgi:application --timeout 0 --workers 4 -k uvicorn.workers.UvicornWorker
