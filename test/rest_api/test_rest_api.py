import pytest
import json
from unittest.mock import Mock
from q_app.app import QuestionnaireApp


class TestMongoDBImpl():
    def __init__(self):
        pass

    def update_one(self, key, value, upsert):
        return {}


TEST_MONGO_DB_IMPL = TestMongoDBImpl()

class TestDatabase:
    def __getitem__(self, key):
        return TEST_MONGO_DB_IMPL


TEST_DB = TestDatabase()


@pytest.fixture
def flask_app():
    return QuestionnaireApp(database=TEST_DB).test_client()

@pytest.fixture
def mocker():
    return Mock()


def test_create_abtest(flask_app, mocker):
    expected = {"status_code": 200}

    sv_mock = mocker.patch(TEST_MONGO_DB_IMPL.update_one)
    sv_mock.return_value.get_metrics.return_value = {}

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