from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, MultipleFileField, SelectField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Length, Email, Optional, DataRequired



class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=1, max=50), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=1, max=40)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")