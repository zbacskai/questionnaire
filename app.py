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

from bson import ObjectId

app = Flask(__name__)

API_VERSION='0.1'

QE = QuestionnaireEngine()

QUESTIONS = 'questions'
QUESTIONNAIRES = 'questionnaires'
ABTESTS = 'abtests'

# TODO: Change this
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/l2'

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

def get_field_var_name(input_str):
    var_name = input_str
    var_name = var_name.lower()
    return var_name.replace(' ', '_')

def create_multi_input(qdef):
    class F(FlaskForm):
        pass

    for input_field in qdef['input_fields']:
        if input_field['type'] != 'TEXT':
            continue

        var_name = get_field_var_name(input_field['text'])
        setattr(F, var_name, TextField(input_field['text']))

    setattr(F, 'submit', SubmitField('Next'))
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

def store_final_input(question, form, session_id):
    if form.submit.data:
        QE.set_form_submitted(session_id)
    else:
        QE.delete_form(session_id)

    return redirect('/')

def store_answer_multi_input(question, form, session_id):
    qdef = question['definition']
    answer = {}
    answer['answer'] = {}
    for input_field in qdef['input_fields']:
        var_name = get_field_var_name(input_field['text'])
        field = getattr(form, var_name)
        answer['answer'][input_field['text']] = field.data

    QE.set_next_question(session_id, 0, answer)
    return redirect('/')


def store_answer_simple(question, form, session_id):
    qtype = question['type']
    qdef = question['definition']
    answer = {}
    answer['question'] = qdef['question']
    answer['answer'] = form.question.data
    next_question_id = get_next_question_id(qdef, qtype, answer['answer'])
    QE.set_next_question(session_id, next_question_id, answer)
    return redirect('/')

def store_answer_and_get_next(question, form, session_id):
    qtype = question['type']
    if qtype in ['TEXT', 'MULTI_SELECT', 'MULTI_SELECT_CHOICE']:
        return store_answer_simple(question, form, session_id)

    if qtype == 'MULTI_INPUT':
        return store_answer_multi_input(question, form, session_id)

    return store_final_input(question, form, session_id)

# Helper functions
def handle_question(question, session_id):
    if question['type'] == 'SUBMITTED':
        return render_template('thanks-for-submit.html')

    form = create_form(question)
    if form.validate_on_submit():
        return store_answer_and_get_next(question, form, session_id)

    return render_template('question-step.html', form=form)

# Rest API
@app.route('/', methods=['POST', 'GET'])
def handle_questionnaire():
    if 'uuid' not in session or not QE.session_is_valid(ObjectId(session['uuid'])):
        session['uuid'] = str(QE.create_new_session())

    session_uuid = ObjectId(session['uuid'])

    question = QE.get_next_question(session_uuid)
    return handle_question(question, session_uuid)

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

@app.route(f'/{API_VERSION}/{ABTESTS}/update', methods=['POST'])
def create_abtest():
    request.json['id'] = 'testconfig'
    status = QE.create_doc('configuration', request.json)
    return jsonify(status)

@app.route(f'/{API_VERSION}/{ABTESTS}/delete', methods=['POST'])
def delete_abtest():
    status = QE.delete_doc('configuration', {'id' : 'testconfig'})
    return jsonify(status)

@app.route(f'/{API_VERSION}/{ABTESTS}/get')
def get_abtest():
    status = QE.get_doc('configuration', 'testconfig')

    return jsonify(status)

if __name__ == '__main__':
    app.run()
