web: gunicorn app.wsgi -k sync --workers=1 --log-file -
worker: python worker.py
release: python manage.py migrate
