# app.py
# aca configuramos flask y las rutas del proyecto integrador
# cada modulo (productos,clientes,proveedores,facturacion) tiene su propia ruta
# desde la semana 11 se usan formularios con flask-wtf,validados en el servidor
# por ahora los datos son de ejemplo,estaticos,todavia no hay base de datos

from flask import Flask, render_template, redirect, url_for

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

app = Flask(__name__)

# secret_key necesaria para que funcione la proteccion csrf de flask-wtf
# en un proyecto real esto no se deja escrito asi en el codigo,se pone en una variable de entorno
app.config['SECRET_KEY'] = 'clave-secreta-proyecto-integrador-uea-2026'

# ============================================
# DATOS EN MEMORIA
# estas listas viven mientras la app este corriendo,se reinician
# si se reinicia el servidor. no hay base de datos todavia
# ============================================

productos_data = [
    {'id': 1, 'nombre': 'Laptop HP', 'descripcion': 'Laptop para oficina con 8GB RAM', 'categoria': 'Electronica', 'stock': 8},
    {'id': 2, 'nombre': 'Silla ergonomica', 'descripcion': 'Silla para oficina con soporte lumbar', 'categoria': 'Oficina', 'stock': 3},
    {'id': 3, 'nombre': 'Lampara LED', 'descripcion': 'Lampara de escritorio ajustable', 'categoria': 'Hogar', 'stock': 0}
]

clientes_data = [
    {'id': 1, 'nombre': 'Juan Perez', 'correo': 'juan.perez@example.com', 'telefono': '099 123 4567'},
    {'id': 2, 'nombre': 'Maria Lopez', 'correo': 'maria.lopez@example.com', 'telefono': '098 765 4321'},
    {'id': 3, 'nombre': 'Carlos Mera', 'correo': 'carlos.mera@example.com', 'telefono': '096 541 2378'}
]

proveedores_data = [
    {'id': 1, 'nombre': 'Distribuidora Andina', 'producto': 'Electronica', 'telefono': '02 234 5678'},
    {'id': 2, 'nombre': 'Muebles del Pacifico', 'producto': 'Oficina', 'telefono': '02 456 7891'},
    {'id': 3, 'nombre': 'Iluminacion Total', 'producto': 'Hogar', 'telefono': '02 345 6789'}
]

facturas = [
    {'id': 1001, 'cliente': 'Juan Perez', 'total': 350.50, 'estado': 'Pagada'},
    {'id': 1002, 'cliente': 'Maria Lopez', 'total': 120.00, 'estado': 'Pendiente'},
    {'id': 1003, 'cliente': 'Carlos Mera', 'total': 89.99, 'estado': 'Pagada'}
]


# ============================================
# RUTA PRINCIPAL
# ============================================

# ruta principal,muestra la pagina informativa del proyecto (la del semana 6-8)
# nombre_sistema es una variable simple,estadisticas es un diccionario con info general
@app.route('/')
def index():
    nombre_sistema = 'Sistema de Gestión de Inventario'

    # ahora estadisticas se calcula con len(),asi que si se registra algo nuevo
    # con los formularios de flask-wtf,estos numeros si cambian
    estadisticas = {
        'total_productos': len(productos_data),
        'total_clientes': len(clientes_data),
        'total_proveedores': len(proveedores_data)
    }

    return render_template('index.html', nombre_sistema=nombre_sistema, estadisticas=estadisticas)


# ============================================
# MODULO PRODUCTOS
# ============================================

@app.route('/productos')
def productos():
    return render_template('productos.html', productos=productos_data)


# ruta con formulario de flask-wtf,acepta GET (mostrar el formulario) y POST (procesar los datos)
@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    form = ProductoForm()

    # validate_on_submit() revisa que sea POST y que pasen todos los validadores
    if form.validate_on_submit():
        nuevo = {
            'id': len(productos_data) + 1,
            'nombre': form.nombre.data,
            'descripcion': form.descripcion.data,
            'categoria': form.categoria.data,
            'stock': form.stock.data
        }
        productos_data.append(nuevo)
        return redirect(url_for('productos'))

    return render_template('formulario_producto.html', form=form)


# ruta para eliminar un producto por su id,solo acepta post,se llama desde un boton en productos.html
@app.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    global productos_data
    productos_data = [p for p in productos_data if p['id'] != producto_id]
    return redirect(url_for('productos'))


# ============================================
# MODULO CLIENTES
# ============================================

@app.route('/clientes')
def clientes():
    return render_template('clientes.html', clientes=clientes_data)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        nuevo = {
            'id': len(clientes_data) + 1,
            'nombre': form.nombre.data,
            'correo': form.correo.data,
            'telefono': form.telefono.data
        }
        clientes_data.append(nuevo)
        return redirect(url_for('clientes'))

    return render_template('formulario_cliente.html', form=form)


# ruta para eliminar un cliente por su id,solo acepta post
@app.route('/clientes/eliminar/<int:cliente_id>', methods=['POST'])
def eliminar_cliente(cliente_id):
    global clientes_data
    clientes_data = [c for c in clientes_data if c['id'] != cliente_id]
    return redirect(url_for('clientes'))


# ============================================
# MODULO PROVEEDORES
# ============================================

@app.route('/proveedores')
def proveedores():
    return render_template('proveedores.html', proveedores=proveedores_data)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    form = ProveedorForm()

    if form.validate_on_submit():
        nuevo = {
            'id': len(proveedores_data) + 1,
            'nombre': form.nombre.data,
            'producto': form.producto.data,
            'telefono': form.telefono.data
        }
        proveedores_data.append(nuevo)
        return redirect(url_for('proveedores'))

    return render_template('formulario_proveedor.html', form=form)


# ruta para eliminar un proveedor por su id,solo acepta post
@app.route('/proveedores/eliminar/<int:proveedor_id>', methods=['POST'])
def eliminar_proveedor(proveedor_id):
    global proveedores_data
    proveedores_data = [p for p in proveedores_data if p['id'] != proveedor_id]
    return redirect(url_for('proveedores'))


# ============================================
# MODULO FACTURACION
# ============================================

@app.route('/facturacion')
def facturacion():
    return render_template('facturacion.html', facturas=facturas)


@app.route('/facturacion/nuevo', methods=['GET', 'POST'])
def nueva_factura():
    form = FacturacionForm()

    if form.validate_on_submit():
        nueva = {
            'id': 1000 + len(facturas) + 1,
            'cliente': form.cliente.data,
            'total': form.total.data,
            'estado': form.estado.data
        }
        facturas.append(nueva)
        return redirect(url_for('facturacion'))

    return render_template('formulario_facturacion.html', form=form)


# ruta para eliminar una factura por su id,solo acepta post
@app.route('/facturacion/eliminar/<int:factura_id>', methods=['POST'])
def eliminar_factura(factura_id):
    global facturas
    facturas = [f for f in facturas if f['id'] != factura_id]
    return redirect(url_for('facturacion'))


if __name__ == '__main__':
    app.run(debug=True)
