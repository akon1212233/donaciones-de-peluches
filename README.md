# Donaciones de peluches

Aplicación Flask y MySQL para registrar usuarios, donar, editar, ver, borrar y adoptar peluches. Implementa los requisitos y bonus de [la consigna original](docs/requisitos.md).

## Referencia y pantallas

![Referencia del profesor](<Donación de Peluches.png>)

- `/`: registro e inicio de sesión en dos columnas.
- `/dashboard`: bienvenida, donador, enlace Ver, botones de propietario y estado de adopción.
- `/nueva`: formulario de nombre y descripción.
- `/editar/<id>`: formulario completo con valores actuales.
- `/ver/<id>`: donador, descripción, adoptante cuando corresponde y visitas.

## Ejecutar localmente

Requisitos: Python 3.14 y MySQL 8.0.16+ o MariaDB 10.6+. Las pruebas usan MariaDB.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Copia la clave generada en `SECRET_KEY` de `.env` y configura las credenciales `MYSQL_*`. No publiques `.env`. Usa un usuario de BD con permisos únicamente sobre la base del proyecto.

Crea una base vacía desde MySQL Workbench o el cliente MySQL:

```sql
CREATE DATABASE donaciones_peluches_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Inicializa las tablas y arranca la aplicación:

```bash
python -m scripts.init_db
python server.py
```

Abre `http://127.0.0.1:5000`. No se incluyen cuentas ni datos de ejemplo; registra dos usuarios para probar donación y adopción. El inicializador se niega a modificar una base que ya contenga tablas. El DDL de MySQL no es transaccional: si una importación falla a mitad, revisa el esquema antes de reintentar.

Alternativa: selecciona la base vacía e importa [squema.sql](flask_app/SQL/squema.sql) desde Workbench.

## Configuración

| Variable | Uso |
|---|---|
| `SECRET_KEY` | Clave aleatoria estable de al menos 32 caracteres; firma sesiones y formularios |
| `MYSQL_HOST`, `MYSQL_PORT` | Servidor y puerto de MySQL |
| `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB` | Usuario, contraseña y base de datos |
| `COOKIE_SECURE` | `false` en HTTP local, `true` en HTTPS de Render |
| `APP_DEBUG` | `false` por defecto; `true` solo para desarrollo local |
| `PORT` | Puerto asignado por Render; localmente 5000 por defecto |

La aplicación exige sus variables de conexión y clave al iniciar; no contiene credenciales de respaldo. Las variables del servidor tienen prioridad sobre `.env`.

## Arquitectura y reglas

- `flask_app/models/`: clases `Usuario` y `Peluche`, consultas SQL con parámetros y conversión a objetos.
- `flask_app/controllers/router.py`: rutas y coordinación de las operaciones.
- `flask_app/controllers/functions.py`: validaciones, sesión y comprobaciones reutilizables.
- `flask_app/templates/`: cada pantalla tiene su contenido y formularios; `base.html` contiene la estructura común.
- `flask_app/config/mysqlconnection.py`: apertura/cierre de conexión, transacciones y registro de errores sin credenciales.
- [DER en SVG](docs/DER.svg) y [explicación y versión Mermaid](docs/DER.md).

Registro exige nombre/apellido de 2 a 100 caracteres, correo válido y único, contraseña no vacía y confirmación coincidente. Bcrypt admite hasta 72 bytes UTF-8 y guarda exclusivamente el hash. El proyecto no impone un mínimo adicional de contraseña que no aparece en la consigna.

El nombre del peluche admite de 1 a 100 caracteres; la descripción es obligatoria y respeta la capacidad de `TEXT`. Crear y editar comparten validaciones y conservan los valores ante errores. El nombre puede conservarse al editar y es único también en la BD.

Solo el donador puede editar o borrar, incluso mediante peticiones directas. No puede adoptar su propio peluche, siguiendo los botones de la referencia. La adopción es irreversible desde la interfaz y solo se completa si sigue disponible. El donador conserva sus permisos después de una adopción, según la consigna. Cada visita autenticada válida al detalle aumenta el contador, incluyendo recargas y visitas del donador; no mide visitantes únicos.

Todos los formularios POST incluyen CSRF. Las contraseñas no se vuelven a mostrar. Jinja escapa el contenido del usuario. Los errores 400/403/404/405/413/500/503 tienen una página legible; una consulta fallida no se interpreta como un recurso inexistente.

## Pruebas

```bash
python scripts/probar.py
```

Requiere `mariadb-install-db` y `mariadbd` en el sistema. Levanta una instancia temporal sin TCP, ejecuta el SQL real y limpia los datos al terminar. No usa la BD de `.env`. Verifica registro/login/hash, validaciones, CSRF, permisos, CRUD, nombres duplicados, adopción concurrente, visitas, escape HTML y errores de BD.

Las dependencias opcionales de pruebas visuales están en `requirements-dev.txt`. El resultado de la revisión y los pendientes externos se registran en [la matriz de evaluación](docs/evaluacion.md).

## Despliegue y entrega

Sigue [la guía de Render](docs/render.md). `render.yaml` configura Gunicorn y el chequeo `/salud`, que requiere acceso a las tablas de la BD. No arranca con el servidor de desarrollo.

**URL pública: pendiente de configurar MySQL y desplegar en Render.** Tener los archivos de despliegue no equivale a una publicación. Agrega aquí el enlace verificado antes de entregar.

Entregables: código MVC, requisitos/dependencias, `.env.example`, `.gitignore`, SQL, DER, guía de ejecución y pruebas. Los porcentajes, medallas y plazos oficiales se encuentran en `docs/requisitos.md`; la nota y la elegibilidad dependen del instructor y de la entrega efectiva.

Para repetir la revisión de navegador y generar las capturas (Chrome/Chromium de Playwright):

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/probar.py --visual
```

Usa `--visual-only` para repetir únicamente la prueba de navegador. Las capturas de demostración se guardan en `docs/capturas/`; los datos se eliminan con la instancia temporal.
