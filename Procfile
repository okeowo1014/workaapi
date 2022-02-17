release: python manage.py migrate
web: daphne workaapi.asgi:application --port $PORT --bind 0.0.0.0 -v2 --t 3000 --websocket_timeout -1 --websocket_connect_timeout -1
worker: python manage.py runworker -v2