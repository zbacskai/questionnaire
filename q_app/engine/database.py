from pymongo import MongoClient
import os

MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = os.environ.get('MONGO_PORT', '27017')

class Database:
    def __init__(self):
        self._dbclient = MongoClient(
            MONGO_HOST, int(MONGO_PORT), username="root", password="example"
        )
        self._db = self._dbclient["questions_db"]

    def __getitem__(self, key):
        return self._db[key]


DB = Database()
