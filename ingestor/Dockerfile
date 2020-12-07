FROM python:3

WORKDIR /usr/src/app
RUN pip3 install jsonpickle pika influxdb requests numpy

COPY ingestor_server.py /usr/src/app
CMD ["python3", "ingestor_server.py"]
