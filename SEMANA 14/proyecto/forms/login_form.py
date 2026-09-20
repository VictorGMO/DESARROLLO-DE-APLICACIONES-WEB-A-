# forms/login_form.py
# formulario de inicio de sesion,con flask-wtf y wtforms

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    usuario = StringField(
        'Usuario',
        validators=[DataRequired(message='este campo es obligatorio.')]
    )

    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(message='este campo es obligatorio.')]
    )

    submit = SubmitField('Iniciar Sesión')
