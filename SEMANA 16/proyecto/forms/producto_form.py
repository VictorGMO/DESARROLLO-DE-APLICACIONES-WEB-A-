# forms/producto_form.py
# formulario del modulo de productos,con flask-wtf y wtforms
# se usa tanto para registrar como para editar un producto

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange


class ProductoForm(FlaskForm):
    nombre = StringField(
        'Nombre del Producto',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=3, max=80, message='debe tener entre 3 y 80 caracteres.')
        ],
        render_kw={'placeholder': 'Ej: Cocina a gas 4 hornillas'}
    )

    descripcion = TextAreaField(
        'Descripción',
        validators=[
            DataRequired(message='este campo es obligatorio.'),
            Length(min=10, message='la descripción debe tener al menos 10 caracteres.')
        ],
        render_kw={'placeholder': 'Detalles del producto...'}
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

    precio = FloatField(
        'Precio ($)',
        validators=[
            InputRequired(message='ingrese un número válido.'),
            NumberRange(min=0.01, message='el precio debe ser mayor a 0.')
        ],
        render_kw={'placeholder': 'Ej: 125.50', 'step': '0.01', 'min': '0.01'}
    )

    stock = IntegerField(
        'Stock disponible',
        validators=[
            InputRequired(message='ingrese un número válido.'),
            NumberRange(min=0, message='el stock no puede ser negativo.')
        ],
        render_kw={'placeholder': 'Ej: 10', 'min': '0'}
    )

    # relacion (clave foranea) con la tabla proveedores,las choices se llenan desde app.py
    id_proveedor = SelectField(
        'Proveedor',
        coerce=int,
        choices=[]
    )

    submit = SubmitField('Guardar Producto')
