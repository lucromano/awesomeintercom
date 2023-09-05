from wtforms import Form, StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email

class LoginForm(Form):
    email = StringField(validators=[InputRequired(), Length(min=1, max=50), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=1, max=40)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


class CreateForm(Form):
    submit = SubmitField('Create')