import os
import redis
import hashlib
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

# TODO: Make operations, transactional

class accounts_handler:

    def __init__(self, db, redisHost=None):
        self.db = db

        if not redisHost:
            self.redisHost = os.getenv("REDIS_SERVICE_HOST") or "localhost"
        else:
            self.redisHost = redisHost
        
        self.rdb = redis.Redis(host=redisHost, db=self.db)


    def isExistingUsername(self, uname):
        # try:
        #     if self.rdb.get(uname):
        #         return True
        # except:
        #     pass

        if self.rdb.get(uname):
            return True

        return False

    def getPasswordHash(self, uname):
        # try:
        #     ph = self.rdb.get(uname)
        #     if ph:
        #         return ph.decode()
        # except:
        #     pass
        ph = self.rdb.get(uname)
        if ph:
            return ph.decode()

        return ""

    def addUser(self, uname, passHash):
        # try:
        #     if not self.isExistingUsername(uname):
        #         self.rdb.set(uname, passHash)
        #         return True
        # except:
        #     pass
        if not self.isExistingUsername(uname):
            self.rdb.set(uname, passHash)
            return True

        return False

