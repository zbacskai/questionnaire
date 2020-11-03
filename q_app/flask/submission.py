from bson import ObjectId
from flask import Flask, redirect, render_template, request, session
from flask.json import jsonify
from flask_wtf import FlaskForm
from wtforms import (
    RadioField,
    SelectMultipleField,
    SubmitField,
    TextField,
)
from wtforms.validators import DataRequired

from q_app.engine.config_api import ConfigureApi
from q_app.engine.questionnaire import QuestionnaireEngine
from q_app.engine.database import Database
from q_app.flask.forms import FormFactory

from q_app.engine.utils import get_field_var_name
from q_app.engine.questionnaire import QE

def get_next_question_id(qdef, qtype, answer):
    if qtype != "MULTI_SELECT":
        return 0

    for index, stored_answer in enumerate(qdef["answer"]):
        if stored_answer == answer:
            return index

    return 0


def store_final_input(question, form, session_id):
    if form.submit.data:
        QE.set_form_submitted(session_id)
    else:
        QE.delete_form(session_id)

    return redirect("/")


def store_answer_multi_input(question, form, session_id):
    qdef = question["definition"]
    answer = {}
    answer["answer"] = {}
    for input_field in qdef["input_fields"]:
        var_name = get_field_var_name(input_field["text"])
        field = getattr(form, var_name)
        answer["answer"][input_field["text"]] = field.data

    QE.set_next_question(session_id, 0, answer)
    return redirect("/")


def store_answer_simple(question, form, session_id):
    qtype = question["type"]
    qdef = question["definition"]
    answer = {}
    answer["question"] = qdef["question"]
    answer["answer"] = form.question.data
    next_question_id = get_next_question_id(qdef, qtype, answer["answer"])
    QE.set_next_question(session_id, next_question_id, answer)
    return redirect("/")


def store_answer_and_get_next(question, form, session_id):
    qtype = question["type"]
    if qtype in ["TEXT", "MULTI_SELECT", "MULTI_SELECT_CHOICE"]:
        return store_answer_simple(question, form, session_id)

    if qtype == "MULTI_INPUT":
        return store_answer_multi_input(question, form, session_id)

    return store_final_input(question, form, session_id)
