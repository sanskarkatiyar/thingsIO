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
import pandas as pd
sys.path.append('../')
import dashboard.tools.accounts_handler as accounts_handler
import dashboard.tools.schema_handler as schema_handler

users_db = accounts_handler.accounts_handler()
schema_db = schema_handler.schema_handler()


hostname = platform.node()

def getDatafromUUID(API_KEY):
    client = DataFrameClient(host='localhost', port=8086, username='root', password='root', database='database')
    print("Influxdb Connected")
    q = 'SELECT "field_1" FROM \"'+API_KEY+'\" WHERE time > now() - 24h;'
    result = client.query(q) # returns dict list
    df = result[API_KEY]
    print(df)
    # if(users_db.isExistingUUID(API_KEY)):
    #     schema = schema_db.getSchemaFromUUID(API_KEY)
    #     print(schema)
        # if(schema_db.isValidSchema(schema)):
        #     client = DataFrameClient(host='localhost', port=8086, username='root', password='root', database='database')
        #     print("Influxdb Connected")
        #     for key in schema.keys():
        #         name = key['name']
        #         datatype = key['type']
        #         q = 'SELECT \"'+key+'\" FROM \"'+API_KEY+'\" WHERE time > now() - 24h;'
        #         result = client.query(q)
        #         df = result[API_KEY]
        #         print(df)


def receive():
    rabbitMQHost = os.getenv("RABBITMQ_SERVICE_HOST") or "localhost"
    influxDBHost = os.getenv("INFLUXDB_SERVICE_HOST") or "localhost"
    
    print("Connecting to rabbitmq({}) and influxdb({})".format(rabbitMQHost,influxDBHost))


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

        #Connecting to influx db server
        client = InfluxDBClient(influxDBHost, 8086, 'root', 'root','database')
        
        #Writing points to database from list of dict
        client.write_points(decoded)

        measurement = decoded[0]['measurement']
        
        getDatafromUUID(measurement) #Calling the function to test data pull from influx

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