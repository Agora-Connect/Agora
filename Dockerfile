# base image
FROM python:3.11-slim

# labels and environments 
LABEL maintainer="Agora-Connect"

ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \ 
    gcc \
    pkg-config \ 
    default-libmysqlclient-dev \ 
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

EXPOSE 8000

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8000", "--workers", "2"]


