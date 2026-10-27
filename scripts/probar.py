"""Ejecuta la integración en una instancia MariaDB temporal sin puerto TCP.

Requiere mariadb-install-db y mariadbd. No lee ni modifica la BD de .env.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import pymysql

root = Path(__file__).resolve().parent.parent
for comando in ('mariadb-install-db', 'mariadbd'):
    if not shutil.which(comando):
        raise SystemExit(f'Falta {comando}. Instala MariaDB para ejecutar las pruebas.')

with tempfile.TemporaryDirectory(prefix='peluches-test-') as carpeta:
    base = Path(carpeta)
    socket = str(base / 'mysql.sock')
    with (base / 'mysql.log').open('w+') as log:
        subprocess.run(['mariadb-install-db', '--no-defaults', f'--datadir={base / "data"}',
                        '--auth-root-authentication-method=normal', '--skip-test-db'],
                       stdout=log, stderr=log, check=True)
        proceso = subprocess.Popen(['mariadbd', '--no-defaults', f'--datadir={base / "data"}',
                                    f'--socket={socket}', f'--pid-file={base / "mysql.pid"}',
                                    '--skip-networking'], stdout=log, stderr=log)
        try:
            for intento in range(100):
                try:
                    conexion = pymysql.connect(unix_socket=socket, user='root')
                    conexion.close()
                    break
                except pymysql.MySQLError:
                    if proceso.poll() is not None:
                        log.seek(0)
                        raise RuntimeError(log.read())
                    time.sleep(0.1)
            else:
                raise RuntimeError('MariaDB no inició a tiempo.')
            resultado = subprocess.CompletedProcess([], 0)
            if '--visual-only' not in sys.argv:
                resultado = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                                           cwd=root, env=dict(os.environ, MYSQL_SOCKET=socket))
            if resultado.returncode == 0 and ('--visual' in sys.argv or '--visual-only' in sys.argv):
                resultado = subprocess.run([sys.executable, 'scripts/revisar_visual.py'], cwd=root,
                                           env=dict(os.environ, MYSQL_SOCKET=socket))
        finally:
            proceso.terminate()
            proceso.wait(timeout=20)
    sys.exit(resultado.returncode)
