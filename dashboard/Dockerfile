FROM python:3.7-slim

RUN apt-get update
RUN pip3 install --upgrade flask jsonpickle pika redis influxdb requests numpy pandas matplotlib

RUN mkdir -p /app/
COPY dash.tar.gz /app/
WORKDIR /app/
RUN tar -zxvf dash.tar.gz

ENV FLASK_APP=/app/dashboard/__init__.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD flask run --host=0.0.0.0