import os
import redis
import uuid
import hashlib
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

# TODO: Make operations, transactional, if possible.

class accounts_handler:

    def __init__(self, redisHost=None):

        if not redisHost:
            self.redisHost = os.getenv("REDIS_SERVICE_HOST") or "localhost"
        else:
            self.redisHost = redisHost
        
        self.username_passhash_db = redis.Redis(host=redisHost, db=0)
        self.username_uuid_db = redis.Redis(host=redisHost, db=1)
        self.uuid_username_db = redis.Redis(host=redisHost, db=2)


    def isExistingUsername(self, uname):
        try:
            if self.username_passhash_db.get(uname):
                return True
        except:
            pass

        return False

    def isExistingUUID(self, uuid):
        try:
            if self.uuid_username_db.get(uuid):
                return True
        except:
            pass

        return False

    def getPasswordHashFromUsername(self, uname):
        try:
            ph = self.username_passhash_db.get(uname)
            if ph:
                return ph.decode()
        except:
            pass

        return ""

    def getPasswordHashFromUUID(self, uuid):
        try:
            un = self.uuid_username_db.get(uuid)

            if un:
                ph = self.username_passhash_db.get(un.decode())

            if ph:
                return ph.decode()
        except:
            pass

        return ""

    def getUsernameFromUUID(self, uuid):
        try:
            un = self.uuid_username_db.get(uuid)
            if un:
                return un.decode()
        except:
            pass

        return ""

    def getUUIDFromUsername(self, uname):
        try:
            uid = self.username_uuid_db.get(uname)
            if uid:
                return uid.decode()
        except:
            pass

        return ""

    def addUser(self, uname, passHash):
        try:
            if not self.isExistingUsername(uname):
                self.username_passhash_db.set(uname, passHash)

                # generate uuid
                uid = ""
                while True:
                    uid = uuid.uuid1().hex

                    try:
                        if len(self.uuid_username_db.get(uid).decode()):
                            continue
                    except:
                        break
                
                self.username_uuid_db.set(uname, uid)
                self.uuid_username_db.set(uid, uname)

                return True
        except:
            pass

        return False