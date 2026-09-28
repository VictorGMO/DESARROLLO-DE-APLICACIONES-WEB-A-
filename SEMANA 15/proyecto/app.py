# app.py
# configuracion de flask y las rutas del proyecto integrador de ElectroCasa
# los cuatro modulos (productos,clientes,proveedores,facturacion) usan PostgreSQL
# las paginas de administracion estan protegidas con login,solo se entra iniciando sesion

import os

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm
from forms.login_form import LoginForm
from forms.usuario_form import UsuarioForm

from conexion.conexion import obtener_conexion, obtener_cursor_dict
from models import Usuario

app = Flask(__name__)

# secret_key para la proteccion csrf de flask-wtf y para las sesiones
# en render se configura como variable de entorno,si no existe se usa la de abajo (solo para local)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-local-solo-para-pruebas')

# configuracion del login manager,el encargado de manejar la sesion del usuario
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # si alguien sin sesion entra a una pagina protegida,lo manda aca
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'


# flask-login llama a esta funcion para saber quien es el usuario de la sesion
@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.get(id_usuario)


# ============================================
# FUNCIONES AUXILIARES: llenar los select de los formularios con datos de la base
# ============================================

def cargar_opciones_proveedor(form):
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre')
    proveedores_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    opciones = [(0, 'Sin proveedor asignado')]
    opciones += [(p['id_proveedor'], p['nombre']) for p in proveedores_lista]
    form.id_proveedor.choices = opciones


def cargar_opciones_cliente(form):
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT id_cliente, nombre FROM clientes ORDER BY nombre')
    clientes_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    opciones = [(0, 'Seleccione un cliente')]
    opciones += [(c['id_cliente'], c['nombre']) for c in clientes_lista]
    form.id_cliente.choices = opciones


# ============================================
# AUTENTICACION: login,logout,registro y dashboard
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        usuario_encontrado = Usuario.buscar_por_usuario(form.usuario.data)

        # se compara con check_password_hash,nunca el texto plano contra lo que hay en la base
        if usuario_encontrado and check_password_hash(usuario_encontrado.password, form.password.data):
            login_user(usuario_encontrado)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# solo un usuario que ya inicio sesion puede crear usuarios nuevos
@app.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():
    form = UsuarioForm()

    if form.validate_on_submit():
        # la contraseña se guarda con hash,nunca en texto plano
        password_protegido = generate_password_hash(form.password.data)

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO usuarios (usuario, password) VALUES (%s, %s)',
                (form.usuario.data, password_protegido)
            )
            conn.commit()
            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('dashboard'))
        except Exception:
            # si el nombre de usuario ya existe,postgres da error por el UNIQUE
            conn.rollback()
            flash('Ese nombre de usuario ya existe.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('registro.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# ============================================
# RUTA PRINCIPAL (publica)
# ============================================

@app.route('/')
def index():
    nombre_sistema = 'ElectroCasa'

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM productos')
    total_productos = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM clientes')
    total_clientes = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM proveedores')
    total_proveedores = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    estadisticas = {
        'total_productos': total_productos,
        'total_clientes': total_clientes,
        'total_proveedores': total_proveedores
    }

    return render_template('index.html', nombre_sistema=nombre_sistema, estadisticas=estadisticas)


# ============================================
# MODULO PRODUCTOS
# ============================================

@app.route('/productos')
@login_required
def productos():
    # join con proveedores para mostrar el nombre del proveedor de cada producto
    # left join porque algunos productos pueden no tener proveedor (NULL)
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


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    form = ProductoForm()
    cargar_opciones_proveedor(form)

    if form.validate_on_submit():
        # el valor 0 significa sin proveedor,se guarda como NULL
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


@app.route('/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
@login_required
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

    # en GET se cargan los datos actuales del producto dentro del formulario
    if request.method == 'GET':
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM productos WHERE id_producto = %s', (producto_id,))
        producto = cursor.fetchone()
        cursor.close()
        conn.close()

        if producto is None:
            return redirect(url_for('productos'))

        form.nombre.data = producto['nombre']
        form.descripcion.data = producto['descripcion']
        form.categoria.data = producto['categoria']
        form.stock.data = producto['stock']
        form.id_proveedor.data = producto['id_proveedor'] if producto['id_proveedor'] else 0

    return render_template('formulario_producto.html', form=form, modo='editar')


@app.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_producto(producto_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id_producto = %s', (producto_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('productos'))


# ============================================
# MODULO CLIENTES
# ============================================

@app.route('/clientes')
@login_required
def clientes():
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT * FROM clientes ORDER BY id_cliente')
    clientes_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('clientes.html', clientes=clientes_lista)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO clientes (nombre, correo, telefono) VALUES (%s, %s, %s)',
            (form.nombre.data, form.correo.data, form.telefono.data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('clientes'))

    return render_template('formulario_cliente.html', form=form, modo='nuevo')


@app.route('/clientes/editar/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(cliente_id):
    form = ClienteForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE clientes SET nombre = %s, correo = %s, telefono = %s WHERE id_cliente = %s',
            (form.nombre.data, form.correo.data, form.telefono.data, cliente_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('clientes'))

    if request.method == 'GET':
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM clientes WHERE id_cliente = %s', (cliente_id,))
        cliente = cursor.fetchone()
        cursor.close()
        conn.close()

        if cliente is None:
            return redirect(url_for('clientes'))

        form.nombre.data = cliente['nombre']
        form.correo.data = cliente['correo']
        form.telefono.data = cliente['telefono']

    return render_template('formulario_cliente.html', form=form, modo='editar')


@app.route('/clientes/eliminar/<int:cliente_id>', methods=['POST'])
@login_required
def eliminar_cliente(cliente_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE id_cliente = %s', (cliente_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('clientes'))


# ============================================
# MODULO PROVEEDORES
# ============================================

@app.route('/proveedores')
@login_required
def proveedores():
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT * FROM proveedores ORDER BY id_proveedor')
    proveedores_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('proveedores.html', proveedores=proveedores_lista)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proveedor():
    form = ProveedorForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO proveedores (nombre, producto, telefono) VALUES (%s, %s, %s)',
            (form.nombre.data, form.producto.data, form.telefono.data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('proveedores'))

    return render_template('formulario_proveedor.html', form=form, modo='nuevo')


@app.route('/proveedores/editar/<int:proveedor_id>', methods=['GET', 'POST'])
@login_required
def editar_proveedor(proveedor_id):
    form = ProveedorForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE proveedores SET nombre = %s, producto = %s, telefono = %s WHERE id_proveedor = %s',
            (form.nombre.data, form.producto.data, form.telefono.data, proveedor_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('proveedores'))

    if request.method == 'GET':
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM proveedores WHERE id_proveedor = %s', (proveedor_id,))
        proveedor = cursor.fetchone()
        cursor.close()
        conn.close()

        if proveedor is None:
            return redirect(url_for('proveedores'))

        form.nombre.data = proveedor['nombre']
        form.producto.data = proveedor['producto']
        form.telefono.data = proveedor['telefono']

    return render_template('formulario_proveedor.html', form=form, modo='editar')


@app.route('/proveedores/eliminar/<int:proveedor_id>', methods=['POST'])
@login_required
def eliminar_proveedor(proveedor_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM proveedores WHERE id_proveedor = %s', (proveedor_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('proveedores'))


# ============================================
# MODULO FACTURACION
# ============================================

@app.route('/facturacion')
@login_required
def facturacion():
    # join con clientes para mostrar el nombre del cliente de cada factura
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('''
        SELECT f.id_factura, f.id_cliente, f.total, f.estado, f.fecha,
               c.nombre AS cliente_nombre
        FROM facturas f
        JOIN clientes c ON f.id_cliente = c.id_cliente
        ORDER BY f.id_factura
    ''')
    facturas_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('facturacion.html', facturas=facturas_lista)


@app.route('/facturacion/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    form = FacturacionForm()
    cargar_opciones_cliente(form)

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO facturas (id_cliente, total, estado) VALUES (%s, %s, %s)',
            (form.id_cliente.data, form.total.data, form.estado.data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('facturacion'))

    return render_template('formulario_facturacion.html', form=form, modo='nuevo')


@app.route('/facturacion/editar/<int:factura_id>', methods=['GET', 'POST'])
@login_required
def editar_factura(factura_id):
    form = FacturacionForm()
    cargar_opciones_cliente(form)

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE facturas SET id_cliente = %s, total = %s, estado = %s WHERE id_factura = %s',
            (form.id_cliente.data, form.total.data, form.estado.data, factura_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('facturacion'))

    if request.method == 'GET':
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM facturas WHERE id_factura = %s', (factura_id,))
        factura = cursor.fetchone()
        cursor.close()
        conn.close()

        if factura is None:
            return redirect(url_for('facturacion'))

        form.id_cliente.data = factura['id_cliente']
        form.total.data = float(factura['total'])
        form.estado.data = factura['estado']

    return render_template('formulario_facturacion.html', form=form, modo='editar')


@app.route('/facturacion/eliminar/<int:factura_id>', methods=['POST'])
@login_required
def eliminar_factura(factura_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM facturas WHERE id_factura = %s', (factura_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('facturacion'))


if __name__ == '__main__':
    app.run(debug=True)
