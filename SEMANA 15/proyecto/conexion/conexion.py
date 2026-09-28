# conexion/conexion.py
# aca se centraliza la conexion a la base de datos postgresql
# app.py importa obtener_conexion() desde aca,en vez de que cada ruta se conecte por su cuenta
#
# funciona tanto en la computadora local como en Render:
# - en Render existe la variable de entorno DATABASE_URL y se usa esa
# - en la computadora local no existe,entonces se usan los datos de abajo

import os
import psycopg2
import psycopg2.extras

# datos de conexion para cuando se corre local
# ADVERTENCIA: nunca subas tu contraseña real de postgres a un repositorio publico de github
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'electrocasa'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'  # <-- cambia esto por tu propia contraseña de postgres

DATABASE_URL = os.environ.get('DATABASE_URL')


def obtener_conexion():
    if DATABASE_URL:
        # desplegado en render
        conn = psycopg2.connect(DATABASE_URL)
    else:
        # corriendo local
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    return conn


def obtener_cursor_dict(conn):
    # cursor que devuelve cada fila como diccionario,para usar producto.nombre en las plantillas
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
