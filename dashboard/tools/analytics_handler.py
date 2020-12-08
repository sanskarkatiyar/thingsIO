import os
import pika
import redis
import jsonpickle

class analytics_handler:
    def __init__(self, MQ_HOST="localhost", redisHost="localhost"):
        self.mq_host = os.getenv("RABBITMQ_SERVICE_HOST") or MQ_HOST
        self.redisHost = os.getenv("REDIS_SERVICE_HOST") or "localhost"

        self.uuid_jobid_db = redis.Redis(host=self.redisHost, db=4)
        self.jobid_result_db = redis.Redis(host=self.redisHost, db=5)

    def send_msg_to_queue(self, data, exchange_name="toAnalytics", routing_key="data"):
        rabbitMQ = pika.BlockingConnection(pika.ConnectionParameters(host=self.mq_host))

        rabbitMQChannel = rabbitMQ.channel()
        rabbitMQChannel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        rabbitMQChannel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=data)
        rabbitMQ.close()

    def store_jobid_to_redis(self, uuid, jobid):
        return self.uuid_jobid_db.sadd(uuid, jobid)
