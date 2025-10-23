# syntax=docker/dockerfile:1

# ---- Base image ----
FROM python:3.12-slim

# ---- Environment variables ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Working directory ----
WORKDIR /app

# ---- Dependencies ----
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y netcat-traditional && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ---- Copy project ----
COPY . .

# ---- Collect static files (optional) ----
RUN python manage.py collectstatic --noinput

# ---- Port ----
EXPOSE 8000

# ---- Command ----
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
