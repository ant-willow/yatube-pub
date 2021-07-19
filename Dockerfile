FROM python:3.8.5

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
