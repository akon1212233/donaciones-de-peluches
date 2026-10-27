from flask_app.config.mysqlconnection import connectToMySQL


class Peluche:
    def __init__(self, data):
        self.id_peluche = data["id_peluche"]
        self.nombre = data["nombre"]
        self.descripcion = data["descripcion"]
        self.id_estado = data["id_estado"]
        self.id_donador = data["id_donador"]
        self.id_adoptante = data["id_adoptante"]
        self.visitas = data["visitas"]

    @classmethod
    def save(cls, data):
        """Guarda una donación y devuelve su ID o False si falla."""
        query = """
            INSERT INTO peluches (nombre, descripcion, id_donador)
            VALUES (%(nombre)s, %(descripcion)s, %(id_donador)s);
        """
        return connectToMySQL().query_db(query, data)

    @classmethod
    def get_all(cls):
        """Devuelve una lista de peluches o False si falla la consulta."""
        query = "SELECT * FROM peluches ORDER BY id_peluche DESC;"
        results = connectToMySQL().query_db(query)
        if results is False:
            return False
        return [cls(row) for row in results]

    @classmethod
    def get_by_id(cls, id_peluche):
        """Devuelve un Peluche, None si no existe o False si falla."""
        query = "SELECT * FROM peluches WHERE id_peluche = %(id_peluche)s;"
        results = connectToMySQL().query_db(query, {"id_peluche": id_peluche})
        if results is False:
            return False
        return cls(results[0]) if results else None

    @classmethod
    def get_by_name(cls, nombre, exclude_id=None):
        """Busca un nombre, excluyendo opcionalmente el peluche que se edita.

        Devuelve un Peluche, None si no existe o False si falla.
        """
        query = "SELECT * FROM peluches WHERE nombre = %(nombre)s"
        data = {"nombre": nombre}
        if exclude_id is not None:
            query += " AND id_peluche != %(exclude_id)s"
            data["exclude_id"] = exclude_id
        results = connectToMySQL().query_db(query + ";", data)
        if results is False:
            return False
        return cls(results[0]) if results else None

    @classmethod
    def update(cls, data):
        """Actualiza nombre y descripción solo si el usuario es el donador.

        id_donador debe proceder de la sesión, no del formulario.
        Devuelve las filas afectadas o False si falla.
        """
        query = """
            UPDATE peluches
            SET nombre = %(nombre)s, descripcion = %(descripcion)s
            WHERE id_peluche = %(id_peluche)s AND id_donador = %(id_donador)s;
        """
        return connectToMySQL().query_db(query, data)

    @classmethod
    def delete(cls, id_peluche, id_donador):
        """Borra solo si id_donador corresponde al usuario de la sesión.

        Devuelve las filas afectadas o False si falla.
        """
        query = """
            DELETE FROM peluches
            WHERE id_peluche = %(id_peluche)s AND id_donador = %(id_donador)s;
        """
        data = {"id_peluche": id_peluche, "id_donador": id_donador}
        return connectToMySQL().query_db(query, data)

    @classmethod
    def adopt(cls, id_peluche, id_adoptante):
        """Asigna el adoptante de la sesión solo si el peluche está disponible.

        Devuelve las filas afectadas o False si falla.
        """
        query = """
            UPDATE peluches
            SET id_adoptante = %(id_adoptante)s, id_estado = 2
            WHERE id_peluche = %(id_peluche)s
                AND id_adoptante IS NULL AND id_estado = 1
                AND id_donador != %(id_adoptante)s;
        """
        data = {"id_peluche": id_peluche, "id_adoptante": id_adoptante}
        return connectToMySQL().query_db(query, data)

    @classmethod
    def increment_views(cls, id_peluche):
        """Suma una visita y devuelve las filas afectadas o False si falla."""
        query = """
            UPDATE peluches SET visitas = visitas + 1
            WHERE id_peluche = %(id_peluche)s;
        """
        return connectToMySQL().query_db(query, {"id_peluche": id_peluche})
