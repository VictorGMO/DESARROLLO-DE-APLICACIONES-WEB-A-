# app.py
# configuracion de flask y las rutas del proyecto integrador de ElectroCasa
# sistema completo: login con roles,CRUD de los 4 modulos,facturacion con detalle
# de productos,calculo automatico de IVA y descuento de stock

import os
from datetime import date
from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.login_form import LoginForm
from forms.facturacion_form import FacturaForm
from forms.usuario_form import UsuarioForm, CambiarPasswordForm

from conexion.conexion import obtener_conexion, obtener_cursor_dict
from models import Usuario

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-local-solo-para-pruebas')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'


@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.get(id_usuario)


# decorador para rutas que solo puede usar un administrador
# se combina con @login_required arriba de cada ruta que lo use
def admin_required(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not current_user.es_administrador:
            flash('Esta acción solo la puede realizar un administrador.', 'danger')
            return redirect(url_for('dashboard'))
        return vista(*args, **kwargs)
    return envoltura


IVA_PORCENTAJE = 0.15


def generar_numero_factura(id_factura):
    # numero secuencial con formato tipo 001-001-000000123
    return f'001-001-{id_factura:09d}'


# ============================================
# FUNCIONES AUXILIARES: llenar los select de los formularios
# ============================================

def cargar_opciones_proveedor(form):
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    form.id_proveedor.choices = [(0, 'Sin proveedor asignado')] + [(f['id_proveedor'], f['nombre']) for f in filas]


def obtener_clientes_para_select():
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT id_cliente, nombre, cedula FROM clientes ORDER BY nombre')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return filas


def obtener_productos_para_venta():
    # solo se puede vender lo que tiene stock disponible
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT id_producto, nombre, precio, stock FROM productos WHERE stock > 0 ORDER BY nombre')
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return filas


# ============================================
# AUTENTICACION: login,logout,registro,dashboard,usuarios,cambiar password
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        usuario_encontrado = Usuario.buscar_por_usuario(form.usuario.data)

        if usuario_encontrado is None or not check_password_hash(usuario_encontrado.password, form.password.data):
            flash('Usuario o contraseña incorrectos.', 'danger')
        elif not usuario_encontrado.activo:
            flash('Este usuario se encuentra desactivado. Contacte a un administrador.', 'danger')
        else:
            login_user(usuario_encontrado)
            flash(f'Bienvenido, {usuario_encontrado.nombre}.', 'success')
            return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente. ¡Hasta pronto!', 'success')
    return redirect(url_for('index'))


@app.route('/registro', methods=['GET', 'POST'])
@login_required
@admin_required
def registro():
    form = UsuarioForm()

    if form.validate_on_submit():
        password_protegido = generate_password_hash(form.password.data)

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO usuarios (usuario, password, nombre, rol) VALUES (%s, %s, %s, %s)',
                (form.usuario.data, password_protegido, form.nombre.data, form.rol.data)
            )
            conn.commit()
            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('usuarios'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('Ese nombre de usuario ya existe.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('registro.html', form=form)


@app.route('/usuarios')
@login_required
@admin_required
def usuarios():
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT * FROM usuarios ORDER BY id')
    usuarios_lista = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios_lista)


@app.route('/usuarios/desactivar/<int:usuario_id>', methods=['POST'])
@login_required
@admin_required
def desactivar_usuario(usuario_id):
    if usuario_id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'danger')
        return redirect(url_for('usuarios'))

    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('UPDATE usuarios SET activo = NOT activo WHERE id = %s', (usuario_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('usuarios'))


@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    form = CambiarPasswordForm()

    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.password_actual.data):
            flash('La contraseña actual no es correcta.', 'danger')
        else:
            nuevo_hash = generate_password_hash(form.password_nueva.data)
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute('UPDATE usuarios SET password = %s WHERE id = %s', (nuevo_hash, current_user.id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Contraseña actualizada correctamente.', 'success')
            return redirect(url_for('dashboard'))

    return render_template('cambiar_password.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)

    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) AS total FROM facturas
        WHERE estado = 'Pagada' AND date_trunc('month', fecha) = date_trunc('month', CURRENT_DATE)
    """)
    ventas_mes = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM productos WHERE stock > 0 AND stock < 5")
    productos_stock_bajo = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM facturas WHERE estado = 'Pendiente'")
    facturas_pendientes = cursor.fetchone()['total']

    cursor.execute("""
        SELECT f.numero_factura, f.total, f.estado, f.fecha, c.nombre AS cliente_nombre
        FROM facturas f JOIN clientes c ON f.id_cliente = c.id_cliente
        ORDER BY f.id_factura DESC LIMIT 5
    """)
    ultimos_movimientos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        ventas_mes=ventas_mes,
        productos_stock_bajo=productos_stock_bajo,
        facturas_pendientes=facturas_pendientes,
        ultimos_movimientos=ultimos_movimientos
    )


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
    buscar = request.args.get('buscar', '').strip()
    categoria_filtro = request.args.get('categoria', '').strip()

    condiciones = []
    parametros = []

    if buscar:
        condiciones.append('p.nombre ILIKE %s')
        parametros.append(f'%{buscar}%')
    if categoria_filtro:
        condiciones.append('p.categoria = %s')
        parametros.append(categoria_filtro)

    where_sql = ('WHERE ' + ' AND '.join(condiciones)) if condiciones else ''

    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute(f'''
        SELECT p.id_producto, p.nombre, p.descripcion, p.categoria, p.precio, p.stock,
               p.id_proveedor, prov.nombre AS proveedor_nombre
        FROM productos p
        LEFT JOIN proveedores prov ON p.id_proveedor = prov.id_proveedor
        {where_sql}
        ORDER BY p.id_producto
    ''', parametros)
    productos_lista = cursor.fetchall()

    cursor.execute('SELECT DISTINCT categoria FROM productos ORDER BY categoria')
    categorias_disponibles = [f['categoria'] for f in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template(
        'productos.html', productos=productos_lista, categorias=categorias_disponibles,
        buscar=buscar, categoria_filtro=categoria_filtro
    )


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_producto():
    form = ProductoForm()
    cargar_opciones_proveedor(form)

    if form.validate_on_submit():
        id_proveedor_valor = form.id_proveedor.data if form.id_proveedor.data != 0 else None

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''INSERT INTO productos (nombre, descripcion, categoria, precio, stock, id_proveedor)
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (form.nombre.data, form.descripcion.data, form.categoria.data,
                 form.precio.data, form.stock.data, id_proveedor_valor)
            )
            conn.commit()
            flash('Producto registrado correctamente.', 'success')
            return redirect(url_for('productos'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('Ya existe un producto con ese nombre.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('formulario_producto.html', form=form, modo='nuevo')


@app.route('/productos/editar/<int:producto_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_producto(producto_id):
    form = ProductoForm()
    cargar_opciones_proveedor(form)

    if form.validate_on_submit():
        id_proveedor_valor = form.id_proveedor.data if form.id_proveedor.data != 0 else None

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''UPDATE productos
                   SET nombre = %s, descripcion = %s, categoria = %s, precio = %s, stock = %s, id_proveedor = %s
                   WHERE id_producto = %s''',
                (form.nombre.data, form.descripcion.data, form.categoria.data,
                 form.precio.data, form.stock.data, id_proveedor_valor, producto_id)
            )
            conn.commit()
            flash('Producto actualizado correctamente.', 'success')
            return redirect(url_for('productos'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('Ya existe un producto con ese nombre.', 'danger')
        finally:
            cursor.close()
            conn.close()

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
        form.precio.data = float(producto['precio'])
        form.stock.data = producto['stock']
        form.id_proveedor.data = producto['id_proveedor'] if producto['id_proveedor'] else 0

    return render_template('formulario_producto.html', form=form, modo='editar')


@app.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_producto(producto_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM productos WHERE id_producto = %s', (producto_id,))
        conn.commit()
        flash('Producto eliminado correctamente.', 'success')
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        flash('No se puede eliminar: este producto ya tiene facturas registradas.', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('productos'))


# ============================================
# MODULO CLIENTES
# ============================================

@app.route('/clientes')
@login_required
def clientes():
    buscar = request.args.get('buscar', '').strip()

    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    if buscar:
        cursor.execute(
            '''SELECT * FROM clientes
               WHERE nombre ILIKE %s OR cedula ILIKE %s OR correo ILIKE %s
               ORDER BY id_cliente''',
            (f'%{buscar}%', f'%{buscar}%', f'%{buscar}%')
        )
    else:
        cursor.execute('SELECT * FROM clientes ORDER BY id_cliente')
    clientes_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('clientes.html', clientes=clientes_lista, buscar=buscar)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO clientes (nombre, correo, telefono, cedula, direccion) VALUES (%s, %s, %s, %s, %s)',
                (form.nombre.data, form.correo.data, form.telefono.data, form.cedula.data, form.direccion.data)
            )
            conn.commit()
            flash('Cliente registrado correctamente.', 'success')
            return redirect(url_for('clientes'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('Ya existe un cliente con ese correo o cédula/RUC.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('formulario_cliente.html', form=form, modo='nuevo')


@app.route('/clientes/editar/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_cliente(cliente_id):
    form = ClienteForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'UPDATE clientes SET nombre = %s, correo = %s, telefono = %s, cedula = %s, direccion = %s WHERE id_cliente = %s',
                (form.nombre.data, form.correo.data, form.telefono.data, form.cedula.data, form.direccion.data, cliente_id)
            )
            conn.commit()
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('clientes'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('Ya existe un cliente con ese correo o cédula/RUC.', 'danger')
        finally:
            cursor.close()
            conn.close()

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
        form.cedula.data = cliente['cedula']
        form.direccion.data = cliente['direccion']

    return render_template('formulario_cliente.html', form=form, modo='editar')


@app.route('/clientes/eliminar/<int:cliente_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_cliente(cliente_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM clientes WHERE id_cliente = %s', (cliente_id,))
        conn.commit()
        flash('Cliente eliminado correctamente.', 'success')
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        flash('No se puede eliminar: este cliente ya tiene facturas registradas en su historial.', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('clientes'))


@app.route('/clientes/historial/<int:cliente_id>')
@login_required
def historial_cliente(cliente_id):
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    cursor.execute('SELECT * FROM clientes WHERE id_cliente = %s', (cliente_id,))
    cliente = cursor.fetchone()

    if cliente is None:
        cursor.close()
        conn.close()
        return redirect(url_for('clientes'))

    cursor.execute(
        'SELECT * FROM facturas WHERE id_cliente = %s ORDER BY id_factura DESC',
        (cliente_id,)
    )
    facturas_cliente = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('historial_cliente.html', cliente=cliente, facturas=facturas_cliente)


# ============================================
# MODULO PROVEEDORES
# ============================================

@app.route('/proveedores')
@login_required
def proveedores():
    buscar = request.args.get('buscar', '').strip()

    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    # left join + count para saber cuantos productos tiene cada proveedor
    if buscar:
        cursor.execute('''
            SELECT pr.*, COUNT(p.id_producto) AS total_productos
            FROM proveedores pr
            LEFT JOIN productos p ON p.id_proveedor = pr.id_proveedor
            WHERE pr.nombre ILIKE %s
            GROUP BY pr.id_proveedor
            ORDER BY pr.id_proveedor
        ''', (f'%{buscar}%',))
    else:
        cursor.execute('''
            SELECT pr.*, COUNT(p.id_producto) AS total_productos
            FROM proveedores pr
            LEFT JOIN productos p ON p.id_proveedor = pr.id_proveedor
            GROUP BY pr.id_proveedor
            ORDER BY pr.id_proveedor
        ''')
    proveedores_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('proveedores.html', proveedores=proveedores_lista, buscar=buscar)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_proveedor():
    form = ProveedorForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO proveedores (nombre, producto, telefono, correo, direccion) VALUES (%s, %s, %s, %s, %s)',
            (form.nombre.data, form.producto.data, form.telefono.data, form.correo.data or None, form.direccion.data or None)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Proveedor registrado correctamente.', 'success')
        return redirect(url_for('proveedores'))

    return render_template('formulario_proveedor.html', form=form, modo='nuevo')


@app.route('/proveedores/editar/<int:proveedor_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_proveedor(proveedor_id):
    form = ProveedorForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE proveedores SET nombre = %s, producto = %s, telefono = %s, correo = %s, direccion = %s WHERE id_proveedor = %s',
            (form.nombre.data, form.producto.data, form.telefono.data, form.correo.data or None, form.direccion.data or None, proveedor_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Proveedor actualizado correctamente.', 'success')
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
        form.correo.data = proveedor['correo']
        form.direccion.data = proveedor['direccion']

    return render_template('formulario_proveedor.html', form=form, modo='editar')


@app.route('/proveedores/eliminar/<int:proveedor_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_proveedor(proveedor_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM proveedores WHERE id_proveedor = %s', (proveedor_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Proveedor eliminado correctamente.', 'success')
    return redirect(url_for('proveedores'))


# ============================================
# MODULO FACTURACION (con detalle,IVA y descuento de stock)
# ============================================

@app.route('/facturacion')
@login_required
def facturacion():
    estado_filtro = request.args.get('estado', '').strip()

    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)
    if estado_filtro:
        cursor.execute('''
            SELECT f.*, c.nombre AS cliente_nombre
            FROM facturas f JOIN clientes c ON f.id_cliente = c.id_cliente
            WHERE f.estado = %s
            ORDER BY f.id_factura DESC
        ''', (estado_filtro,))
    else:
        cursor.execute('''
            SELECT f.*, c.nombre AS cliente_nombre
            FROM facturas f JOIN clientes c ON f.id_cliente = c.id_cliente
            ORDER BY f.id_factura DESC
        ''')
    facturas_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('facturacion.html', facturas=facturas_lista, estado_filtro=estado_filtro)


@app.route('/facturacion/nuevo', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    csrf_form = FacturaForm()
    clientes_lista = obtener_clientes_para_select()
    productos_lista = obtener_productos_para_venta()

    if request.method == 'POST' and csrf_form.validate_on_submit():
        id_cliente = request.form.get('id_cliente', type=int)
        estado = request.form.get('estado', '')
        productos_ids = request.form.getlist('producto_id')
        cantidades = request.form.getlist('cantidad')

        errores = []
        if not id_cliente:
            errores.append('Debe seleccionar un cliente.')
        if estado not in ('Pagada', 'Pendiente'):
            errores.append('Debe seleccionar un estado válido.')
        if not productos_ids:
            errores.append('Debe agregar al menos un producto a la factura.')

        # se arma la lista de lineas validas,verificando stock disponible de cada una
        lineas = []
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)

        for pid_str, cant_str in zip(productos_ids, cantidades):
            try:
                pid = int(pid_str)
                cantidad = int(cant_str)
            except ValueError:
                errores.append('Cantidad inválida en uno de los productos.')
                continue

            if cantidad <= 0:
                errores.append('La cantidad debe ser mayor a 0.')
                continue

            cursor.execute('SELECT * FROM productos WHERE id_producto = %s', (pid,))
            producto = cursor.fetchone()

            if producto is None:
                errores.append('Uno de los productos seleccionados no existe.')
                continue

            # aca se defiende el sistema de vender mas de lo que hay en stock
            if cantidad > producto['stock']:
                errores.append(
                    f"No hay stock suficiente de \"{producto['nombre']}\". Disponible: {producto['stock']},solicitado: {cantidad}."
                )
                continue

            subtotal_linea = round(float(producto['precio']) * cantidad, 2)
            lineas.append({
                'id_producto': pid,
                'nombre': producto['nombre'],
                'cantidad': cantidad,
                'precio_unitario': float(producto['precio']),
                'subtotal': subtotal_linea
            })

        if errores or not lineas:
            for error in errores:
                flash(error, 'danger')
            cursor.close()
            conn.close()
            return render_template(
                'formulario_factura.html', clientes=clientes_lista, productos=productos_lista,
                iva_porcentaje=IVA_PORCENTAJE, csrf_form=csrf_form
            )

        subtotal = round(sum(l['subtotal'] for l in lineas), 2)
        iva = round(subtotal * IVA_PORCENTAJE, 2)
        total = round(subtotal + iva, 2)

        try:
            cursor.execute(
                '''INSERT INTO facturas (numero_factura, id_cliente, subtotal, iva, total, estado)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_factura''',
                ('TEMPORAL', id_cliente, subtotal, iva, total, estado)
            )
            id_factura = cursor.fetchone()['id_factura']

            numero_factura = generar_numero_factura(id_factura)
            cursor.execute('UPDATE facturas SET numero_factura = %s WHERE id_factura = %s', (numero_factura, id_factura))

            for linea in lineas:
                cursor.execute(
                    '''INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio_unitario, subtotal)
                       VALUES (%s, %s, %s, %s, %s)''',
                    (id_factura, linea['id_producto'], linea['cantidad'], linea['precio_unitario'], linea['subtotal'])
                )
                # se descuenta el stock vendido
                cursor.execute(
                    'UPDATE productos SET stock = stock - %s WHERE id_producto = %s',
                    (linea['cantidad'], linea['id_producto'])
                )

            conn.commit()
            flash(f'Factura {numero_factura} registrada correctamente.', 'success')
            return redirect(url_for('facturacion'))
        except Exception:
            conn.rollback()
            flash('Ocurrió un error al registrar la factura. Intente nuevamente.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template(
        'formulario_factura.html', clientes=clientes_lista, productos=productos_lista,
        iva_porcentaje=IVA_PORCENTAJE, csrf_form=csrf_form
    )


@app.route('/facturacion/detalle/<int:factura_id>')
@login_required
def detalle_factura(factura_id):
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)

    cursor.execute('''
        SELECT f.*, c.nombre AS cliente_nombre, c.cedula, c.correo, c.telefono, c.direccion
        FROM facturas f JOIN clientes c ON f.id_cliente = c.id_cliente
        WHERE f.id_factura = %s
    ''', (factura_id,))
    factura = cursor.fetchone()

    if factura is None:
        cursor.close()
        conn.close()
        return redirect(url_for('facturacion'))

    cursor.execute('''
        SELECT d.*, p.nombre AS producto_nombre
        FROM detalle_factura d JOIN productos p ON d.id_producto = p.id_producto
        WHERE d.id_factura = %s
        ORDER BY d.id_detalle
    ''', (factura_id,))
    detalle = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('detalle_factura.html', factura=factura, detalle=detalle)


@app.route('/facturacion/marcar-pagada/<int:factura_id>', methods=['POST'])
@login_required
def marcar_pagada(factura_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT estado FROM facturas WHERE id_factura = %s', (factura_id,))
    fila = cursor.fetchone()

    if fila is None:
        flash('Esa factura no existe.', 'danger')
    elif fila[0] != 'Pendiente':
        flash('Solo una factura Pendiente se puede marcar como Pagada.', 'danger')
    else:
        cursor.execute("UPDATE facturas SET estado = 'Pagada' WHERE id_factura = %s", (factura_id,))
        conn.commit()
        flash('Factura marcada como Pagada.', 'success')

    cursor.close()
    conn.close()
    return redirect(url_for('facturacion'))


@app.route('/facturacion/anular/<int:factura_id>', methods=['POST'])
@login_required
@admin_required
def anular_factura(factura_id):
    conn = obtener_conexion()
    cursor = obtener_cursor_dict(conn)

    cursor.execute('SELECT * FROM facturas WHERE id_factura = %s', (factura_id,))
    factura = cursor.fetchone()

    if factura is None:
        flash('Esa factura no existe.', 'danger')
    elif factura['estado'] == 'Anulada':
        flash('Esta factura ya estaba anulada.', 'danger')
    else:
        # se devuelve el stock de cada producto de la factura,y se marca como anulada
        cursor.execute('SELECT * FROM detalle_factura WHERE id_factura = %s', (factura_id,))
        lineas = cursor.fetchall()
        for linea in lineas:
            cursor.execute(
                'UPDATE productos SET stock = stock + %s WHERE id_producto = %s',
                (linea['cantidad'], linea['id_producto'])
            )
        cursor.execute("UPDATE facturas SET estado = 'Anulada' WHERE id_factura = %s", (factura_id,))
        conn.commit()
        flash('Factura anulada. El stock fue devuelto.', 'success')

    cursor.close()
    conn.close()
    return redirect(url_for('facturacion'))


if __name__ == '__main__':
    app.run(debug=True)
