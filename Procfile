web: gunicorn app.wsgi -k sync --workers=1 --log-file -
release: python manage.py migrate
