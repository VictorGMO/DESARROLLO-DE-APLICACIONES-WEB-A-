# app.py
# aca configuramos flask y las rutas del proyecto integrador de ElectroCasa
# cada modulo (productos,clientes,proveedores,facturacion) tiene su propia ruta
# se usan formularios con flask-wtf,validados en el servidor
# el modulo de productos ya no usa una lista de python,
# usa una base de datos sqlite para que los datos no se pierdan al reiniciar la app

import sqlite3
import os

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
# BASE DE DATOS SQLITE
# se guarda dentro de la carpeta data,en la raiz del proyecto
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'electrocasa.db')


def obtener_conexion():
    # sqlite3.connect abre (o crea si no existe) el archivo de base de datos
    conn = sqlite3.connect(DB_PATH)
    # row_factory permite acceder a cada fila como si fuera un diccionario,
    # asi en las plantillas se puede seguir usando producto.nombre igual que antes
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_base_datos():
    conn = obtener_conexion()
    cursor = conn.cursor()

    # create table if not exists evita error si la tabla ya existe
    # id es la clave primaria,se autoincrementa solo con cada nuevo producto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            categoria TEXT NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    # si la tabla esta vacia (primera vez que se corre la app),se cargan datos de ejemplo
    cursor.execute('SELECT COUNT(*) FROM productos')
    total = cursor.fetchone()[0]

    if total == 0:
        productos_ejemplo = [
            ('Cocina a gas 4 hornillas', 'Cocina a gas de acero inoxidable con encendido automatico', 'Cocinas', 8),
            ('Refrigeradora 300L', 'Refrigeradora No Frost de 300 litros,color plateado', 'Refrigeración', 3),
            ('Televisor LED 50 pulgadas', 'Smart TV LED 50 pulgadas,resolucion 4K', 'Televisores', 0),
            ('Lavadora automatica 16kg', 'Lavadora de carga superior,16 kilogramos,varios programas', 'Lavado', 5),
            ('Licuadora industrial', 'Licuadora de alta potencia,jarra de vidrio de 2 litros', 'Cocina', 12)
        ]
        cursor.executemany(
            'INSERT INTO productos (nombre, descripcion, categoria, stock) VALUES (?, ?, ?, ?)',
            productos_ejemplo
        )

    conn.commit()
    conn.close()


# se inicializa la base de datos apenas arranca la aplicacion
inicializar_base_datos()


# ============================================
# DATOS EN MEMORIA (modulos que todavia no tienen persistencia)
# estas listas viven mientras la app este corriendo,se reinician
# si se reinicia el servidor. quedan preparadas para migrarse a sqlite
# progresivamente en semanas siguientes,tal como pide la consigna
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

# ruta principal,muestra la pagina informativa de ElectroCasa
# nombre_sistema es una variable simple,estadisticas es un diccionario con info general
@app.route('/')
def index():
    nombre_sistema = 'ElectroCasa'

    # el total de productos ahora se consulta directo en la base de datos
    conn = obtener_conexion()
    total_productos = conn.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
    conn.close()

    estadisticas = {
        'total_productos': total_productos,
        'total_clientes': len(clientes_data),
        'total_proveedores': len(proveedores_data)
    }

    return render_template('index.html', nombre_sistema=nombre_sistema, estadisticas=estadisticas)


# ============================================
# MODULO PRODUCTOS (con persistencia en sqlite desde la semana 12)
# ============================================

@app.route('/productos')
def productos():
    # select para traer todos los productos guardados en la base de datos
    conn = obtener_conexion()
    filas = conn.execute('SELECT * FROM productos ORDER BY id').fetchall()
    conn.close()

    # se convierte cada fila a un diccionario normal,para que jinja2 los recorra igual que antes
    productos_lista = [dict(fila) for fila in filas]

    return render_template('productos.html', productos=productos_lista)


# ruta con formulario de flask-wtf,acepta GET (mostrar el formulario) y POST (procesar los datos)
@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    form = ProductoForm()

    # validate_on_submit() revisa que sea POST y que pasen todos los validadores
    # el insert solo se ejecuta si el formulario paso todas las validaciones
    if form.validate_on_submit():
        conn = obtener_conexion()
        conn.execute(
            'INSERT INTO productos (nombre, descripcion, categoria, stock) VALUES (?, ?, ?, ?)',
            (form.nombre.data, form.descripcion.data, form.categoria.data, form.stock.data)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('productos'))

    return render_template('formulario_producto.html', form=form)


# ruta para eliminar un producto por su id,solo acepta post,se llama desde un boton en productos.html
@app.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    conn = obtener_conexion()
    conn.execute('DELETE FROM productos WHERE id = ?', (producto_id,))
    conn.commit()
    conn.close()
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
