-- sql/esquema.sql
-- este script crea desde cero las tablas principales del proyecto ElectroCasa
-- se puede correr completo en pgAdmin (Query Tool) sobre la base "electrocasa"
-- para recrear la estructura si hiciera falta

DROP TABLE IF EXISTS facturas;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS proveedores;

-- proveedores va primero,porque productos depende de esta tabla (clave foranea)
CREATE TABLE proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    producto VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

-- productos tiene id_proveedor como clave foranea,relacionada con proveedores
-- puede ser NULL si un producto todavia no tiene proveedor asignado
CREATE TABLE productos (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    stock INTEGER NOT NULL,
    id_proveedor INTEGER REFERENCES proveedores(id_proveedor)
);

CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

CREATE TABLE facturas (
    id_factura SERIAL PRIMARY KEY,
    id_cliente INTEGER REFERENCES clientes(id_cliente),
    total NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(20) NOT NULL
);

-- datos iniciales de proveedores,se cargan primero porque productos los necesita
INSERT INTO proveedores (nombre, producto, telefono) VALUES
('Indurama', 'Cocinas', '07 280 5000'),
('Mabe Ecuador', 'Refrigeración', '04 220 1000'),
('LG Electronics', 'Televisores', '02 396 3000');

-- productos de ejemplo,algunos ya relacionados con su proveedor mediante id_proveedor
-- los dos ultimos se dejan sin proveedor asignado (NULL),para poder probar tambien ese caso
INSERT INTO productos (nombre, descripcion, categoria, stock, id_proveedor) VALUES
('Cocina a gas 4 hornillas', 'Cocina a gas de acero inoxidable con encendido automatico', 'Cocinas', 8, 1),
('Refrigeradora 300L', 'Refrigeradora No Frost de 300 litros,color plateado', 'Refrigeración', 3, 2),
('Televisor LED 50 pulgadas', 'Smart TV LED 50 pulgadas,resolucion 4K', 'Televisores', 0, 3),
('Lavadora automatica 16kg', 'Lavadora de carga superior,16 kilogramos,varios programas', 'Lavado', 5, NULL),
('Licuadora industrial', 'Licuadora de alta potencia,jarra de vidrio de 2 litros', 'Cocina', 12, NULL);

-- clientes de ejemplo (este modulo todavia no usa base de datos,se deja preparado)
INSERT INTO clientes (nombre, correo, telefono) VALUES
('Juan Perez', 'juan.perez@example.com', '099 123 4567'),
('Maria Lopez', 'maria.lopez@example.com', '098 765 4321'),
('Carlos Mera', 'carlos.mera@example.com', '096 541 2378');

-- facturas de ejemplo,relacionadas con clientes mediante id_cliente
INSERT INTO facturas (id_cliente, total, estado) VALUES
(1, 650.50, 'Pagada'),
(2, 890.00, 'Pendiente'),
(3, 120.99, 'Pagada');
