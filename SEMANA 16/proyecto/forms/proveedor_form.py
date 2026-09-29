# forms/proveedor_form.py
# formulario del modulo de proveedores,con flask-wtf y wtforms
# se usa tanto para registrar como para editar un proveedor

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp


class ProveedorForm(FlaskForm):
    nombre = StringField(
        'Nombre de la empresa',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=3, max=80, message='debe tener entre 3 y 80 caracteres.')
        ],
        render_kw={'placeholder': 'Ej: Indurama'}
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
            Regexp(r'^0\d{8,9}$', message='ingrese un teléfono válido. Ej: 072805000.')
        ],
        render_kw={'placeholder': 'Ej: 072805000'}
    )

    correo = StringField(
        'Correo (opcional)',
        validators=[Optional(), Email(message='ingrese un correo electrónico válido.')],
        render_kw={'placeholder': 'ventas@empresa.com'}
    )

    direccion = StringField(
        'Dirección (opcional)',
        validators=[Optional(), Length(max=200)],
        render_kw={'placeholder': 'Ej: Av. Amazonas y Colón, Cuenca'}
    )

    submit = SubmitField('Guardar Proveedor')
