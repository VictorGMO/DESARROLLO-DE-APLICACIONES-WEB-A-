# forms/facturacion_form.py
# formulario del modulo de facturacion,con flask-wtf y wtforms

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class FacturacionForm(FlaskForm):
    cliente = StringField(
        'Nombre del cliente',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=3, max=80, message='debe tener entre 3 y 80 caracteres.')
        ]
    )

    total = FloatField(
        'Total de la factura',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            NumberRange(min=0.01, message='el total debe ser mayor a 0.')
        ]
    )

    estado = SelectField(
        'Estado',
        choices=[
            ('', 'Seleccione un estado'),
            ('Pagada', 'Pagada'),
            ('Pendiente', 'Pendiente')
        ],
        validators=[DataRequired(message='debe seleccionar un estado.')]
    )

    submit = SubmitField('Registrar Factura')
