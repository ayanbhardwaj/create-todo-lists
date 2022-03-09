from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm
class CreateList(FlaskForm):
    title = StringField("New Work List Title", validators=[DataRequired()])
    submit = SubmitField("Create New Work List")


# register wtf form
class RegisterForm(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    name = StringField(label="Name", validators=[DataRequired()])
    submit = SubmitField(label="SIGN ME UP")


# login wtf form
class LoginForm(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="LOG IN")


# Task Form
class TaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    start_date = StringField("Start Date")
    due_date = StringField("Due Date")
    status = StringField("Status")
    assigned_to = StringField("Assigned To")
    submit = SubmitField("Save")


class AddMember(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired()])
    submit = SubmitField("Add Member")