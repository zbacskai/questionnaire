from pymongo import MongoClient

class Database():
    def __init__(self):
        self._dbclient = MongoClient(
            "localhost", 27017, username="root", password="example"
        )
        self._db = self._dbclient["questions_db"]

    def __getitem__(self, key):
        return self._db[key]

DB = Database()
