FROM python:3

WORKDIR /usr/src/app

COPY ../dashboard/tools/accounts_handler.py /usr/src/app/accounts_handler.py
COPY ../dashboard/tools/schema_handler.py /usr/src/app/schema_handler.py
COPY rest_server.py /usr/src/app

RUN pip3 install flask jsonpickle pika requests numpy

CMD ["python3", "rest_server.py"]
