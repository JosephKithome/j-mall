release: heroku run python manage.py makemigrations core
release: heroku run python manage.py migrate core
release: heroku run python manage.py migrate 
release: heroku run python manage.py collectstatic --noinput

web: gunicorn deligo.wsgi