import os

from bson import ObjectId
from flask import Flask, render_template, request, session
from flask.json import jsonify

from q_app.engine.config_api import ConfigureApi
from q_app.engine.database import Database
from q_app.engine.questionnaire import QuestionnaireEngine
from q_app.flask.forms import FormFactory
from q_app.flask.submission import UserInputHandler

app = Flask(__name__)

API_VERSION = "0.1"

QUESTIONS = "questions"
QUESTIONNAIRES = "questionnaires"
ABTESTS = "abtests"
ABTEST_DB = "configuration"
ABTEST_KEY = "testconfig"

DB = Database()
CA = ConfigureApi(DB)
QE = QuestionnaireEngine(DB)
UI = UserInputHandler(QE)

# TODO: Change this
app.secret_key = os.environ["Q_APP_SECRET_KEY"]


def _handle_question(question, session_id):
    if question["type"] == "SUBMITTED":
        return render_template("thanks-for-submit.html")

    form = FormFactory.create_form(question["type"], question["definition"])
    if form.validate_on_submit():
        return UI.store_answer_and_get_next(question, form, session_id)

    return render_template("question-step.html", form=form)


# Rest API
@app.route("/", methods=["POST", "GET"])
def handle_questionnaire():
    if "uuid" not in session or not QE.session_is_valid(ObjectId(session["uuid"])):
        session["uuid"] = str(QE.create_new_session())

    session_uuid = ObjectId(session["uuid"])

    question = QE.get_question(session_uuid)
    return _handle_question(question, session_uuid)


@app.route(f"/{API_VERSION}/{QUESTIONS}/create", methods=["POST"])
def create_question():
    return jsonify(CA.create_doc(QUESTIONS, request.json))


@app.route(f"/{API_VERSION}/{QUESTIONS}/delete", methods=["POST"])
def delete_question():
    return jsonify(CA.delete_doc(QUESTIONS, request.json))


@app.route(f"/{API_VERSION}/{QUESTIONS}/get")
def get_question():
    if "name" not in request.args:
        status = {"status_code": 200, "error": 'variable "name" missing in query'}
    else:
        status = CA.get_doc(QUESTIONS, request.args["name"])

    return jsonify(status)


@app.route(f"/{API_VERSION}/{QUESTIONS}/list")
def get_question_list():
    return jsonify(CA.list_all_docs(QUESTIONS))


@app.route(f"/{API_VERSION}/{QUESTIONNAIRES}/create", methods=["POST"])
def create_questionnaire():
    return jsonify(CA.create_doc(QUESTIONNAIRES, request.json))


@app.route(f"/{API_VERSION}/{QUESTIONNAIRES}/delete", methods=["POST"])
def delete_questionnaire():
    return jsonify(CA.delete_doc(QUESTIONNAIRES, request.json))


@app.route(f"/{API_VERSION}/{QUESTIONNAIRES}/get")
def get_questionnaire():
    if "name" not in request.args:
        status = {"status_code": 200, "error": 'variable "name" missing in query'}
    else:
        status = CA.get_doc(QUESTIONNAIRES, request.args["name"])

    return jsonify(status)


@app.route(f"/{API_VERSION}/{QUESTIONNAIRES}/list")
def get_questionnaires_list():
    status = CA.list_all_docs(QUESTIONNAIRES)
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
