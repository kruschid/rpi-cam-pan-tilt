# syntax=docker/dockerfile:1
FROM python:3.11-slim-bullseye 

RUN apt-get update && apt-get install make gcc ffmpeg libsm6 libxext6 -y

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY templates templates/

CMD ["python", "-u", "-m", "flask", "run", "--host=0.0.0.0"]
