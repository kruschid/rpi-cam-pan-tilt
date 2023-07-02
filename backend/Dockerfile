# syntax=docker/dockerfile:1
FROM python:3.11-slim-bullseye 

WORKDIR /app

COPY  app.py \
      requirements.txt \
      .

COPY templates templates/

RUN apt-get update && apt-get install make gcc ffmpeg libsm6 libxext6 -y
RUN pip install -r requirements.txt

CMD ["python", "-u", "-m", "flask", "run", "--host=0.0.0.0"]

