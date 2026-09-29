# models.py
# clase Usuario que necesita flask-login para manejar la sesion
# UserMixin da los metodos que pide flask-login (is_authenticated,is_active,get_id,etc)

from flask_login import UserMixin
from conexion.conexion import obtener_conexion, obtener_cursor_dict


class Usuario(UserMixin):
    def __init__(self, id, usuario, password, nombre, rol, activo):
        self.id = id
        self.usuario = usuario
        self.password = password
        self.nombre = nombre
        self.rol = rol
        self.activo = activo

    # flask-login solo deja entrar a un usuario si is_active es True
    # asi un usuario desactivado no puede seguir usando una sesion vieja
    @property
    def is_active(self):
        return self.activo

    @property
    def es_administrador(self):
        return self.rol == 'administrador'

    @staticmethod
    def _desde_fila(fila):
        if fila is None:
            return None
        return Usuario(fila['id'], fila['usuario'], fila['password'], fila['nombre'], fila['rol'], fila['activo'])

    @staticmethod
    def get(id_usuario):
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (id_usuario,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()
        return Usuario._desde_fila(fila)

    @staticmethod
    def buscar_por_usuario(nombre_usuario):
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM usuarios WHERE usuario = %s', (nombre_usuario,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()
        return Usuario._desde_fila(fila)
