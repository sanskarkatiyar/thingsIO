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

rabbitMQHost = os.getenv("RABBITMQ_SERVICE_HOST") or "localhost"
influxDBHost = os.getenv("INFLUXDB_SERVICE_HOST") or "localhost"
print("Connecting to rabbitmq({}) and influxdb({})".format(rabbitMQHost,influxDBHost))

ReadClient = DataFrameClient(influxDBHost, 8086, 'root', 'root', 'thingsIODB')
WriteClient = InfluxDBClient(influxDBHost, 8086, 'root', 'root','thingsIODB')


def getDatafromUUID(API_KEY):
    if(users_db.isExistingUUID(API_KEY)):
        schema = schema_db.getSchemaFromUUID(API_KEY)
        if(schema_db.isValidSchema(schema)):
            q = 'SELECT * FROM \"'+API_KEY+'\" WHERE time > now() - 24h;'
            result = ReadClient.query(q)
            df = result[API_KEY]
            return df
            # for key in schema.keys():
            #     name = schema[key]['name']
            #     datatype = schema[key]['type']
            #     q = 'SELECT \"'+key+'\" FROM \"'+API_KEY+'\" WHERE time > now() - 24h;'
            #     result = ReadClient.query(q)
            #     df = result[API_KEY]
            #     print(df)


def receive():
    
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
        WriteClient.create_database('thingsIODB')
        WriteClient.switch_database('thingsIODB')
        #Writing points to database from list of dict
        WriteClient.write_points(decoded)
        measurement = decoded[0]['measurement']
        #getDatafromUUID(measurement) #Calling the function to test data pull from influx

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