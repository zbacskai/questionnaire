import pytest
import json
from unittest.mock import MagicMock
from q_app.app import QuestionnaireApp
from bson import ObjectId

class TestMongo():
    def __init__(self):
        self.update_one = MagicMock()
        self.find_one = MagicMock()
        self.delete_one = MagicMock()
        self.insert = MagicMock()

TEST_MONGO_DB_IMPL = TestMongo()

class TestDatabase:
    def __getitem__(self, key):
        return TEST_MONGO_DB_IMPL


TEST_DB = TestDatabase()


@pytest.fixture
def flask_app():
    return QuestionnaireApp(database=TEST_DB).test_client()

def test_create_abtest(flask_app):
    expected = {"status_code": 200}

    response = flask_app.post(
        '/0.1/abtests/update',
        data=json.dumps({
            "allocations": [
                {"questionnaire": "QUESTIONNAIRE-1-a", "percentage": 50},
                {"questionnaire": "QUESTIONNAIRE-1-b", "percentage": 50}
            ]}),
        content_type='application/json'
    )

    assert expected == json.loads(response.data)

def test_simple_question(flask_app):
    TEST_MONGO_DB_IMPL.find_one.side_effect = [
        {"allocations": [
            {"questionnaire": "QUESTIONNAIRE-1-a", "percentage": 100}]},
        { "id": "QUESTIONNAIRE-1-a",
          "start": "SIMPLE-QUESTION-1",
          "description": [
              {"qid": "SIMPLE-QUESTION-1",
               "next": ["MULTI_SELECT_QUESTION3"]}
            ]
        },
        {
            "_id": ObjectId('5fa27162b44ab4a90a781239'),
            "next_question": 'SUBMITTED',
            "questionnaire": 'QUESTIONNAIRE-1-a',
            "answers": [],
            "question_count": 1
        }
    ]

    TEST_MONGO_DB_IMPL.insert.side_effect = [
        ObjectId('000000000000000000000000')
    ]

    response = flask_app.get(
        '/',
    )
    assert b'<h1>Thank You!</h1>\n<p> Your answers have been recorded </p>' == response.data
