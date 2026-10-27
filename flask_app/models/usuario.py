from flask_app.config.mysqlconnection import connectToMySQL


class Usuario:
    def __init__(self, data):
        self.id_usuario = data["id_usuario"]
        self.nombre = data["nombre"]
        self.apellido = data["apellido"]
        self.email = data["email"]
        self.password_hash = data["password_hash"]

    @classmethod
    def save(cls, data):
        """Guarda un usuario con su contraseña previamente hasheada."""
        query = """
            INSERT INTO usuarios (nombre, apellido, email, password_hash)
            VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password_hash)s);
        """
        return connectToMySQL().query_db(query, data)

    @classmethod
    def get_by_email(cls, email):
        """Devuelve un Usuario, None si no existe o False si falla la consulta."""
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        results = connectToMySQL().query_db(query, {"email": email})
        if results is False:
            return False
        return cls(results[0]) if results else None

    @classmethod
    def get_by_id(cls, id_usuario):
        """Devuelve un Usuario, None si no existe o False si falla la consulta."""
        query = "SELECT * FROM usuarios WHERE id_usuario = %(id_usuario)s;"
        results = connectToMySQL().query_db(query, {"id_usuario": id_usuario})
        if results is False:
            return False
        return cls(results[0]) if results else None
