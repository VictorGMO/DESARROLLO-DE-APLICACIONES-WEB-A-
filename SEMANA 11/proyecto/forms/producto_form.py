# forms/producto_form.py
# formulario del modulo de productos,con flask-wtf y wtforms
# esta misma clase se podria reutilizar despues para editar un producto

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ProductoForm(FlaskForm):
    nombre = StringField(
        'Nombre del Producto',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=3, max=80, message='debe tener entre 3 y 80 caracteres.')
        ]
    )

    descripcion = TextAreaField(
        'Descripción',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=10, message='la descripción debe tener al menos 10 caracteres.')
        ]
    )

    categoria = SelectField(
        'Categoría',
        choices=[
            ('', 'Seleccione una categoría'),
            ('Electrónica', 'Electrónica'),
            ('Oficina', 'Oficina'),
            ('Hogar', 'Hogar'),
            ('Otros', 'Otros')
        ],
        validators=[DataRequired(message='debe seleccionar una categoría.')]
    )

    stock = IntegerField(
        'Stock disponible',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            NumberRange(min=0, message='el stock no puede ser negativo.')
        ]
    )

    submit = SubmitField('Registrar Producto')
