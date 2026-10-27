import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect, CSRFError

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ['SECRET_KEY'],
    MYSQL_HOST=os.environ['MYSQL_HOST'],
    MYSQL_PORT=int(os.environ['MYSQL_PORT']),
    MYSQL_USER=os.environ['MYSQL_USER'],
    MYSQL_PASSWORD=os.environ['MYSQL_PASSWORD'],
    MYSQL_DB=os.environ['MYSQL_DB'],
    MYSQL_SOCKET=os.getenv('MYSQL_SOCKET'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
    MAX_CONTENT_LENGTH=128 * 1024,
)
if len(app.secret_key) < 32:
    raise RuntimeError('SECRET_KEY debe tener al menos 32 caracteres aleatorios.')

bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)


@app.errorhandler(CSRFError)
def formulario_vencido(error):
    return render_template('error.html', codigo=400,
                           mensaje='El formulario venció. Vuelve a la página e inténtalo otra vez.'), 400


def mostrar_error(error):
    mensajes = {
        400: 'La solicitud no es válida.',
        403: 'No tienes permiso para realizar esta acción.',
        404: 'La página o el peluche ya no existe.',
        405: 'Esta acción debe realizarse desde el formulario correspondiente.',
        413: 'El formulario supera el tamaño permitido.',
        500: 'Ocurrió un error. Inténtalo nuevamente más tarde.',
        503: 'No pudimos acceder a los datos. Inténtalo nuevamente más tarde.',
    }
    return render_template('error.html', codigo=error.code, mensaje=mensajes[error.code]), error.code


for codigo in (400, 403, 404, 405, 413, 500, 503):
    app.register_error_handler(codigo, mostrar_error)

from flask_app.controllers import router
