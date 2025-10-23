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
from app_auth.models import UserProfile
User = get_user_model()
su_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
su_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
su_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')
guest_password = os.environ.get('DJANGO_GUEST_PASSWORD', '123456')

# Admin
if not User.objects.filter(username=su_username).exists():
    print(f"[entrypoint] Creating superuser '{su_username}'")
    su = User.objects.create_superuser(username=su_username, email=su_email, password=su_password)
    if not hasattr(su, "profile"):
        UserProfile.objects.create(user=su, type="business")
    print(f"[entrypoint] Superuser '{su_username}' created")
else:
    print(f"[entrypoint] Superuser '{su_username}' already exists")

# Guest-Logins
guests = [
    {"username": "Guest Customer", "email": "guest.customer@example.com", "password": guest_password, "type": "customer"},
    {"username": "Guest Business", "email": "guest.business@example.com", "password": guest_password, "type": "business"},
]

for g in guests:
    required_keys = {"username", "email", "password", "type"}
    missing = required_keys - set(g.keys())
    if missing:
        raise ValueError(f"[entrypoint] Guest definition missing keys: {missing}")

    user = User.objects.filter(username=g["username"]).first()
    if user is None:
        print(f"[entrypoint] Creating guest user '{g['username']}'")
        with transaction.atomic():
            user = User.objects.create_user(username=g["username"], email=g["email"])
            user.set_password(g["password"])
            user.is_staff = False
            user.is_superuser = False
            user.save()
            if not hasattr(user, "profile"):
                UserProfile.objects.create(user=user, type=g["type"])
        print(f"[entrypoint] Guest user '{g['username']}' created")
PYCODE

echo "[entrypoint] Starting Gunicorn"
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
