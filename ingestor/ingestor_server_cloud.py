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
import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS



hostname = platform.node()


token = "cn1eTVldRTqf6Phf4SZadVqnlwvhre25y9img3OsQzbr9wpbgzZ7zVSI-ZNIdvcxo830jwg54uTCOnWMnbuLBw=="
org = "sisu7408@colorado.edu"
bucket = "thingsIO"


def receive():
    rabbitMQHost = os.getenv("RABBITMQ_SERVICE_HOST") or "localhost"
    #influxDBHost = os.getenv("INFLUXDB_SERVICE_HOST") or "localhost"
    
    print("Connecting to rabbitmq({})".format(rabbitMQHost))

    client = InfluxDBClient(url="https://us-central1-1.gcp.cloud2.influxdata.com", token=token ,org = org)
    
    write_api = client.write_api(write_options=SYNCHRONOUS)
    query_api = client.query_api()

    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='toIngestors',exchange_type='direct')

    result = rabbitMQChannel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    rabbitMQChannel.queue_bind(
        exchange='toIngestors', queue=queue_name, routing_key='data')

    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        decoded = jsonpickle.decode(body)

        database = decoded['database']
        json_body = decoded['json_body']
        
        
        write_api.write(bucket, org, json_body)  

        tables = query_api.query('from(bucket:"thingsIO") |> range(start: -10d)')

        for table in tables:
            print(table)
            for row in table.records:
                print (row.values)

    rabbitMQChannel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    rabbitMQChannel.start_consuming()
    print("done")

if __name__ == '__main__':
    try:
        receive()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)