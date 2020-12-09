#
# Ingestor server
#
import pickle
import jsonpickle
import platform
import json
import io
import os
import sys
import pika
from influxdb import InfluxDBClient
from influxdb import DataFrameClient


hostname = platform.node()

rabbitMQHost = os.getenv("RABBITMQ_SERVICE_HOST") or "localhost"
influxDBHost = os.getenv("INFLUXDB_SERVICE_HOST") or "localhost"
print("Connecting to rabbitmq({}) and influxdb({})".format(rabbitMQHost,influxDBHost))

WriteClient = InfluxDBClient(influxDBHost, 8086, 'root', 'root','thingsIODB')
WriteClient.create_database('thingsIODB')
WriteClient.switch_database('thingsIODB')

def receive():
    
    rabbitMQ = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='toIngestors', exchange_type='direct')

    result = rabbitMQChannel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    rabbitMQChannel.queue_bind(exchange='toIngestors', queue=queue_name, routing_key='data')

    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print("INGESTOR.{}.CALLBACK".format(hostname))
        decoded = jsonpickle.decode(body)
        # WriteClient.create_database('thingsIODB')
        # WriteClient.switch_database('thingsIODB')
        #Writing points to database from list of dict
        WriteClient.write_points(decoded)
        measurement = decoded[0]['measurement']

    rabbitMQChannel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    rabbitMQChannel.start_consuming()
    # print("done")


if __name__ == '__main__':
    try:
        receive()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)