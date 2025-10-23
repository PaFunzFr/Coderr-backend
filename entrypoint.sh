#!/bin/sh
set -e

echo "[entrypoint] Starting container for Django app"

echo "[entrypoint] Running Django management commands"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Superuser automatisch anlegen, falls nicht vorhanden
echo "[entrypoint] Ensuring Django superuser exists"
python manage.py shell <<'PYCODE'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')
guest_password = os.environ.get('DJANGO_GUEST_PASSWORD', '123456')

# Admin
if not User.objects.filter(username=username).exists():
    print(f"[entrypoint] Creating superuser '{username}'")
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"[entrypoint] Superuser '{username}' created")
else:
    print(f"[entrypoint] Superuser '{username}' already exists")

# Guest-Logins
guests = [
    {"username": "Guest Customer", "email": "guest.customer@example.com", "password": guest_password},
    {"username": "Guest Business", "email": "guest.business@example.com", "password": guest_password},
]

for g in guests:
    if not User.objects.filter(username=g["username"]).exists():
        print(f"[entrypoint] Creating guest user '{g['username']}'")
        user = User.objects.create_user(username=g["username"], email=g["email"])
        user.set_password(g["password"])
        user.is_staff = False
        user.is_superuser = False
        user.save()
        print(f"[entrypoint] Guest user '{g['username']}' created")
    else:
        print(f"[entrypoint] Guest user '{g['username']}' already exists")
PYCODE

echo "[entrypoint] Starting Gunicorn"
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
