# forms/cliente_form.py
# formulario del modulo de clientes,con flask-wtf y wtforms
# se usa tanto para registrar como para editar un cliente

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp


class ClienteForm(FlaskForm):
    nombre = StringField(
        'Nombre completo',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=3, max=80, message='debe tener entre 3 y 80 caracteres.')
        ],
        render_kw={'placeholder': 'Ej: Juan Pérez'}
    )

    correo = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Email(message='ingrese un correo electrónico válido.')
        ],
        render_kw={'placeholder': 'ejemplo@correo.com'}
    )

    telefono = StringField(
        'Teléfono',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Regexp(r'^0\d{9}$', message='ingrese un teléfono válido de 10 dígitos,empezando con 0. Ej: 0991234567.')
        ],
        render_kw={'placeholder': 'Ej: 0991234567'}
    )

    cedula = StringField(
        'Cédula o RUC',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Regexp(r'^\d{10}(\d{3})?$', message='ingrese una cédula (10 dígitos) o RUC (13 dígitos) válido.')
        ],
        render_kw={'placeholder': 'Ej: 1712345678'}
    )

    direccion = StringField(
        'Dirección',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=5, max=200, message='debe tener entre 5 y 200 caracteres.')
        ],
        render_kw={'placeholder': 'Ej: Av. 6 de Diciembre y Colón'}
    )

    submit = SubmitField('Guardar Cliente')
