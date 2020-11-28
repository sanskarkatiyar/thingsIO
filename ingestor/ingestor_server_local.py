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



hostname = platform.node()


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

        database = decoded['database']
        json_body = decoded['json_body']
        
        #Connecting to influx db server
        client = InfluxDBClient(influxDBHost, 8086, 'root', 'root', database)

        #Creating a database
        client.create_database(database)

        #Switching to the database
        client.switch_database(database)

        #Writing points to database from list of dict
        client.write_points(json_body)

        measurement = json_body[0]['measurement']

        #Quering points from database
        result = client.query('SELECT * FROM '+database+".autogen."+measurement)
        print("Result: {0}".format(result))
        

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