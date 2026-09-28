# forms/producto_form.py
# formulario del modulo de productos,con flask-wtf y wtforms
# esta misma clase se reutiliza para registrar Y para editar un producto

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
            ('Cocinas', 'Cocinas'),
            ('Refrigeración', 'Refrigeración'),
            ('Televisores', 'Televisores'),
            ('Lavado', 'Lavado'),
            ('Cocina', 'Electrodomésticos de cocina'),
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

    # este campo representa la relacion (clave foranea) con la tabla proveedores
    # las choices se llenan dinamicamente desde app.py,consultando la tabla proveedores
    # el valor 0 significa "sin proveedor asignado" (id_proveedor queda NULL en la base)
    id_proveedor = SelectField(
        'Proveedor',
        coerce=int,
        choices=[]
    )

    submit = SubmitField('Guardar Producto')
