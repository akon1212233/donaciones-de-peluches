"""Crea el esquema solo si la base configurada está vacía.

Uso: python -m scripts.init_db
La base debe existir. No elimina ni migra tablas existentes.
"""
from pathlib import Path

from flask_app import app
from flask_app.config.mysqlconnection import MySQLConnection


def main():
    with app.app_context():
        conexion = MySQLConnection.get_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute('SHOW TABLES')
                if cursor.fetchall():
                    raise SystemExit('La base contiene tablas. No se modificó; revisa su esquema manualmente.')
                ruta = Path(__file__).resolve().parent.parent / 'flask_app/SQL/squema.sql'
                sql = '\n'.join(line for line in ruta.read_text().splitlines() if not line.startswith('--'))
                for sentencia in sql.split(';'):
                    if sentencia.strip():
                        cursor.execute(sentencia)
            conexion.commit()
            print('Esquema creado: usuarios, estados y peluches.')
        finally:
            conexion.close()


if __name__ == '__main__':
    main()
