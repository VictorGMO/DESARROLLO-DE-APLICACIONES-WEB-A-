# forms/cliente_form.py
# formulario del modulo de clientes,con flask-wtf y wtforms

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class ClienteForm(FlaskForm):
    nombre = StringField(
        'Nombre completo',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=3, max=80, message='debe tener entre 3 y 80 caracteres.')
        ]
    )

    correo = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Email(message='ingrese un correo electrónico válido.')
        ]
    )

    telefono = StringField(
        'Teléfono',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=7, max=15, message='ingrese un teléfono válido.')
        ]
    )

    submit = SubmitField('Registrar Cliente')
