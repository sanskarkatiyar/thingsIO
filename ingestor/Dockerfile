FROM python:3.9.1-slim

RUN apt-get update

RUN pip3 install --upgrade jsonpickle pika influxdb requests numpy

RUN mkdir -p /ingestor
COPY *.py /ingestor/

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

CMD python3 /ingestor/ingestor_server.py
