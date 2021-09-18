release: python manage.py makemigrations core
release: python manage.py migrate core core
release: python manage.py migrate core
release: python manage.py collectstatic --noinput

web: gunicorn deligo.wsgi