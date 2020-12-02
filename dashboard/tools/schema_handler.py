import os
import redis
import jsonpickle

class schema_handler:

    def __init__(self, redisHost=None):

        if not redisHost:
            self.redisHost = os.getenv("REDIS_SERVICE_HOST") or "localhost"
        else:
            self.redisHost = redisHost
        
        self.uuid_schema_db = redis.Redis(host=redisHost, db=4)


    def getSchemaFromUUID(self, uuid):
        try:
            sc = self.uuid_schema_db.get(uuid)
            if sc:
                return jsonpickle.decode(sc)
        except:
            pass

        return ""

    def setSchemaForUUID(self, uuid, schema):
        try:
            self.uuid_schema_db.set(uuid, jsonpickle.encode(schema))
            return True
        except:
            pass

        return False

    def schemaExists(self, uuid):
        try:
            if self.uuid_schema_db.get(uuid):
                return True
        except:
            pass

        return False

    def isValidSchema(self, schema:dict):
        # NOTE: this is not the best way to identify a valid schema
        # all keys should have a `field` start
        if len(schema.keys()) > 0:
            for k in schema:
                if k.startswith() == 'field' and len(schema[k]) > 0:
                    continue
                else:
                    return False # some field has an incorrect key
            return True # all keys have correct format and >= 1 value

        return False    # no keys

    # TODO: Complete!
    def isValidPoint(self, uuid, point):
        pass
