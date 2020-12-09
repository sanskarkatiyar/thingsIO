#
# Rest server
#
from flask import Flask, request, Response
import jsonpickle, pickle
import platform
import io, os, sys
import pika
import requests
import sys
import datetime

from accounts_handler import accounts_handler

users_db = accounts_handler()
rabbitMQHost = os.getenv("RABBITMQ_SERVICE_HOST") or "localhost"
# Initialize the Flask application
app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return '<h1> thingsIO Server</h1><p> Use a valid endpoint </p>'

# route http posts to this method
@app.route('/store/<API_KEY>', methods=['POST'])
def sendJson(API_KEY):
    sendLogs('{} - REST - Received request for /store/{} at RabbitMQ Host-{}'.format(datetime.datetime.now(), API_KEY, rabbitMQHost))
    if(users_db.isExistingUUID(API_KEY)):
        req_data = request.get_json()

        jsonData = [{"measurement":API_KEY, "fields":req_data}]
        req_data_pickled = jsonpickle.encode(jsonData)      

        # print("Using host", rabbitMQHost)

        rabbitMQ = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitMQHost))
        rabbitMQChannel = rabbitMQ.channel()

        rabbitMQChannel.exchange_declare(exchange='toIngestors',
                                exchange_type='direct')
        rabbitMQChannel.basic_publish(exchange='toIngestors',
                            routing_key='data',
                            body=req_data_pickled)
        
        # print(" [x] Sent data ")
        rabbitMQ.close()
        response = { 'Status' : 'OK' }
    
    else:
        response = { 'Status' : "UUID does not exist"}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


def sendLogs(logdata):
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='logs',
                            exchange_type='direct')
    rabbitMQChannel.basic_publish(exchange='logs',
                        routing_key='logdata',
                        body=logdata)
    
    rabbitMQ.close()
# start flask app
app.run(host="0.0.0.0", port=6000)
