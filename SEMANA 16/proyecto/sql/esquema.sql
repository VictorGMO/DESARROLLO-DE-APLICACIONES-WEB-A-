-- sql/esquema.sql
-- esquema final del proyecto ElectroCasa
-- se corre completo en pgAdmin (Query Tool) sobre la base de datos del proyecto

DROP TABLE IF EXISTS detalle_factura;
DROP TABLE IF EXISTS facturas;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS usuarios;

-- usuarios del sistema. rol define que puede hacer cada uno:
-- administrador ve y hace todo. vendedor solo factura y consulta,no puede
-- crear/eliminar usuarios ni eliminar registros criticos
-- activo permite desactivar un usuario sin borrar su historial
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'vendedor' CHECK (rol IN ('administrador', 'vendedor')),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    producto VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(100),
    direccion VARCHAR(200)
);

-- productos. nombre es UNIQUE para no repetir productos por error
-- precio con CHECK > 0,stock con CHECK >= 0 (defensa a nivel de base de datos,
-- ademas de la validacion que ya hace el formulario)
CREATE TABLE productos (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    precio NUMERIC(10, 2) NOT NULL CHECK (precio > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    id_proveedor INTEGER REFERENCES proveedores(id_proveedor) ON DELETE SET NULL
);

-- clientes. correo y cedula son UNIQUE para no duplicar clientes
CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    cedula VARCHAR(13) UNIQUE NOT NULL,
    direccion VARCHAR(200) NOT NULL
);

-- facturas. ON DELETE RESTRICT en id_cliente: no se puede borrar un cliente
-- que ya tiene facturas,para no perder el historial (antes era CASCADE y eso
-- estaba mal,se perdian las facturas si se borraba el cliente)
-- numero_factura es el numero secuencial con formato,unico
-- subtotal/iva/total se calculan solos a partir del detalle,no se escriben a mano
CREATE TABLE facturas (
    id_factura SERIAL PRIMARY KEY,
    numero_factura VARCHAR(20) UNIQUE NOT NULL,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente) ON DELETE RESTRICT,
    subtotal NUMERIC(10, 2) NOT NULL,
    iva NUMERIC(10, 2) NOT NULL,
    total NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('Pagada', 'Pendiente', 'Anulada')),
    fecha DATE NOT NULL DEFAULT CURRENT_DATE
);

-- detalle de cada factura: que productos,cuantos,y a que precio se vendieron
-- precio_unitario se guarda aca (no se toma de productos.precio),asi si el precio
-- del producto cambia despues,las facturas viejas no se alteran
-- ON DELETE RESTRICT en id_producto: no se puede borrar un producto que ya se vendio
CREATE TABLE detalle_factura (
    id_detalle SERIAL PRIMARY KEY,
    id_factura INTEGER NOT NULL REFERENCES facturas(id_factura) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL REFERENCES productos(id_producto) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
);

-- datos de ejemplo
INSERT INTO proveedores (nombre, producto, telefono, correo, direccion) VALUES
('Indurama', 'Cocinas', '072805000', 'ventas@indurama.com', 'Av. Amazonas y Colon, Cuenca'),
('Mabe Ecuador', 'Refrigeración', '042201000', 'contacto@mabe.com.ec', 'Via a Daule km 8, Guayaquil'),
('LG Electronics', 'Televisores', '023963000', 'info@lg.com.ec', 'Av. Republica del Salvador, Quito');

INSERT INTO productos (nombre, descripcion, categoria, precio, stock, id_proveedor) VALUES
('Cocina a gas 4 hornillas', 'Cocina a gas de acero inoxidable con encendido automatico', 'Cocinas', 285.99, 8, 1),
('Refrigeradora 300L', 'Refrigeradora No Frost de 300 litros,color plateado', 'Refrigeración', 649.00, 3, 2),
('Televisor LED 50 pulgadas', 'Smart TV LED 50 pulgadas,resolucion 4K', 'Televisores', 399.50, 0, 3),
('Lavadora automatica 16kg', 'Lavadora de carga superior,16 kilogramos,varios programas', 'Lavado', 459.00, 5, NULL),
('Licuadora industrial', 'Licuadora de alta potencia,jarra de vidrio de 2 litros', 'Cocina', 65.00, 12, NULL);

INSERT INTO clientes (nombre, correo, telefono, cedula, direccion) VALUES
('Juan Perez', 'juan.perez@example.com', '0991234567', '1712345678', 'Av. 6 de Diciembre, Quito'),
('Maria Lopez', 'maria.lopez@example.com', '0987654321', '0923456789', 'Cdla. Kennedy, Guayaquil'),
('Carlos Mera', 'carlos.mera@example.com', '0965412378', '1834567890', 'Barrio Central, Lago Agrio');

-- usuario administrador inicial. la contraseña real se genera aparte (nunca en texto plano)
-- y se actualiza con un UPDATE despues de correr este script,ver instrucciones
INSERT INTO usuarios (usuario, password, nombre, rol, activo) VALUES
('admin', 'scrypt:32768:8:1$FydHcdLr6cARj3CQ$499e542e39235209fd5f0ba827e360ff81736c5ac67b6ecf825fd2d1e2a91dc3972f810b9adc3e44c3beef16d9c71378dbd00243cf955db217f230696d61f842', 'Victor Garofalo', 'administrador', TRUE);
