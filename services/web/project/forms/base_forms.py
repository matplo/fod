from flask_wtf import FlaskForm
from wtforms import Form, FileField, StringField, PasswordField, SubmitField, validators


def file_required(form, field):
    if not field.data or not field.data.filename:
        raise validators.ValidationError("File is required")


def file_allowed(form, field):
    if field.data and field.data.filename:
        ext = field.data.filename.split(".")[-1].lower()
        if ext not in ["jpg", "png", 'txt', 'yaml', 'yml', 'pdf']:
            raise validators.ValidationError("Only jpg and png files are allowed")


class MyForm(FlaskForm):
    text = StringField("Query", validators=[validators.DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[validators.DataRequired()])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    submit = SubmitField("Log In")


class UploadForm(FlaskForm):
    file = FileField("File", validators=[file_required, file_allowed])
    submit = SubmitField("Submit")
