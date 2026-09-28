-- sql/esquema.sql
-- este script crea desde cero las tablas del proyecto ElectroCasa
-- se corre completo en pgAdmin (Query Tool) sobre la base de datos del proyecto

DROP TABLE IF EXISTS facturas;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS usuarios;

-- tabla de usuarios para el login
-- usuario es UNIQUE para que no se repitan nombres,y password guarda solo el hash
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    producto VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

-- productos se relaciona con proveedores mediante id_proveedor (clave foranea)
-- si se elimina un proveedor,el producto se queda sin proveedor (NULL)
CREATE TABLE productos (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    stock INTEGER NOT NULL,
    id_proveedor INTEGER REFERENCES proveedores(id_proveedor) ON DELETE SET NULL
);

CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

-- facturas se relaciona con clientes mediante id_cliente (clave foranea)
-- si se elimina un cliente,tambien se eliminan sus facturas
CREATE TABLE facturas (
    id_factura SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente) ON DELETE CASCADE,
    total NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE
);

-- datos de ejemplo
INSERT INTO proveedores (nombre, producto, telefono) VALUES
('Indurama', 'Cocinas', '07 280 5000'),
('Mabe Ecuador', 'Refrigeración', '04 220 1000'),
('LG Electronics', 'Televisores', '02 396 3000');

INSERT INTO productos (nombre, descripcion, categoria, stock, id_proveedor) VALUES
('Cocina a gas 4 hornillas', 'Cocina a gas de acero inoxidable con encendido automatico', 'Cocinas', 8, 1),
('Refrigeradora 300L', 'Refrigeradora No Frost de 300 litros,color plateado', 'Refrigeración', 3, 2),
('Televisor LED 50 pulgadas', 'Smart TV LED 50 pulgadas,resolucion 4K', 'Televisores', 0, 3),
('Lavadora automatica 16kg', 'Lavadora de carga superior,16 kilogramos,varios programas', 'Lavado', 5, NULL),
('Licuadora industrial', 'Licuadora de alta potencia,jarra de vidrio de 2 litros', 'Cocina', 12, NULL);

INSERT INTO clientes (nombre, correo, telefono) VALUES
('Juan Perez', 'juan.perez@example.com', '099 123 4567'),
('Maria Lopez', 'maria.lopez@example.com', '098 765 4321'),
('Carlos Mera', 'carlos.mera@example.com', '096 541 2378');

INSERT INTO facturas (id_cliente, total, estado) VALUES
(1, 650.50, 'Pagada'),
(2, 890.00, 'Pendiente'),
(3, 120.99, 'Pagada');

-- usuario administrador inicial,con la contraseña ya protegida con hash
INSERT INTO usuarios (usuario, password) VALUES
('admin', 'scrypt:32768:8:1$PNkAUXWZkN9yLIco$91b29c29dc97a2ed1f2a2e322c5fd5dd37046386e227442849e42af782a27585454093f5d6299d173093a44cc17be115564051fad937c034deab6b8d8b0186fe');
