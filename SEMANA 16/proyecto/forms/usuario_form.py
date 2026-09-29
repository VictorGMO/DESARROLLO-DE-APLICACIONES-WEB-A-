# forms/usuario_form.py
# formulario para registrar un nuevo usuario del sistema
# solo lo puede usar un administrador ya logueado

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class UsuarioForm(FlaskForm):
    nombre = StringField(
        'Nombre completo',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=3, max=100, message='debe tener entre 3 y 100 caracteres.')
        ]
    )

    usuario = StringField(
        'Nombre de usuario (para iniciar sesión)',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=4, max=50, message='debe tener entre 4 y 50 caracteres.')
        ]
    )

    rol = SelectField(
        'Rol',
        choices=[('vendedor', 'Vendedor'), ('administrador', 'Administrador')],
        validators=[DataRequired(message='debe seleccionar un rol.')]
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


class CambiarPasswordForm(FlaskForm):
    password_actual = PasswordField(
        'Contraseña actual',
        validators=[DataRequired(message='este campo es obligatorio.')]
    )

    password_nueva = PasswordField(
        'Nueva contraseña',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=6, message='la contraseña debe tener al menos 6 caracteres.')
        ]
    )

    confirmar_password_nueva = PasswordField(
        'Confirmar nueva contraseña',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            EqualTo('password_nueva', message='las contraseñas no coinciden.')
        ]
    )

    submit = SubmitField('Cambiar Contraseña')
