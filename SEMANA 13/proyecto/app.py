# app.py
# configuracion de flask y las rutas del proyecto integrador de ElectroCasa
# el modulo de productos usa PostgreSQL como base de datos real.
# los otros modulos (clientes,proveedores,facturacion) siguen con listas en memoria por ahora,
# quedan preparados para migrar a la base de datos mas adelante

from flask import Flask, render_template, redirect, url_for, request

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

from conexion.conexion import obtener_conexion, obtener_cursor_dict

app = Flask(__name__)

# secret_key necesaria para que funcione la proteccion csrf de flask-wtf
app.config['SECRET_KEY'] = 'clave-secreta-proyecto-integrador-uea-2026'


# ============================================
# FUNCION AUXILIAR: llenar las opciones de proveedor en el formulario
# se consulta la tabla proveedores cada vez que se abre el formulario de producto,
# asi el select siempre muestra los proveedores que existan en ese momento
# ============================================

def cargar_opciones_proveedor(form):
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre')
    proveedores = cursor.fetchall()
    cursor.close()
    conn.close()

    opciones = [(0, 'Sin proveedor asignado')]
    opciones += [(p['id_proveedor'], p['nombre']) for p in proveedores]
    form.id_proveedor.choices = opciones


# ============================================
# DATOS EN MEMORIA (modulos que todavia no usan base de datos)
# ============================================

clientes_data = [
    {'id': 1, 'nombre': 'Juan Perez', 'correo': 'juan.perez@example.com', 'telefono': '099 123 4567'},
    {'id': 2, 'nombre': 'Maria Lopez', 'correo': 'maria.lopez@example.com', 'telefono': '098 765 4321'},
    {'id': 3, 'nombre': 'Carlos Mera', 'correo': 'carlos.mera@example.com', 'telefono': '096 541 2378'}
]

proveedores_data = [
    {'id': 1, 'nombre': 'Indurama', 'producto': 'Cocinas', 'telefono': '07 280 5000'},
    {'id': 2, 'nombre': 'Mabe Ecuador', 'producto': 'Refrigeración', 'telefono': '04 220 1000'},
    {'id': 3, 'nombre': 'LG Electronics', 'producto': 'Televisores', 'telefono': '02 396 3000'}
]

facturas = [
    {'id': 1001, 'cliente': 'Juan Perez', 'total': 650.50, 'estado': 'Pagada'},
    {'id': 1002, 'cliente': 'Maria Lopez', 'total': 890.00, 'estado': 'Pendiente'},
    {'id': 1003, 'cliente': 'Carlos Mera', 'total': 120.99, 'estado': 'Pagada'}
]


# ============================================
# RUTA PRINCIPAL
# ============================================

@app.route('/')
def index():
    nombre_sistema = 'ElectroCasa'

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM productos')
    total_productos = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    estadisticas = {
        'total_productos': total_productos,
        'total_clientes': len(clientes_data),
        'total_proveedores': len(proveedores_data)
    }

    return render_template('index.html', nombre_sistema=nombre_sistema, estadisticas=estadisticas)


# ============================================
# MODULO PRODUCTOS (listar,agregar,modificar y eliminar usando PostgreSQL)
# ============================================

@app.route('/productos')
def productos():
    # select con join,para traer tambien el nombre del proveedor de cada producto
    # left join porque algunos productos pueden no tener proveedor asignado (NULL)
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('''
        SELECT p.id_producto, p.nombre, p.descripcion, p.categoria, p.stock,
               p.id_proveedor, prov.nombre AS proveedor_nombre
        FROM productos p
        LEFT JOIN proveedores prov ON p.id_proveedor = prov.id_proveedor
        ORDER BY p.id_producto
    ''')
    productos_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('productos.html', productos=productos_lista)


# agregar un producto nuevo,GET muestra el formulario vacio,POST valida e inserta
@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    form = ProductoForm()
    cargar_opciones_proveedor(form)

    if form.validate_on_submit():
        # value 0 = "sin proveedor asignado",se guarda como NULL en la base
        id_proveedor_valor = form.id_proveedor.data if form.id_proveedor.data != 0 else None

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO productos (nombre, descripcion, categoria, stock, id_proveedor)
               VALUES (%s, %s, %s, %s, %s)''',
            (form.nombre.data, form.descripcion.data, form.categoria.data, form.stock.data, id_proveedor_valor)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('productos'))

    return render_template('formulario_producto.html', form=form, modo='nuevo')


# modificar un producto existente. GET carga los datos actuales en el formulario,
# POST valida y actualiza con UPDATE ... WHERE (solo ese registro)
@app.route('/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    form = ProductoForm()
    cargar_opciones_proveedor(form)

    if form.validate_on_submit():
        id_proveedor_valor = form.id_proveedor.data if form.id_proveedor.data != 0 else None

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE productos
               SET nombre = %s, descripcion = %s, categoria = %s, stock = %s, id_proveedor = %s
               WHERE id_producto = %s''',
            (form.nombre.data, form.descripcion.data, form.categoria.data, form.stock.data,
             id_proveedor_valor, producto_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('productos'))

    # si es GET (primera vez que se abre la pagina),se cargan los datos actuales del producto
    # si es POST pero la validacion fallo,se deja lo que el usuario escribio,no se sobreescribe
    if request.method == 'GET':
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM productos WHERE id_producto = %s', (producto_id,))
        producto = cursor.fetchone()
        cursor.close()
        conn.close()

        form.nombre.data = producto['nombre']
        form.descripcion.data = producto['descripcion']
        form.categoria.data = producto['categoria']
        form.stock.data = producto['stock']
        form.id_proveedor.data = producto['id_proveedor'] if producto['id_proveedor'] else 0

    return render_template('formulario_producto.html', form=form, modo='editar', producto_id=producto_id)


# eliminar un producto,solo acepta post,con confirmacion desde el html antes de enviar
@app.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id_producto = %s', (producto_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('productos'))


# ============================================
# MODULO CLIENTES (todavia en memoria,preparado para migrar mas adelante)
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


@app.route('/clientes/eliminar/<int:cliente_id>', methods=['POST'])
def eliminar_cliente(cliente_id):
    global clientes_data
    clientes_data = [c for c in clientes_data if c['id'] != cliente_id]
    return redirect(url_for('clientes'))


# ============================================
# MODULO PROVEEDORES (todavia en memoria para el listado propio del modulo;
# la tabla proveedores de postgresql se usa solo como referencia para productos)
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


@app.route('/proveedores/eliminar/<int:proveedor_id>', methods=['POST'])
def eliminar_proveedor(proveedor_id):
    global proveedores_data
    proveedores_data = [p for p in proveedores_data if p['id'] != proveedor_id]
    return redirect(url_for('proveedores'))


# ============================================
# MODULO FACTURACION (todavia en memoria)
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


@app.route('/facturacion/eliminar/<int:factura_id>', methods=['POST'])
def eliminar_factura(factura_id):
    global facturas
    facturas = [f for f in facturas if f['id'] != factura_id]
    return redirect(url_for('facturacion'))


if __name__ == '__main__':
    app.run(debug=True)
