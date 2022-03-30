from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, DateField
from wtforms.validators import DataRequired


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
    start_date = DateField("Start Date", format='%Y-%m-%d')
    due_date = DateField("Due Date", format='%Y-%m-%d')
    status = StringField("Status")
    assigned_to = StringField("Assigned To")
    submit = SubmitField("Save")


class AddMember(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired()])
    submit = SubmitField("Add Member")