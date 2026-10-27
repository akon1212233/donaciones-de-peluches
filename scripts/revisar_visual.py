"""Prueba opcional del navegador sobre la BD temporal de scripts/probar.py."""
from pathlib import Path
import os
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / 'tests'))
from test_app import AplicacionTest

AplicacionTest.setUpClass()
caso = AplicacionTest()
caso.setUp()
from flask_app import app
from flask_app.models.peluche import Peluche

# Datos ficticios exclusivos de la prueba, similares a la referencia.
miyagi = caso.registrar(nombre='Miyagi')
caso.donar(nombre='Pikachu')
for nombre, peluche in [('Juan', 'Oso de Peluche'), ('Andrea', 'Gatito Peluchón'), ('Elizabeth', 'Mickey Mouse')]:
    cliente = app.test_client()
    caso.registrar(cliente, f'{nombre.lower()}@example.com', nombre)
    caso.donar(cliente, peluche)
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    puerto = sock.getsockname()[1]
base = f'http://127.0.0.1:{puerto}'
carpeta = root / 'docs/capturas'
carpeta.mkdir(exist_ok=True)
with (root / '.venv/preview.log').open('w') as log:
    servidor = subprocess.Popen([str(root / '.venv/bin/gunicorn'), '--bind', f'127.0.0.1:{puerto}',
                                 '--workers', '2', 'server:app'], cwd=root, env=os.environ,
                                stdout=log, stderr=log)
    try:
        for intento in range(100):
            try:
                with urlopen(base + '/salud') as respuesta:
                    assert respuesta.status == 200
                break
            except Exception:
                if servidor.poll() is not None:
                    raise RuntimeError('Gunicorn no inició; revisa .venv/preview.log')
                time.sleep(0.1)
        else:
            raise RuntimeError('No respondió el servidor.')
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            pagina = navegador.new_page(viewport={'width': 1280, 'height': 900})
            errores = []
            pagina.on('pageerror', lambda error: errores.append(str(error)))
            pagina.goto(base)
            pagina.screenshot(path=str(carpeta / 'registro.png'), full_page=True)
            pagina.locator('#login-email').fill('ana@example.com')
            pagina.locator('#login-password').fill('secreto')
            pagina.get_by_role('button', name='Iniciar Sesión', exact=True).click()
            pagina.wait_for_url(base + '/dashboard')
            assert pagina.get_by_role('heading', name='Bienvenido Miyagi').is_visible()
            fila = pagina.locator('.donation-row').filter(has_text='Gatito Peluchón')
            fila.get_by_role('button', name='Adoptar', exact=True).click()
            pagina.wait_for_url(base + '/dashboard')
            assert pagina.locator('.donation-row').filter(has_text='Gatito Peluchón').get_by_text('ADOPTADO', exact=True).is_visible()
            pagina.screenshot(path=str(carpeta / 'dashboard.png'), full_page=True)
            pagina.get_by_role('link', name='Donar Peluche', exact=True).click()
            pagina.screenshot(path=str(carpeta / 'nueva.png'), full_page=True)
            pagina.locator('#nombre').fill('Minion')
            pagina.locator('#descripcion').fill('Peluche amarillo, limpio y listo para una nueva familia.')
            pagina.get_by_role('button', name='Guardar', exact=True).click()
            pagina.wait_for_url(base + '/dashboard')
            fila = pagina.locator('.donation-row').filter(has_text='Minion')
            fila.get_by_role('link', name='Editar', exact=True).click()
            assert pagina.locator('#nombre').input_value() == 'Minion'
            pagina.screenshot(path=str(carpeta / 'editar.png'), full_page=True)
            pagina.locator('#descripcion').fill('Descripción actualizada.')
            pagina.get_by_role('button', name='Guardar', exact=True).click()
            pagina.wait_for_url(base + '/dashboard')
            pagina.locator('.donation-row').filter(has_text='Gatito Peluchón').get_by_role('link', name='Ver', exact=True).click()
            assert pagina.get_by_text('Miyagi Prueba', exact=True).is_visible()
            assert pagina.get_by_text('Visitas: 1', exact=True).is_visible()
            pagina.reload()
            assert pagina.get_by_text('Visitas: 2', exact=True).is_visible()
            pagina.screenshot(path=str(carpeta / 'detalle.png'), full_page=True)
            pagina.set_viewport_size({'width': 375, 'height': 812})
            for ruta in ('/dashboard', '/nueva'):
                pagina.goto(base + ruta)
                assert pagina.evaluate('document.documentElement.scrollWidth <= innerWidth'), ruta
            pagina.goto(base + '/dashboard')
            pagina.screenshot(path=str(carpeta / 'movil.png'), full_page=True)
            pagina.get_by_role('button', name='Cerrar Sesión', exact=True).click()
            pagina.wait_for_url(base + '/')
            assert pagina.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert not errores, errores
            diagrama = navegador.new_page(viewport={'width': 1100, 'height': 620})
            diagrama.set_content('<html><body style="margin:0">' + (root / 'docs/DER.svg').read_text() + '</body></html>')
            diagrama.screenshot(path=str(root / 'docs/DER.png'))
            navegador.close()
        print('Navegador: login, creación, edición, adopción, visitas, salida y móvil OK; Gunicorn con 2 workers OK.')
    finally:
        servidor.terminate()
        servidor.wait(timeout=20)
        AplicacionTest.tearDownClass()
