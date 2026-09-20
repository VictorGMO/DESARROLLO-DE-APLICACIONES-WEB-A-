# app.py
# configuracion de flask y las rutas del proyecto integrador de ElectroCasa
# el modulo de productos usa PostgreSQL como base de datos real.
# los otros modulos (clientes,proveedores,facturacion) siguen con listas en memoria por ahora,
# quedan preparados para migrar a la base de datos mas adelante
# las paginas de administracion (productos,clientes,proveedores,facturacion) ahora
# estan protegidas con un sistema de login,solo se puede entrar iniciando sesion

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

# secret_key necesaria para que funcione la proteccion csrf de flask-wtf y el manejo de sesiones
app.config['SECRET_KEY'] = 'clave-secreta-proyecto-integrador-uea-2026'

# configuracion del login manager,el encargado de manejar la sesion del usuario
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # si alguien entra sin sesion a una pagina protegida,lo manda para aca
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'


# flask-login llama a esta funcion en cada peticion para saber quien es el usuario logueado
@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.get(id_usuario)


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
# AUTENTICACION: login,logout,registro y dashboard
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    # si ya inicio sesion,no tiene sentido que vea el login de nuevo
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        usuario_encontrado = Usuario.buscar_por_usuario(form.usuario.data)

        # se compara con check_password_hash,nunca comparando texto plano contra texto plano
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


# esta pagina solo la puede usar alguien que ya inicio sesion,
# asi no cualquiera puede crear usuarios nuevos por su cuenta
@app.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():
    form = UsuarioForm()

    if form.validate_on_submit():
        # la contraseña se protege con hash antes de guardarla,nunca en texto plano
        password_protegido = generate_password_hash(form.password.data)

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO usuarios (usuario, password) VALUES (%s, %s)',
            (form.usuario.data, password_protegido)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Usuario registrado correctamente.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('registro.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


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
@login_required
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
@login_required
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
# MODULO CLIENTES (todavia en memoria,preparado para migrar mas adelante)
# ============================================

@app.route('/clientes')
@login_required
def clientes():
    return render_template('clientes.html', clientes=clientes_data)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
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
@login_required
def eliminar_cliente(cliente_id):
    global clientes_data
    clientes_data = [c for c in clientes_data if c['id'] != cliente_id]
    return redirect(url_for('clientes'))


# ============================================
# MODULO PROVEEDORES (todavia en memoria para el listado propio del modulo;
# la tabla proveedores de postgresql se usa solo como referencia para productos)
# ============================================

@app.route('/proveedores')
@login_required
def proveedores():
    return render_template('proveedores.html', proveedores=proveedores_data)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
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
@login_required
def eliminar_proveedor(proveedor_id):
    global proveedores_data
    proveedores_data = [p for p in proveedores_data if p['id'] != proveedor_id]
    return redirect(url_for('proveedores'))


# ============================================
# MODULO FACTURACION (todavia en memoria)
# ============================================

@app.route('/facturacion')
@login_required
def facturacion():
    return render_template('facturacion.html', facturas=facturas)


@app.route('/facturacion/nuevo', methods=['GET', 'POST'])
@login_required
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
@login_required
def eliminar_factura(factura_id):
    global facturas
    facturas = [f for f in facturas if f['id'] != factura_id]
    return redirect(url_for('facturacion'))


if __name__ == '__main__':
    app.run(debug=True)
