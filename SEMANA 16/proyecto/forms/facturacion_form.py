# forms/facturacion_form.py
# la factura se arma con html/js normal (detalle con varios productos),
# esta clase vacia solo sirve para tener el token csrf en ese formulario
from flask_wtf import FlaskForm


class FacturaForm(FlaskForm):
    pass
