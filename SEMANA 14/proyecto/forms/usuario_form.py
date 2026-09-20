# forms/usuario_form.py
# formulario para registrar un nuevo usuario del sistema
# solo lo puede usar un usuario que ya inicio sesion (administrador)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class UsuarioForm(FlaskForm):
    usuario = StringField(
        'Nombre de usuario',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=4, max=50, message='debe tener entre 4 y 50 caracteres.')
        ]
    )

    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=6, message='la contraseña debe tener al menos 6 caracteres.')
        ]
    )

    confirmar_password = PasswordField(
        'Confirmar contraseña',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            EqualTo('password', message='las contraseñas no coinciden.')
        ]
    )

    submit = SubmitField('Registrar Usuario')
