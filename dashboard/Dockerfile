FROM python:3.7-slim

RUN apt-get update
RUN pip3 install --upgrade flask jsonpickle pika redis influxdb requests numpy pandas matplotlib

RUN mkdir -p /dashboard
COPY .* dashboard/

WORKDIR /dashboard

ENV FLASK_APP=dashboard
ENV FLASK_ENV=development
EXPOSE 5000

CMD flask run
