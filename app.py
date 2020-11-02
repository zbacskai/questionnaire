from flask import Flask
from flask import request
from flask import session
from questionnaire_engine import QuestionnaireEngine
from flask.json import jsonify

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField
from wtforms.validators import DataRequired

from flask import render_template
from flask import redirect

import uuid

app = Flask(__name__)

API_VERSION='0.1'

QE = QuestionnaireEngine()

QUESTIONS = 'questions'
QUESTIONNAIRES = 'questionnaires'
ABTESTS = 'abtests'

# TODO: Change this
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/f'

# Helper functions
def render_question(question, session_id):
    print(str(question))
    qtype = question['type']
    if qtype != 'TEXT':
        return f"Hello World! Your id: {session['uuid']}"

    class F(FlaskForm):
        pass

    qdef = question['definition']
    setattr(F, 'question', TextField(qdef['question']))
    setattr(F, 'submit', SubmitField('Next'))
    form = F()

    if form.validate_on_submit():
        answer = {}
        answer['question'] = qdef['question']
        answer['answer'] = form.question.data
        QE.set_next_question(session_id, 0, answer)
        return redirect('/')

    return render_template('simple-text-question.html', form=form)

# Rest API
@app.route('/', methods=['POST', 'GET'])
def start_questionnaire():
    if 'uuid' not in session:
        session['uuid'] = uuid.uuid4()

    #Create a new session. only if needed
    QE.create_new_session(session['uuid'])
    question = QE.get_next_question(session['uuid'])
    return render_question(question, session['uuid'])

@app.route(f'/{API_VERSION}/{QUESTIONS}/create', methods=['POST'])
def create_question():
    status = QE.create_doc(QUESTIONS, request.json)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{QUESTIONS}/delete', methods=['POST'])
def delete_question():
    status = QE.delete_doc(QUESTIONS, request.json)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{QUESTIONS}/get')
def get_question():
    if 'name' not in request.args:
        status = { 'status_code' : 200, 'error' : 'variable "name" missing in query' }
    else:
        status = QE.get_doc(QUESTIONS, request.args['name'])

    return jsonify(status)

@app.route(f'/{API_VERSION}/{QUESTIONS}/list')
def get_question_list():
    status = QE.list_all_docs(QUESTIONS)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{QUESTIONNAIRES}/create', methods=['POST'])
def create_questionnaire():
    status = QE.create_doc(QUESTIONNAIRES, request.json)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{QUESTIONNAIRES}/delete', methods=['POST'])
def delete_questionnaire():
    status = QE.delete_doc(QUESTIONNAIRES, request.json)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{QUESTIONNAIRES}/get')
def get_questionnaire():
    if 'name' not in request.args:
        status = { 'status_code' : 200, 'error' : 'variable "name" missing in query' }
    else:
        status = QE.get_doc(QUESTIONNAIRES, request.args['name'])

    return jsonify(status)

@app.route(f'/{API_VERSION}/{QUESTIONNAIRES}/list')
def get_questionnaires_list():
    status = QE.list_all_docs(QUESTIONNAIRES)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{ABTESTS}/create', methods=['POST'])
def create_abtest():
    status = QE.create_doc(ABTESTS, request.json)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{ABTESTS}/delete', methods=['POST'])
def delete_abtest():
    status = QE.delete_doc(ABTESTS, request.json)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{ABTESTS}/get')
def get_abtest():
    if 'name' not in request.args:
        status = { 'status_code' : 200, 'error' : 'variable "name" missing in query' }
    else:
        status = QE.get_doc(ABTESTS, request.args['name'])

    return jsonify(status)

@app.route(f'/{API_VERSION}/{ABTESTS}/list')
def get_abtest_list():
    status = QE.list_all_docs(ABTESTS)
    return jsonify(status)


if __name__ == '__main__':
    app.run()
