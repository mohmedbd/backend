release: python manage.py migrate --noinput
web: gunicorn QRcode.wsgi:application --bind 0.0.0.0:$PORT
