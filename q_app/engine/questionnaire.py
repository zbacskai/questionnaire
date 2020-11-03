from random import choices
from q_app.engine.database import DB

class QuestionnaireEngine:
    def __init__(self, db_client):
        self._db = db_client

    def session_is_valid(self, session_id):
        return self._db["sessions"].find_one({"_id": session_id}) is not None

    def get_questionnaire_based_on_experiment(self):
        abtest_data = self._db["configuration"].find_one({"_id": "testconfig"})
        tuple_list = [
            (alloc_def["questionnaire"], alloc_def["percentage"])
            for alloc_def in abtest_data["allocations"]
        ]
        choice_input = list(zip(*tuple_list))
        return choices(choice_input[0], choice_input[1])[0]

    def delete_form(self, session_id):
        self._db["sessions"].delete_one({"_id": session_id})

    def set_form_submitted(self, session_id):
        self._db["sessions"].update_one(
            {"_id": session_id}, {"$set": {"next_question": "SUBMITTED"}}
        )

    def set_next_question(self, session_id, choice_index, answer):
        session_data = self._db["sessions"].find_one({"_id": session_id})
        questionnaire = self._db["questionnaires"].find_one(
            {"_id": session_data["questionnaire"]}
        )
        for qdata in questionnaire["description"]:
            if qdata["qid"] == session_data["next_question"]:
                next_question = qdata["next"][choice_index]

        self._db["sessions"].update_one(
            {"_id": session_id},
            {"$set":
             {"next_question": next_question}, "$push": {"answers": answer}}
        )

    def create_new_session(self):
        qname = self.get_questionnaire_based_on_experiment()
        qdata = self._db["questionnaires"].find_one({"_id": qname})
        first_question = qdata["start"]
        session_id = self._db["sessions"].insert(
            {"next_question": first_question,
             "questionnaire": qname, "answers": []}
        )
        print(str(session_id))
        self._db["sessions"].update_one(
            {"_id": session_id},
            {"$currentDate": {"created": {"$type": "date"}}}
        )

        return session_id

    def get_question(self, session_id):
        qdata = self._db["sessions"].find_one({"_id": session_id})
        if qdata["next_question"] == "SUBMITTED":
            return {"type": "SUBMITTED"}

        return self._db["questions"].find_one({"_id": qdata["next_question"]})

QE = QuestionnaireEngine(DB)
