FROM python:3.7-slim

RUN apt-get update

RUN pip3 install --upgrade jsonpickle pika redis influxdb requests numpy scipy pandas matplotlib seaborn patsy scikit-learn

RUN mkdir -p /analytics
COPY *.py analytics/

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

CMD python3 analytics/analytics.py
