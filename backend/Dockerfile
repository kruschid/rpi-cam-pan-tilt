FROM python:3.11-slim-bullseye 

WORKDIR /app

COPY  app.py \
      requirements.txt \
      .

RUN pip install -r requirements.txt

CMD flask --app app run --host=0.0.0.0
