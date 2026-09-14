# forms/proveedor_form.py
# formulario del modulo de proveedores,con flask-wtf y wtforms

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class ProveedorForm(FlaskForm):
    nombre = StringField(
        'Nombre de la empresa',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=3, max=80, message='debe tener entre 3 y 80 caracteres.')
        ]
    )

    producto = SelectField(
        'Categoría que provee',
        choices=[
            ('', 'Seleccione una categoría'),
            ('Cocinas', 'Cocinas'),
            ('Refrigeración', 'Refrigeración'),
            ('Televisores', 'Televisores'),
            ('Lavado', 'Lavado')
        ],
        validators=[DataRequired(message='debe seleccionar una categoría.')]
    )

    telefono = StringField(
        'Teléfono',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=7, max=15, message='ingrese un teléfono válido.')
        ]
    )

    submit = SubmitField('Registrar Proveedor')
