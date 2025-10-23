FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y netcat-traditional && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY . .
EXPOSE 8000
CMD ["bash","-lc","python manage.py migrate && python manage.py collectstatic --noinput && exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60"]