import ssl

import pymysql
from flask import current_app


class MySQLConnection:
    @staticmethod
    def get_db():
        certificado = current_app.config.get('MYSQL_SSL_CA')
        contexto_ssl = ssl.create_default_context(cafile=certificado) if certificado else None
        return pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            port=current_app.config['MYSQL_PORT'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            unix_socket=current_app.config.get('MYSQL_SOCKET'),
            charset='utf8mb4',
            ssl=contexto_ssl,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,
            read_timeout=10,
            write_timeout=10,
            autocommit=False,
        )

    def query_db(self, query, data=None):
        """SELECT devuelve filas; INSERT un ID; UPDATE/DELETE filas afectadas.

        False indica un error de BD, distinto de una consulta sin resultados.
        """
        connection = None
        try:
            connection = self.get_db()
            with connection.cursor() as cursor:
                cursor.execute(query, data)
                tipo = query.lstrip().split(None, 1)[0].upper()
                if tipo == 'SELECT':
                    return cursor.fetchall()
                connection.commit()
                return cursor.lastrowid if tipo == 'INSERT' else cursor.rowcount
        except pymysql.MySQLError as error:
            # Registrar el código, sin consultas, credenciales ni datos del usuario.
            current_app.logger.error('Error de MySQL, código %s', error.args[0] if error.args else 'desconocido')
            if connection is not None:
                connection.rollback()
            return False
        finally:
            if connection is not None:
                connection.close()


def connectToMySQL():
    return MySQLConnection()
