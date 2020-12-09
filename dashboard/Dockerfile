FROM python:3.7-slim

RUN apt-get update
RUN pip3 install --upgrade flask jsonpickle pika redis influxdb requests numpy pandas matplotlib

RUN mkdir -p /app/
COPY dashboard.tar.gz /app/
WORKDIR /app/
RUN tar -zxvf dashboard.tar.gz
RUN pip3 install -e dashboard

ENV FLASK_APP=/app/dashr/__init__.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD flask run --host=0.0.0.0