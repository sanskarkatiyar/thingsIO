FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN pip3 install jsonpickle pika requests numpy

ENV FLASK_APP=dashboard
ENV FLASK_ENV=development
CMD ["flask", "run"]

ENV	FLASK_PORT 5000