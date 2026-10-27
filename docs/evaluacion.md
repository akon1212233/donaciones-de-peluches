# Revisión frente a la rúbrica

Esta matriz registra implementación y pruebas, no asigna una nota ni sustituye la evaluación del instructor.

| Criterio | Evidencia |
|---|---|
| Conexión y modelos | SQL ejecutado en MariaDB temporal; conexiones cerradas, parámetros SQL y fallos diferenciados |
| POO | Clases Usuario y Peluche con atributos, constructores y métodos de persistencia |
| CRUD | Crear, leer, editar con valores actuales y eliminar físicamente; probado con SQL real |
| Sesiones | Acceso protegido y usuario existente comprobado en cada ruta privada |
| HTML/Jinja | Registro, dashboard, creación, edición, detalle y errores; contenido dentro de cada plantilla |
| Validaciones | Registro, unicidad en creación/edición, espacios vacíos, longitudes, conservación de valores |
| Autenticación | Registro/login/logout, sesión renovada y rechazo de credenciales inválidas |
| Hash | Bcrypt; verificación de que la BD no contiene la contraseña original |
| MVC | Modelos separados de controladores, helpers en functions.py y vistas Jinja |
| Diseño | Distribución de la imagen; CSS local, navegación por teclado y adaptación móvil |
| Calidad | Variables privadas obligatorias, .gitignore, dependencias fijadas, documentación, pruebas y errores sin credenciales |

## Bonus

- Adoptar un peluche disponible: implementado y probado, incluida concurrencia.
- Mostrar ADOPTADO: implementado y comprobado en navegador.
- Nombre único: validación de aplicación y restricción UNIQUE en BD.
- Editar conservando el nombre: probado; rechaza el nombre de otro peluche.
- Mostrar adoptante: implementado y comprobado en el detalle.
- Contar cada visita al detalle: incremento SQL atómico y pruebas de recarga.

## Entregables

- [Consigna conservada](requisitos.md).
- [SQL](../flask_app/SQL/squema.sql).
- [DER SVG](DER.svg), [DER PNG](DER.png) y [fuente Mermaid y relaciones](DER.md).
- [README de instalación](../README.md), [.env.example](../.env.example), [.gitignore](../.gitignore).
- [Guía Railway](railway.md) y [configuración de arranque](../railway.json).
- [Pruebas](../tests/test_app.py) y [revisión de navegador](../scripts/revisar_visual.py).

## Evidencia visual

Los datos de estas capturas son ficticios y se generaron en una base temporal:

- [Registro](capturas/registro.png)
- [Dashboard](capturas/dashboard.png)
- [Nueva donación](capturas/nueva.png)
- [Edición](capturas/editar.png)
- [Detalle](capturas/detalle.png)
- [Móvil](capturas/movil.png)

## Pendientes externos antes de entregar

- Publicar el repositorio en la cuenta GitHub elegida.
- Crear/conectar Railway y MySQL, importar el esquema y desplegar.
- Verificar la URL HTTPS pública, persistencia después de reiniciar y registrar el enlace en el README.
- Confirmar con el instructor el inicio oficial, fecha límite y forma de entrega. El código no acredita el plazo ni asegura medalla o 100/100.

No se han modificado CinePedia ni el simulacro original. No se incluyen credenciales ni datos personales de pruebas.
