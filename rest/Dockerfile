FROM python:3.9.1-slim

RUN apt-get update

RUN pip3 install --upgrade flask jsonpickle pika redis requests numpy

RUN mkdir -p /rest
COPY *.py rest/

EXPOSE 6000

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

CMD python3 rest/rest_server.py