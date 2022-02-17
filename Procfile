release: python manage.py migrate
web: daphne workaapi.asgi:application --port $PORT --bind 0.0.0.0 -v2 --timeout 300
worker: python manage.py runworker -v2