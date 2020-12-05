import os
import redis
import jsonpickle

class schema_handler:

    def __init__(self, redisHost=None):

        if not redisHost:
            self.redisHost = os.getenv("REDIS_SERVICE_HOST") or "localhost"
        else:
            self.redisHost = redisHost
        
        self.uuid_schema_db = redis.Redis(host=redisHost, db=3)


    def getSchemaFromUUID(self, uuid):
        try:
            sc = self.uuid_schema_db.get(uuid)
            if sc:
                return jsonpickle.decode(sc.decode())
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
                if k.startswith() == 'field_' and len(schema[k]) > 0 and 'name' in schema[k] and 'type' in schema[k]:
                    continue
                else:
                    return False # some field has an incorrect key
            return True # all keys have correct format and >= 1 value

        return False    # no keys

    # TODO: Complete!
    def isValidPoint(self, uuid, point):
        s = getSchemaFromUUID(uuid)
        if len(s):   # check: schema exists
            p_set = set(point.keys())
            s_set = set(s.keys())

            if len(p_set - s_set) > 0:
                return False
            return True
        return False