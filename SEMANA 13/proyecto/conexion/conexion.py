# conexion/conexion.py
# aca se centraliza la conexion a la base de datos postgresql
# app.py importa obtener_conexion() desde aca,en vez de que cada ruta se conecte por su cuenta

import psycopg2
import psycopg2.extras

# datos de conexion a la base de datos local
# ADVERTENCIA: en un proyecto real esto nunca se deja escrito asi en el codigo,
# se pone en variables de entorno. aca se deja simple porque es un proyecto academico,
# pero NUNCA subas tu contraseña real de postgres a un repositorio publico de github
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'electrocasa'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'  # <-- cambia esto por tu propia contraseña de postgres


def obtener_conexion():
    # psycopg2.connect abre la conexion con el servidor de postgresql
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


def obtener_cursor_dict(conn):
    # este cursor especial devuelve cada fila como si fuera un diccionario,
    # asi en las plantillas se puede seguir usando producto.nombre igual que con sqlite
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
