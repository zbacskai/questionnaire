import pymongo
from pymongo import MongoClient
class QuestionnaireEngine():
    def __init__(self):
        self._dbclient = MongoClient('localhost', 27017, username='root', password='example')
        self._db = self._dbclient['questions_db']

    def create_doc(self, collection_name, document_description):
        self._db[collection_name].update_one({ '_id' : document_description['name'] },
                               { "$set" : document_description },
                               upsert=True)

        return { 'status_code' : 200 }

    def delete_doc(self, collection_name, document_description):
        document_name = document_description['name']
        document = self._db[collection_name].find_one({ '_id' : document_name })
        if not document:
            return { 'status_code' : 200, 'error' : f'No document with name: {document_name}' }

        self._db[collection_name].delete_one({ '_id' : document_name })

        return { 'status_code' : 200, 'deleted_document' : document }

    def get_doc(self, collection_name, document_name):
        document = self._db[collection_name].find_one({ '_id' : document_name })
        if not document:
            return { 'status_code' : 200, 'error' : f'No document with name: {document_name}' }

        return { 'status_code' : 200, 'data' : document }

    def list_all_docs(self, collection_name):
        all_documents = []
        for document in self._db[collection_name].find({}):
            all_documents.append(document['name'])

        return { 'status_code' : 200, 'data' : all_documents }


