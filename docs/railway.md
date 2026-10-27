# Publicar en Railway

Estado: configuración preparada; todavía no hay despliegue público verificado.

## 1. Repositorio

Publica este repositorio en tu GitHub. Comprueba que `.env`, `.venv`, claves y archivos de pruebas locales no estén incluidos. Se incluyen `.env.example`, `requirements.txt`, `.python-version` y `railway.json`.

## 2. Proyecto y MySQL

Crea un proyecto en Railway con un servicio MySQL y un servicio de aplicación conectado al repositorio de GitHub. El nombre del servicio de BD usado en los ejemplos es `MySQL`; ajústalo si elegiste otro.

En las variables del servicio **de la aplicación**, configura:

```text
MYSQL_HOST=${{MySQL.MYSQLHOST}}
MYSQL_PORT=${{MySQL.MYSQLPORT}}
MYSQL_USER=${{MySQL.MYSQLUSER}}
MYSQL_PASSWORD=${{MySQL.MYSQLPASSWORD}}
MYSQL_DB=${{MySQL.MYSQLDATABASE}}
APP_DEBUG=false
COOKIE_SECURE=true
```

Agrega `SECRET_KEY` con una clave aleatoria de 64 caracteres hexadecimales generada localmente. No copies el ejemplo vacío. No cambies la clave en cada despliegue, porque invalidaría las sesiones. Railway proporciona `PORT`.

La conexión de la aplicación usa la red privada de Railway. No pongas `localhost`: Flask y MySQL son servicios distintos.

## 3. Crear las tablas antes del primer arranque saludable

El chequeo `/salud` comprueba el acceso a `estados`; si aún no hay tablas, devolverá 503. Inicializa primero la base vacía de Railway con [squema.sql](../flask_app/SQL/squema.sql):

1. En MySQL Workbench configura una conexión con los datos **públicos** de conexión de tu servicio MySQL (host y puerto del TCP Proxy, usuario y contraseña).
2. Selecciona la base indicada por `MYSQLDATABASE`, normalmente `railway`.
3. Abre y ejecuta el script. No crea otra base ni cambia la base seleccionada.
4. Confirma las tablas `usuarios`, `estados` y `peluches`, y los dos estados iniciales.

No importes el esquema en una base con datos existentes. No uses los nombres internos `*.railway.internal` desde tu computador, ya que solo resuelven dentro de Railway.

## 4. Arranque y enlace público

El archivo `railway.json` establece:

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 2 server:app
```

El servidor de desarrollo no se usa. Despliega la aplicación y revisa que `/salud` pase. En Settings → Networking → Public Networking, selecciona **Generate Domain** para obtener la URL HTTPS. Si se solicita un puerto, usa el que escucha el proceso según `PORT`.

## 5. Verificación de entrega

- Abre la URL desde una ventana privada y desde un teléfono.
- Registra dos usuarios; dona con uno y adopta con el otro.
- Confirma edición/borrado exclusivos del donador, estado ADOPTADO y nombre del adoptante.
- Abre el detalle dos veces y comprueba el incremento de visitas.
- Cierra sesión y confirma que no se puede entrar a `/dashboard` directamente.
- Comprueba CSS, errores de validación y ausencia de depuración.
- Reinicia el servicio de aplicación y verifica que los datos persisten en MySQL.
- Agrega la URL pública al README y entrégala junto con el repositorio.

## Diagnóstico

| Síntoma | Revisar |
|---|---|
| Error de variable al iniciar | Variables `MYSQL_*` y `SECRET_KEY` en el servicio Flask |
| 503 en `/salud` | Credenciales, red privada, esquema importado y servicio MySQL activo |
| Formulario vencido/CSRF | Clave estable, cookies habilitadas, HTTPS con `COOKIE_SECURE=true`, recargar formulario |
| 502 | Proceso Gunicorn, puerto `PORT` y escucha en `0.0.0.0` |
| Tablas inexistentes | Base seleccionada al importar; no usar otra base local por error |

Fuentes oficiales consultadas para esta configuración:

- [Flask en Railway](https://docs.railway.com/guides/flask)
- [MySQL](https://docs.railway.com/databases/mysql)
- [Variables y referencias entre servicios](https://docs.railway.com/variables)
- [Dominio público](https://docs.railway.com/networking/domains/working-with-domains)
