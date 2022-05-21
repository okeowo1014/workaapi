web: gunicorn --worker-tmp-dir /dev/shm workaapi.wsgi:application --timeout 200 --workers 4 -k uvicorn.workers.UvicornWorker
