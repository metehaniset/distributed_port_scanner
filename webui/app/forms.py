from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class StartScanForm(FlaskForm):
    # scanner = StringField('Scanner', 'validators=[DataRequired()])
    ip = StringField('IP', validators=[DataRequired()])
    port = StringField('Port', validators=[DataRequired()])
    params = StringField('Params')
    submit = SubmitField('Submit')

