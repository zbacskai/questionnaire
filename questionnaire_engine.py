import pymongo
from pymongo import MongoClient

class QuestionnaireEngine():
    def __init__(self):
        self._dbclient = MongoClient('localhost', 27017, username='root', password='example')
        self._db = self._dbclient['questions_db']

    def set_next_question(self, session_id, choice_index, answer):
        session_data = self._db['sessions'].find_one({'_id' : session_id})
        questionnaire = self._db['questionnaires'].find_one({'_id' : session_data['questionnaire']})
        for qdata in questionnaire['description']:
            if qdata['qid'] == session_data['next_question']:
                next_question = qdata['next'][choice_index]

        self._db['sessions'].update_one({ '_id' : session_id },
                                        { "$set" : { 'next_question' : next_question},
                                         "$push" : { 'answers' : answer }})


    def create_new_session(self, session_id):
        if self._db['sessions'].find_one({'_id' : session_id}) is not None:
            return

        qname = 'QUESTIONNAIRE-1-a'
        qdata = self._db['questionnaires'].find_one({'_id' : qname})
        first_question = qdata['start']
        self._db['sessions'].insert_one({ '_id' : session_id, 'next_question' : first_question,
                                         'questionnaire' : qname, 'answers' : [] })

    def get_next_question(self, session_id):
        qdata = self._db['sessions'].find_one({'_id' : session_id})
        return self._db['questions'].find_one({'_id' : qdata['next_question']})

    def create_doc(self, collection_name, document_description):
        self._db[collection_name].update_one({ '_id' : document_description['id'] },
                               { "$set" : document_description },
                               upsert=True)

        return { 'status_code' : 200 }

    def delete_doc(self, collection_name, document_description):
        document_name = document_description['id']
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
            all_documents.append(document['id'])

        return { 'status_code' : 200, 'data' : all_documents }


