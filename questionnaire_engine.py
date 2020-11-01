import pymongo
from pymongo import MongoClient
class QuestionnaireEngine():
    def __init__(self):
        self._dbclient = MongoClient('localhost', 27017, username='root', password='example')
        self._db = self._dbclient['questions_db']
        self._questions = self._db['questions']

    def create_question(self, question_description):
        self._questions.update_one({ '_id' : question_description['name'] },
                               { "$set" : question_description },
                               upsert=True)

        return { 'status_code' : 200 }

    def delete_question(self, question_description):
        question_name = question_description['name']
        question = self._questions.find_one({ '_id' : question_name })
        if not question:
            return { 'status_code' : 200, 'error' : f'No question with name: {question_name}' }

        self._questions.delete_one({ '_id' : question_name })

        return { 'status_code' : 200, 'deleted_question' : question }

    def get_question(self, question_name):
        question = self._questions.find_one({ '_id' : question_name })
        if not question:
            return { 'status_code' : 200, 'error' : f'No question with name: {question_name}' }

        return { 'status_code' : 200, 'data' : question }

    def list_all_questions(self):
        all_questions = []
        for question in self._questions.find({}):
            all_questions.append(question['name'])

        return { 'status_code' : 200, 'data' : all_questions }


