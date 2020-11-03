from flask import redirect

from q_app.engine.utils import get_field_var_name


def get_next_question_id(qdef, qtype, answer):
    if qtype != "MULTI_SELECT":
        return 0

    for index, stored_answer in enumerate(qdef["answer"]):
        if stored_answer == answer:
            return index

    return 0


class UserInputHandler:
    def __init__(self, questionnaire_engine):
        self._qe = questionnaire_engine

    def _store_final_input(self, question, form, session_id):
        if form.submit.data:
            self._qe.set_form_submitted(session_id)
        else:
            self._qe.delete_form(session_id)

        return redirect("/")

    def _store_answer_multi_input(self, question, form, session_id):
        qdef = question["definition"]
        answer = {}
        answer["answer"] = {}
        for input_field in qdef["input_fields"]:
            var_name = get_field_var_name(input_field["text"])
            field = getattr(form, var_name)
            answer["answer"][input_field["text"]] = field.data

        self._qe.set_next_question(session_id, 0, answer)
        return redirect("/")

    def _store_answer_simple(self, question, form, session_id):
        qtype = question["type"]
        qdef = question["definition"]
        answer = {}
        answer["question"] = qdef["question"]
        answer["answer"] = form.question.data
        next_question_id = get_next_question_id(qdef, qtype, answer["answer"])
        self._qe.set_next_question(session_id, next_question_id, answer)
        return redirect("/")

    def store_answer_and_get_next(self, question, form, session_id):
        qtype = question["type"]
        if qtype in ["TEXT", "MULTI_SELECT", "MULTI_SELECT_CHOICE"]:
            return self._store_answer_simple(question, form, session_id)

        if qtype == "MULTI_INPUT":
            return self._store_answer_multi_input(question, form, session_id)

        return self._store_final_input(question, form, session_id)
