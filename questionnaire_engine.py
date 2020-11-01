import pymongo
from pymongo import MongoClient
class QuestionnaireEngine():
    def __init__(self):
        self._dbclient = MongoClient('localhost', 27017, username='root', password='example')
        self._db = self._dbclient['questions_db']
        self._questions = self._db['questions']

    def create_question(self, question_description):
        print(str(question_description))
        self._questions.update_one({ '_id' : question_description['name'] },
                               { "$set" : question_description },
                               upsert=True)

        return 200

    def list_all_questions(self):
        all_questions = []
        for question in self._questions.find({}):
            all_questions.append(question['name'])

        return all_questions


