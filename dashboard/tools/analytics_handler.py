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
        self.jobid_request_db = redis.Redis(host=self.redisHost, db=6)


    def send_msg_to_queue(self, data, exchange_name="toAnalytics", routing_key="data"):
        rabbitMQ = pika.BlockingConnection(pika.ConnectionParameters(host=self.mq_host))
        rabbitMQChannel = rabbitMQ.channel()
        rabbitMQChannel.queue_declare(queue="queue_{}".format(exchange_name), durable=True)
        # rabbitMQChannel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        # rabbitMQChannel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=jsonpickle.encode(data))

        rabbitMQChannel.basic_publish(
                                        exchange='',
                                        routing_key='queue_{}'.format(exchange_name),
                                        body=jsonpickle.encode(data),
                                        properties=pika.BasicProperties(
                                            delivery_mode=2,  # make message persistent
                                    ))
        rabbitMQ.close()

    def store_jobid_to_redis(self, uuid, jobid):
        return self.uuid_jobid_db.lpush(uuid, jobid) # to get a sorted order of results

    def store_job_request(self, uuid, jobid, jobdesc):
        try:
            self.store_jobid_to_redis(uuid, jobid)
            self.jobid_request_db.set(jobid, jobdesc)
            return True
        except:
            return False

    def get_results_for_job(self, jobid):
        try:
            result = self.jobid_result_db.get(jobid)
            return jsonpickle.decode(result)
        except:
            return None

    def get_jobids_from_uuid(self, uuid):
        return list(self.uuid_jobid_db.lrange(uuid, 0, -1))

    def get_job_request_from_jobid(self, jobid):
        x = self.jobid_request_db.get(jobid)
        if x:
            return jsonpickle.decode(x.decode())
        else:
            return None
