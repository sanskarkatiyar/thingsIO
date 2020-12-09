FROM python:3.7-slim

RUN apt-get update
RUN pip3 install --upgrade flask jsonpickle pika redis influxdb requests numpy pandas matplotlib

ENV FLASK_APP=app/dashboard/__init__.py
ENV FLASK_ENV=development

RUN mkdir -p /app/dashboard
COPY dashboard/ app/dashboard/
# COPY . app/dashboard/
# ADD . app/dashboard/
# COPY ./__init__.py /app/dashboard/__init__.py

WORKDIR /app

EXPOSE 5000

CMD flask run
