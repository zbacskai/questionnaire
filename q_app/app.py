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

app = Flask(__name__)

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

app.secret_key = os.environ["Q_APP_SECRET_KEY"]

def _get_title(question, session_id):
    if 'title' in question:
        return question

    question_count = QE.get_question_count(session_id)
    question['title'] = f'Question {question_count}'
    return question

def _handle_question(question, session_id):
    if question["type"] == QuestionTypes.QuestionnaireClosure:
        return render_template(FINAL_THANK_TEMPLATE)

    question = _get_title(question, session_id)
    form = FormFactory.create_form(question["type"], question["definition"])
    if form.validate_on_submit():
        return UI.store_answer_and_get_next(question, form, session_id)

    return render_template(QUESTION_TEMPLATE, form=form, title=question["title"])


# Rest API
@app.route("/", methods=["POST", "GET"])
def handle_questionnaire():
    if UUID not in session or not QE.session_is_valid(ObjectId(session[UUID])):
        session["uuid"] = str(QE.create_new_session())

    session_uuid = ObjectId(session[UUID])

    question = QE.get_question(session_uuid)
    return _handle_question(question, session_uuid)


@app.route(f"/{API_VERSION}/{QUESTIONS}/create", methods=["POST"])
def create_question():
    return jsonify(CA.create_doc(QUESTIONS_DB, request.json))


@app.route(f"/{API_VERSION}/{QUESTIONS}/delete", methods=["POST"])
def delete_question():
    return jsonify(CA.delete_doc(QUESTIONS_DB, request.json))


@app.route(f"/{API_VERSION}/{QUESTIONS}/get")
def get_question():
    if "name" not in request.args:
        status = {"status_code": 200, "error": 'variable "name" missing in query'}
    else:
        status = CA.get_doc(QUESTIONS_DB, request.args["name"])

    return jsonify(status)


@app.route(f"/{API_VERSION}/{QUESTIONS}/list")
def get_question_list():
    return jsonify(CA.list_all_docs(QUESTIONS_DB))


@app.route(f"/{API_VERSION}/{QUESTIONNAIRES}/create", methods=["POST"])
def create_questionnaire():
    return jsonify(CA.create_doc(QUESTIONNAIRES_DB, request.json))


@app.route(f"/{API_VERSION}/{QUESTIONNAIRES}/delete", methods=["POST"])
def delete_questionnaire():
    return jsonify(CA.delete_doc(QUESTIONNAIRES_DB, request.json))


@app.route(f"/{API_VERSION}/{QUESTIONNAIRES}/get")
def get_questionnaire():
    if "name" not in request.args:
        status = {"status_code": 200, "error": 'variable "name" missing in query'}
    else:
        status = CA.get_doc(QUESTIONNAIRES_DB, request.args["name"])

    return jsonify(status)


@app.route(f"/{API_VERSION}/{QUESTIONNAIRES}/list")
def get_questionnaires_list():
    status = CA.list_all_docs(QUESTIONNAIRES_DB)
    return jsonify(status)


@app.route(f"/{API_VERSION}/{ABTESTS}/update", methods=["POST"])
def create_abtest():
    request.json["id"] = ABTEST_KEY
    return jsonify(CA.create_doc(ABTEST_DB, request.json))


@app.route(f"/{API_VERSION}/{ABTESTS}/delete", methods=["POST"])
def delete_abtest():
    return jsonify(CA.delete_doc(ABTEST_DB, {"id": ABTEST_KEY}))


@app.route(f"/{API_VERSION}/{ABTESTS}/get")
def get_abtest():
    return jsonify(CA.get_doc(ABTEST_DB, ABTEST_KEY))
