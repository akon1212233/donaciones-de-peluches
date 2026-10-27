import os
import re
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pymysql

# Credenciales exclusivas de una instancia temporal; nunca se lee .env para pruebas.
os.environ.update(SECRET_KEY='clave-de-pruebas-' * 4, MYSQL_HOST='127.0.0.1', MYSQL_PORT='3306',
                  MYSQL_USER='root', MYSQL_PASSWORD='', MYSQL_DB='test_peluches_' + uuid.uuid4().hex,
                  COOKIE_SECURE='false')
from flask_app import app, bcrypt
from flask_app.models.peluche import Peluche
from flask_app.models.usuario import Usuario


@unittest.skipUnless(os.getenv('MYSQL_SOCKET'), 'Ejecuta scripts/probar.py con MariaDB instalado')
class AplicacionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=True, BCRYPT_LOG_ROUNDS=4)
        cls.db = pymysql.connect(unix_socket=os.environ['MYSQL_SOCKET'], user='root', autocommit=True)
        cls.nombre_bd = app.config['MYSQL_DB']
        with cls.db.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE `{cls.nombre_bd}` CHARACTER SET utf8mb4')
            cursor.execute(f'USE `{cls.nombre_bd}`')
            sql = Path('flask_app/SQL/squema.sql').read_text()
            sql = '\n'.join(line for line in sql.splitlines() if not line.startswith('--'))
            for sentencia in sql.split(';'):
                if sentencia.strip():
                    cursor.execute(sentencia)

    @classmethod
    def tearDownClass(cls):
        with cls.db.cursor() as cursor:
            cursor.execute(f'DROP DATABASE `{cls.nombre_bd}`')
        cls.db.close()

    def setUp(self):
        with self.db.cursor() as cursor:
            cursor.execute('DELETE FROM peluches')
            cursor.execute('DELETE FROM usuarios')
        self.cliente = app.test_client()

    def post(self, cliente, ruta, datos=None, seguir=False):
        pagina = cliente.get('/')
        if pagina.status_code == 302:
            pagina = cliente.get('/dashboard')
        token = re.search(r'name="csrf_token" value="([^"]+)"', pagina.text).group(1)
        return cliente.post(ruta, data=dict(datos or {}, csrf_token=token), follow_redirects=seguir)

    def registrar(self, cliente=None, email='ana@example.com', nombre='Ana'):
        cliente = cliente or self.cliente
        respuesta = self.post(cliente, '/registro', dict(nombre=nombre, apellido='Prueba', email=email,
                                                        password='secreto', confirm_password='secreto'))
        self.assertEqual(respuesta.status_code, 302)
        with cliente.session_transaction() as sesion:
            return sesion['usuario_id']

    def donar(self, cliente=None, nombre='Oso de Peluche'):
        cliente = cliente or self.cliente
        self.assertEqual(self.post(cliente, '/nueva', dict(nombre=nombre, descripcion='Suave y limpio')).status_code, 302)
        with app.app_context():
            return Peluche.get_by_name(nombre).id_peluche

    def test_registro_login_hash_y_salida(self):
        self.registrar()
        with app.app_context():
            usuario = Usuario.get_by_email('ana@example.com')
            self.assertNotEqual(usuario.password_hash, 'secreto')
            self.assertTrue(bcrypt.check_password_hash(usuario.password_hash, 'secreto'))
        self.assertIn('Bienvenido Ana', self.cliente.get('/dashboard').text)
        self.post(self.cliente, '/cerrar_sesion')
        self.assertEqual(self.cliente.get('/dashboard').status_code, 302)
        self.assertIn('incorrectos', self.post(self.cliente, '/login', dict(email='ana@example.com', password='mal'), True).text)
        self.assertEqual(self.post(self.cliente, '/login', dict(email='ANA@example.com', password='secreto')).status_code, 302)

    def test_validaciones_registro(self):
        base = dict(nombre='Ana', apellido='Prueba', email='ana@example.com', password='secreto', confirm_password='secreto')
        for cambio in ({'nombre':'A'}, {'apellido':' '}, {'email':'invalido'}, {'confirm_password':'otra'},
                       {'password':' '}, {'password':'ñ'*40, 'confirm_password':'ñ'*40}):
            with self.subTest(cambio=cambio):
                self.assertEqual(self.post(self.cliente, '/registro', dict(base, **cambio)).status_code, 400)
        self.registrar()
        otro = app.test_client()
        self.assertEqual(self.post(otro, '/registro', base).status_code, 400)

    def test_sesion_y_csrf(self):
        for ruta in ('/dashboard', '/nueva', '/editar/1', '/ver/1'):
            self.assertEqual(self.cliente.get(ruta).status_code, 302)
        self.assertEqual(self.cliente.post('/registro').status_code, 400)
        self.registrar()
        id_peluche = self.donar()
        self.assertEqual(self.cliente.get(f'/borrar/{id_peluche}').status_code, 405)
        self.assertEqual(self.cliente.post(f'/borrar/{id_peluche}').status_code, 400)
        with self.cliente.session_transaction() as sesion:
            sesion['usuario_id'] = 9999999
        self.assertEqual(self.cliente.get('/dashboard').status_code, 302)

    def test_crud_y_validaciones(self):
        self.registrar()
        id_peluche = self.donar()
        for datos in ({'nombre':'', 'descripcion':'Conservar esta descripción'},
                      {'nombre':'Nuevo', 'descripcion':'  '}):
            respuesta = self.post(self.cliente, '/nueva', datos)
            self.assertEqual(respuesta.status_code, 400)
            if datos['descripcion'].strip():
                self.assertIn(datos['descripcion'], respuesta.text)
        self.assertIn('ya existe', self.post(self.cliente, '/nueva', dict(nombre='oso de peluche', descripcion='Descripción')).text.lower())
        pagina = self.cliente.get(f'/editar/{id_peluche}')
        self.assertIn('value="Oso de Peluche"', pagina.text)
        self.assertIn('Suave y limpio', pagina.text)
        self.assertEqual(self.post(self.cliente, f'/editar/{id_peluche}', dict(nombre='Oso de Peluche', descripcion='Actualizado')).status_code, 302)
        self.donar(nombre='Otro peluche')
        self.assertEqual(self.post(self.cliente, f'/editar/{id_peluche}', dict(nombre='Otro peluche', descripcion='Texto')).status_code, 400)
        self.assertEqual(self.post(self.cliente, f'/editar/{id_peluche}', dict(nombre='Oso de Peluche', descripcion='')).status_code, 400)
        self.post(self.cliente, f'/borrar/{id_peluche}')
        self.assertEqual(self.cliente.get(f'/ver/{id_peluche}').status_code, 404)
        with app.app_context():
            self.assertIsNone(Peluche.get_by_id(id_peluche))

    def test_propiedad_y_adopcion(self):
        self.registrar()
        id_peluche = self.donar()
        otro = app.test_client()
        self.registrar(otro, 'pedro@example.com', 'Pedro')
        self.assertNotIn('>Editar<', otro.get('/dashboard').text)
        self.assertEqual(otro.get(f'/editar/{id_peluche}').status_code, 403)
        self.assertEqual(self.post(otro, f'/editar/{id_peluche}', dict(nombre='Cambio', descripcion='Texto')).status_code, 403)
        self.assertEqual(self.post(otro, f'/borrar/{id_peluche}').status_code, 403)
        self.assertEqual(self.post(self.cliente, f'/adoptar/{id_peluche}').status_code, 403)
        self.assertEqual(self.post(otro, f'/adoptar/{id_peluche}').status_code, 302)
        self.assertIn('ADOPTADO', otro.get('/dashboard').text)
        self.assertIn('Pedro Prueba', self.cliente.get(f'/ver/{id_peluche}').text)
        self.assertIn('ya no está disponible', self.post(otro, f'/adoptar/{id_peluche}', seguir=True).text)

    def test_adopcion_concurrente(self):
        self.registrar()
        id_peluche = self.donar()
        ids = [self.registrar(app.test_client(), f'persona{i}@example.com') for i in range(2)]
        def adoptar(id_usuario):
            with app.app_context():
                return Peluche.adopt(id_peluche, id_usuario)
        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(adoptar, ids))
        self.assertEqual(sorted(resultados), [0, 1])

    def test_visitas_y_escape_html(self):
        self.registrar()
        id_peluche = self.donar(nombre='<script>alert(1)</script>')
        for numero in (1, 2, 3):
            respuesta = self.cliente.get(f'/ver/{id_peluche}')
            self.assertIn(f'Visitas: <strong>{numero}</strong>', respuesta.text)
            self.assertNotIn('<script>alert(1)</script>', respuesta.text)
        with app.app_context():
            self.assertEqual(Peluche.get_by_id(id_peluche).visitas, 3)

    def test_fallos_bd_y_recursos_inexistentes(self):
        self.registrar()
        self.assertEqual(self.cliente.get('/ver/999999').status_code, 404)
        with patch.object(Peluche, 'get_by_id', return_value=False):
            self.assertEqual(self.cliente.get('/ver/1').status_code, 503)
        with patch.object(Peluche, 'get_all', return_value=False):
            respuesta = self.cliente.get('/dashboard')
            self.assertEqual(respuesta.status_code, 503)
            self.assertNotIn('Traceback', respuesta.text)
        self.assertEqual(self.cliente.get('/salud').status_code, 200)
        with patch.object(Usuario, 'get_by_id', return_value=False):
            self.assertEqual(self.cliente.get('/dashboard').status_code, 503)


if __name__ == '__main__':
    unittest.main()
