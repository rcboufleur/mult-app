FROM python:3.11-slim

WORKDIR /app

COPY src/app.py .

CMD ["python", "-u", "app.py"]