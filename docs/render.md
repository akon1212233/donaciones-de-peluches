# Publicar en Render

Repositorio: https://github.com/akon1212233/donaciones-de-peluches

## Base de datos necesaria

La aplicación usa MySQL. Render Postgres no es compatible con estas consultas y el conector PyMySQL: no reemplaces la conexión con una URL PostgreSQL.

Puedes usar una base MySQL externa o desplegar MySQL como servicio privado en Render con disco persistente, que requiere recursos de pago. El `render.yaml` solo configura Flask en el plan gratuito; **no crea ni incluye una base de datos**. La elección del alojamiento de MySQL está pendiente.

Antes del despliegue, crea una base vacía e importa `flask_app/SQL/squema.sql` desde el cliente del proveedor o MySQL Workbench. También puedes configurar las variables locales para esa base vacía y ejecutar `python -m scripts.init_db` si el proveedor permite acceso desde tu equipo. El inicializador se niega a modificar bases que ya contengan tablas.

Para un MySQL privado de Render, usa la consola del servicio para importar el SQL y conecta Flask con el host interno del servicio; ese host no es accesible desde tu computador. Si el proveedor externo exige TLS o un certificado CA, debemos configurar esa conexión antes de publicar; nunca desactives la verificación del certificado para solucionarlo.

## Opción A: Blueprint

En Render selecciona New → Blueprint y conecta el repositorio. Render leerá `render.yaml` y pedirá las variables `MYSQL_*`. Generará `SECRET_KEY` y configurará las cookies para HTTPS. Completa la BD y su esquema antes de desplegar: `/salud` devuelve 503 mientras no pueda consultar las tablas.

## Opción B: Web Service manual

Selecciona New → Web Service y conecta el repositorio. Configura:

| Campo | Valor |
|---|---|
| Name | `donaciones-de-peluches` |
| Branch | `main` |
| Language | Python 3 |
| Root Directory | Vacío, el proyecto está en la raíz |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --bind 0.0.0.0:$PORT --workers 2 server:app` |
| Health Check Path | `/salud` |

El archivo `.python-version` selecciona Python 3.14. Para la web puedes elegir Free; esto no cubre el coste de la base MySQL. No uses Static Site ni `python server.py`.

Agrega en Environment:

- `SECRET_KEY`: clave aleatoria estable de al menos 32 caracteres. Genera una con `python -c "import secrets; print(secrets.token_hex(32))"`.
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`: datos reales del alojamiento MySQL.
- `APP_DEBUG=false`.
- `COOKIE_SECURE=true`.

Render proporciona `PORT`. No uses `localhost` como servidor MySQL: Flask y la BD se ejecutan en servicios distintos. No subas `.env` al repositorio.

## Verificación

Al completarse el despliegue, abre la dirección HTTPS `*.onrender.com` asignada al servicio. Verifica registro, login, donación, edición, adopción con un segundo usuario, visitas, borrado y cierre de sesión. Reinicia la aplicación y comprueba que los datos siguen guardados en MySQL. Agrega la URL verificada al README.

El plan gratuito de la web puede suspenderse tras 15 minutos sin tráfico; la primera carga posterior puede tardar. Su disco es efímero: no sirve para guardar MySQL ni datos persistentes de la aplicación.

## Diagnóstico

- Error al iniciar: revisa las variables obligatorias y la longitud de `SECRET_KEY`.
- 503 en `/salud`: verifica MySQL, el host/puerto, permisos de red y que se importó el esquema en la base seleccionada.
- 502: comprueba Gunicorn y que escuche en `0.0.0.0:$PORT`.
- CSRF/formulario vencido: recarga la página y verifica cookies, HTTPS y clave de sesión estable.

Fuentes oficiales:

- [Desplegar Flask](https://render.com/docs/deploy-flask)
- [Blueprint](https://render.com/docs/blueprint-spec)
- [Desplegar MySQL](https://render.com/docs/deploy-mysql)
- [Límites del plan gratuito](https://render.com/docs/free)
