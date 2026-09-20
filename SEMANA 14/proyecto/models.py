# models.py
# aca esta la clase Usuario que necesita flask-login para manejar la sesion
# UserMixin le da a la clase los metodos que flask-login necesita por dentro
# (is_authenticated,is_active,get_id,etc),asi no hay que escribirlos a mano

from flask_login import UserMixin
from conexion.conexion import obtener_conexion, obtener_cursor_dict


class Usuario(UserMixin):
    def __init__(self, id, usuario, password):
        self.id = id
        self.usuario = usuario
        self.password = password

    # flask-login llama a esta funcion cada vez que necesita saber quien es
    # el usuario de la sesion activa,buscandolo por su id
    @staticmethod
    def get(id_usuario):
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (id_usuario,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()

        if fila is None:
            return None

        return Usuario(fila['id'], fila['usuario'], fila['password'])

    # se usa en el login,para buscar el usuario por su nombre y comparar la contraseña
    @staticmethod
    def buscar_por_usuario(nombre_usuario):
        conn = obtener_conexion()
        cursor = obtener_cursor_dict(conn)
        cursor.execute('SELECT * FROM usuarios WHERE usuario = %s', (nombre_usuario,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()

        if fila is None:
            return None

        return Usuario(fila['id'], fila['usuario'], fila['password'])
