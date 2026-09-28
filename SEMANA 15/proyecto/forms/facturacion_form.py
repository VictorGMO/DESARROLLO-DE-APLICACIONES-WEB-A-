# forms/facturacion_form.py
# formulario del modulo de facturacion,con flask-wtf y wtforms
# se usa tanto para registrar como para editar una factura

from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class FacturacionForm(FlaskForm):
    # relacion (clave foranea) con la tabla clientes
    # las opciones se llenan desde app.py consultando la tabla clientes
    id_cliente = SelectField(
        'Cliente',
        coerce=int,
        choices=[],
        validators=[NumberRange(min=1, message='debe seleccionar un cliente.')]
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

    submit = SubmitField('Guardar Factura')
