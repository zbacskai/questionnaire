from flask import Flask
from flask import request
from flask import session
from questionnaire_engine import QuestionnaireEngine
from flask.json import jsonify

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, RadioField, SelectMultipleField
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
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/j'

def create_textform(qdef):
    class F(FlaskForm):
        pass

    setattr(F, 'question', TextField(qdef['question']))
    setattr(F, 'submit', SubmitField('Next'))
    return F()

def create_multiselect(qdef):
    class F(FlaskForm):
        pass

    setattr(F, 'question', RadioField(qdef['question'], choices=qdef['answer']))
    setattr(F, 'submit', SubmitField('Next'))
    return F()

def create_multiselect_choice(qdef):
    class F(FlaskForm):
        pass

    choices = [ (x, x) for x in qdef['answer']  ]
    setattr(F, 'question',
            SelectMultipleField(qdef['question'], coerce=str,
            choices=choices, validators=[DataRequired()]))
    setattr(F, 'submit', SubmitField('Next'))
    return F()

def create_multi_input(qdef):
    class F(FlaskForm):
        pass

    return F()

def create_final_submit(qdef):
    class F(FlaskForm):
        pass

    setattr(F, 'submit', SubmitField('Submit'))
    setattr(F, 'cancel', SubmitField('Cancel'))

    return F()

FORM_CREATE = {
    'TEXT' : create_textform,
    'MULTI_SELECT' : create_multiselect,
    'MULTI_SELECT_CHOICE' : create_multiselect_choice,
    'MULTI_INPUT' : create_multi_input,
    'FINAL_SUBMIT' : create_final_submit
}

def create_form(question):
    qtype = question['type']
    if qtype not in FORM_CREATE:
        return f"Hello World! Your id: {session['uuid']}"

    qdef = question['definition']

    return FORM_CREATE[qtype](qdef)

def get_next_question_id(qdef, qtype, answer):
    if qtype != 'MULTI_SELECT':
        return 0

    for index, stored_answer in enumerate(qdef['answer']):
        if stored_answer == answer:
            return index

    return 0

# Helper functions
def handle_question(question, session_id):
    form = create_form(question)
    if isinstance(form, str):
        return form

    if form.validate_on_submit():
        qtype = question['type']
        qdef = question['definition']
        answer = {}
        answer['question'] = qdef['question']
        answer['answer'] = form.question.data
        next_question_id = get_next_question_id(qdef, qtype, answer['answer'])
        QE.set_next_question(session_id, next_question_id, answer)
        return redirect('/')

    return render_template('question-step.html', form=form)

# Rest API
@app.route('/', methods=['POST', 'GET'])
def start_questionnaire():
    if 'uuid' not in session:
        session['uuid'] = uuid.uuid4()

    #Create a new session. only if needed
    QE.create_new_session(session['uuid'])
    question = QE.get_next_question(session['uuid'])
    return handle_question(question, session['uuid'])

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
