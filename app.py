from flask import Flask
from flask import request
from questionnaire_engine import QuestionnaireEngine
from flask.json import jsonify

app = Flask(__name__)

API_VERSION='0.1'

QE = QuestionnaireEngine()

@app.route('/')
def hello():
    return "Hello World!"

@app.route(f'/{API_VERSION}/questions/create', methods=['POST'])
def create_question():
    print(str(request.json))
    status = QE.create_question(request.json)
    return jsonify({ 'status_code' : status })

@app.route(f'/{API_VERSION}/questions/delete', methods=['POST'])
def delete_question():
    print('Delete Question')

@app.route(f'/{API_VERSION}/questions/get')
def get_question():
    print(str(request.args))
    #print('Get Question')
    return jsonify({
        'status_code' : 200
    })

@app.route(f'/{API_VERSION}/questions/list')
def get_list():
    questionnaires = QE.list_all_questions()
    return jsonify({
        'status_code' : 200,
        'data' : questionnaires
    })

@app.route(f'/{API_VERSION}/questionnaires/create', methods=['POST'])
def create_questionnaire():
    print('Create Questionnaires')

@app.route(f'/{API_VERSION}/questionnaires/delete', methods=['POST'])
def delete_questionnaire():
    print('Delete Questionnaires')

@app.route(f'/{API_VERSION}/questionnaires/get')
def get_questionnaire():
    print('Get Questionnaires')

@app.route(f'/{API_VERSION}/abtest/create', methods=['POST'])
def create_abtest():
    print('Create A/B test')

@app.route(f'/{API_VERSION}/abtest/delete', methods=['POST'])
def delete_abtest():
    print('Delete A/B test')

@app.route(f'/{API_VERSION}/abtest/get')
def get_abtest():
    print('Get A/B test')


if __name__ == '__main__':
    app.run()
