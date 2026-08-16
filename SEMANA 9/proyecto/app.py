# app.py
# aca configuramos flask y las rutas del proyecto integrador
# cada modulo (productos,clientes,proveedores,facturacion) tiene su propia ruta
# por ahora los datos son de ejemplo,estaticos,todavia no hay base de datos

from flask import Flask, render_template

app = Flask(__name__)

# ruta principal,muestra la pagina informativa del proyecto (la del semana 6-8)
@app.route('/')
def index():
    return render_template('index.html')

# ruta del modulo productos,usa la misma logica de formulario y modal de semanas anteriores
@app.route('/productos')
def productos():
    productos = [
        {'id': 1, 'nombre': 'Laptop HP', 'descripcion': 'Laptop para oficina con 8GB RAM', 'categoria': 'Electronica'},
        {'id': 2, 'nombre': 'Silla ergonomica', 'descripcion': 'Silla para oficina con soporte lumbar', 'categoria': 'Oficina'},
        {'id': 3, 'nombre': 'Lampara LED', 'descripcion': 'Lampara de escritorio ajustable', 'categoria': 'Hogar'}
    ]
    return render_template('productos.html', productos=productos)

# ruta del modulo clientes,datos de ejemplo nomas,todavia no hay bd
@app.route('/clientes')
def clientes():
    clientes = [
        {'id': 1, 'nombre': 'Juan Perez', 'correo': 'juan.perez@example.com', 'telefono': '099 123 4567'},
        {'id': 2, 'nombre': 'Maria Lopez', 'correo': 'maria.lopez@example.com', 'telefono': '098 765 4321'},
        {'id': 3, 'nombre': 'Carlos Mera', 'correo': 'carlos.mera@example.com', 'telefono': '096 541 2378'}
    ]
    return render_template('clientes.html', clientes=clientes)

# ruta del modulo proveedores,datos de ejemplo
@app.route('/proveedores')
def proveedores():
    proveedores = [
        {'id': 1, 'nombre': 'Distribuidora Andina', 'producto': 'Electronica', 'telefono': '02 234 5678'},
        {'id': 2, 'nombre': 'Muebles del Pacifico', 'producto': 'Oficina', 'telefono': '02 456 7891'},
        {'id': 3, 'nombre': 'Iluminacion Total', 'producto': 'Hogar', 'telefono': '02 345 6789'}
    ]
    return render_template('proveedores.html', proveedores=proveedores)

# ruta del modulo facturacion,datos de ejemplo
@app.route('/facturacion')
def facturacion():
    facturas = [
        {'id': 1001, 'cliente': 'Juan Perez', 'total': 350.50, 'estado': 'Pagada'},
        {'id': 1002, 'cliente': 'Maria Lopez', 'total': 120.00, 'estado': 'Pendiente'},
        {'id': 1003, 'cliente': 'Carlos Mera', 'total': 89.99, 'estado': 'Pagada'}
    ]
    return render_template('facturacion.html', facturas=facturas)

if __name__ == '__main__':
    app.run(debug=True)
