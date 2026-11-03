FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

RUN DJANGO_DEBUG=true python src/app.py collectstatic --noinput

EXPOSE 8000

# The local compose.yaml overrides this with the development server.
CMD ["gunicorn", "--chdir", "src", "--bind", "0.0.0.0:8000", "--workers", "2", "app:application"]
