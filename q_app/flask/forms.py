from flask_wtf import FlaskForm
from wtforms import RadioField, SelectMultipleField, SubmitField, TextField
from wtforms.validators import DataRequired

from q_app.engine.utils import get_field_var_name


def create_textform(qdef):
    class F(FlaskForm):
        pass

    setattr(F, "question", TextField(qdef["question"]))
    setattr(F, "submit", SubmitField("Next"))
    return F()


def create_multiselect(qdef):
    class F(FlaskForm):
        pass

    setattr(F, "question", RadioField(qdef["question"], choices=qdef["answer"]))
    setattr(F, "submit", SubmitField("Next"))
    return F()


def create_multiselect_choice(qdef):
    class F(FlaskForm):
        pass

    choices = [(x, x) for x in qdef["answer"]]
    setattr(
        F,
        "question",
        SelectMultipleField(
            qdef["question"], coerce=str, choices=choices, validators=[DataRequired()]
        ),
    )
    setattr(F, "submit", SubmitField("Next"))
    return F()


def create_multi_input(qdef):
    class F(FlaskForm):
        pass

    for input_field in qdef["input_fields"]:
        if input_field["type"] != "TEXT":
            continue

        var_name = get_field_var_name(input_field["text"])
        setattr(F, var_name, TextField(input_field["text"]))

    setattr(F, "submit", SubmitField("Next"))
    return F()


def create_final_submit(qdef):
    class F(FlaskForm):
        pass

    setattr(F, "submit", SubmitField("Submit"))
    setattr(F, "cancel", SubmitField("Cancel"))

    return F()


FORM_CREATE = {
    "TEXT": create_textform,
    "MULTI_SELECT": create_multiselect,
    "MULTI_SELECT_CHOICE": create_multiselect_choice,
    "MULTI_INPUT": create_multi_input,
    "FINAL_SUBMIT": create_final_submit,
}


class FormFactory:
    def create_form(form_type, question_definition):
        return FORM_CREATE[form_type](question_definition)
