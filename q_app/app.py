import os

from bson import ObjectId
from flask import Flask, render_template, request, session
from flask.json import jsonify

from q_app.engine.config_api import ConfigureApi
from q_app.engine.constants import QuestionTypes
from q_app.engine.database import Database
from q_app.engine.questionnaire import QuestionnaireEngine
from q_app.flask.forms import FormFactory
from q_app.flask.submission import UserInputHandler

API_VERSION = "0.1"

QUESTIONS = "questions"
QUESTIONS_DB = "questions"
QUESTIONNAIRES = "questionnaires"
QUESTIONNAIRES_DB = "questionnaires"
ABTESTS = "abtests"
ABTEST_DB = "configuration"
ABTEST_KEY = "testconfig"

DB = Database()
CA = ConfigureApi(DB)
QE = QuestionnaireEngine(DB)
UI = UserInputHandler(QE)

UUID = 'uuid'

FINAL_THANK_TEMPLATE = "thanks-for-submit.html"
QUESTION_TEMPLATE = "question-step.html"

class QuestionaireApp:
    def _get_title(self, question, session_id):
        if 'title' in question:
            return question

        question_count = self._qe.get_question_count(session_id)
        question['title'] = f'Question {question_count}'
        return question

    def _handle_question(self, question, session_id):
        if question["type"] == QuestionTypes.QuestionnaireClosure:
            return render_template(FINAL_THANK_TEMPLATE)

        question = self._get_title(question, session_id)
        form = FormFactory.create_form(question["type"], question["definition"])
        if form.validate_on_submit():
            return self._ui.store_answer_and_get_next(question, form, session_id)

        return render_template(QUESTION_TEMPLATE, form=form, title=question["title"])


    # Rest API
    def handle_questionnaire(self):
        if UUID not in session or not QE.session_is_valid(ObjectId(session[UUID])):
            session["uuid"] = str(self._qe.create_new_session())

        session_uuid = ObjectId(session[UUID])

        question = self._qe.get_question(session_uuid)
        return self._handle_question(question, session_uuid)


    def create_question(self):
        return jsonify(self._ca.create_doc(QUESTIONS_DB, request.json))


    def delete_question(self):
        return jsonify(self._ca.delete_doc(QUESTIONS_DB, request.json))


    def get_question(self):
        if "name" not in request.args:
            status = {"status_code": 200, "error": 'variable "name" missing in query'}
        else:
            status = self._ca.get_doc(QUESTIONS_DB, request.args["name"])

        return jsonify(status)


    def get_question_list(self):
        return jsonify(self._ca.list_all_docs(QUESTIONS_DB))


    def create_questionnaire(self):
        return jsonify(self._ca.create_doc(QUESTIONNAIRES_DB, request.json))


    def delete_questionnaire(self):
        return jsonify(self._ca.delete_doc(QUESTIONNAIRES_DB, request.json))


    def get_questionnaire(self):
        if "name" not in request.args:
            status = {"status_code": 200, "error": 'variable "name" missing in query'}
        else:
            status = self._ca.get_doc(QUESTIONNAIRES_DB, request.args["name"])

        return jsonify(status)


    def get_questionnaires_list(self):
        status = self._ca.list_all_docs(QUESTIONNAIRES_DB)
        return jsonify(status)


    def create_abtest(self):
        request.json["id"] = ABTEST_KEY
        return jsonify(self._ca.create_doc(ABTEST_DB, request.json))


    def delete_abtest(self):
        return jsonify(self._ca.delete_doc(ABTEST_DB, {"id": ABTEST_KEY}))


    def get_abtest(self):
        return jsonify(self._ca.get_doc(ABTEST_DB, ABTEST_KEY))

    def __init__(self, database = Database()):
        self._db = database
        self._ca = ConfigureApi(self._db)
        self._qe = QuestionnaireEngine(self._db)
        self._ui = UserInputHandler(self._qe)
        self._app = Flask(__name__)
        self._app.secret_key = os.environ["Q_APP_SECRET_KEY"]
        self._app.add_url_rule(f"/{API_VERSION}/{ABTESTS}/get", 'get_abtest', self.get_abtest)
        self._app.add_url_rule(f"/{API_VERSION}/{ABTESTS}/delete", 'delete_abtest', self.delete_abtest, methods=["POST"])
        self._app.add_url_rule(f"/{API_VERSION}/{ABTESTS}/update", 'create_abtest', self.create_abtest, methods=["POST"])
        self._app.add_url_rule(f"/{API_VERSION}/{QUESTIONNAIRES}/list", 'get_questionnaires_list', self.get_questionnaires_list)
        self._app.add_url_rule(f"/{API_VERSION}/{QUESTIONNAIRES}/get", 'get_questionnaire', self.get_questionnaire)
        self._app.add_url_rule(f"/{API_VERSION}/{QUESTIONNAIRES}/delete", 'delete_questionnaire', self.delete_questionnaire, methods=["POST"])
        self._app.add_url_rule(f"/{API_VERSION}/{QUESTIONNAIRES}/create", 'create_questionnaire', self.create_questionnaire, methods=["POST"])
        self._app.add_url_rule(f"/{API_VERSION}/{QUESTIONS}/list", 'get_question_list', self.get_question_list)
        self._app.add_url_rule(f"/{API_VERSION}/{QUESTIONS}/get", 'get_question', self.get_question)
        self._app.add_url_rule(f"/{API_VERSION}/{QUESTIONS}/create", 'create_question', self.create_question, methods=["POST"])
        self._app.add_url_rule(f"/{API_VERSION}/{QUESTIONS}/delete", 'delete_question', self.delete_question, methods=["POST"])
        self._app.add_url_rule(f"/", 'handle_questionnaire', self.handle_questionnaire, methods=["GET","POST"])

    def run(self):
        self._app.run(host="0.0.0.0")
