#
# Rest server
#
from flask import Flask, request, Response
import jsonpickle, pickle
import platform
import io, os, sys
import pika
import requests
import base64, codecs


# Initialize the Flask application
app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return '<h1> thingsIO Server</h1><p> Use a valid endpoint </p>'

# route http posts to this method
@app.route('/store', methods=['POST'])
def sendJson():
    req_data = request.get_json()
    req_data_pickled = jsonpickle.encode(req_data)
    rabbitMQHost = os.getenv("RABBITMQ_SERVICE_HOST") or "localhost"

    print("Using host", rabbitMQHost)

    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='toIngestors',
                            exchange_type='direct')
    rabbitMQChannel.basic_publish(exchange='toIngestors',
                        routing_key='data',
                        body=req_data_pickled)
    
    print(" [x] Sent data ")
    rabbitMQ.close()
    response = { 'Status' : "OK"}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# start flask app
app.run(host="0.0.0.0", port=5000)
