import re
from functools import wraps

from flask import abort, flash, g, redirect, session, url_for

from flask_app.models.peluche import Peluche
from flask_app.models.usuario import Usuario


EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def sesion_requerida(view):
    """Exige una sesión válida y deja el usuario disponible en g.user."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("usuario_id")
        if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id <= 0:
            session.clear()
            flash("Debes iniciar sesión para continuar.", "error")
            return redirect(url_for("index"))

        user = Usuario.get_by_id(user_id)
        if user is False:
            abort(503, description="No se pudo consultar el usuario.")
        if user is None:
            session.clear()
            flash("Vuelve a iniciar sesión.", "error")
            return redirect(url_for("index"))

        g.user = user
        return view(*args, **kwargs)

    return wrapped


def validar_registro(data):
    """Devuelve una lista con los errores del registro."""
    errors = []
    nombre = data.get("nombre", "").strip()
    apellido = data.get("apellido", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirmation = data.get("confirm_password", "")

    if not 2 <= len(nombre) <= 100:
        errors.append("El nombre debe tener entre 2 y 100 caracteres.")
    if not 2 <= len(apellido) <= 100:
        errors.append("El apellido debe tener entre 2 y 100 caracteres.")
    if len(email) > 150 or not EMAIL_REGEX.fullmatch(email):
        errors.append("Ingresa un correo electrónico válido.")
    else:
        user = Usuario.get_by_email(email)
        if user is False:
            errors.append("No se pudo comprobar el correo.")
        elif user is not None:
            errors.append("El correo ya está registrado.")

    if not password.strip():
        errors.append("La contraseña es obligatoria.")
    elif len(password.encode("utf-8")) > 72:
        errors.append("La contraseña es demasiado larga. Usa una más corta.")
    if password != confirmation:
        errors.append("Las contraseñas no coinciden.")
    return errors


def validar_peluche(data, exclude_id=None):
    """Valida creación y edición, permitiendo conservar el nombre actual."""
    errors = []
    nombre = data.get("nombre", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not 1 <= len(nombre) <= 100:
        errors.append("El nombre del peluche debe tener entre 1 y 100 caracteres.")
    else:
        existing = Peluche.get_by_name(nombre, exclude_id=exclude_id)
        if existing is False:
            errors.append("No se pudo comprobar el nombre.")
        elif existing is not None:
            errors.append("Ya existe un peluche con ese nombre.")
    if not descripcion:
        errors.append("La descripción no puede estar vacía.")
    elif len(descripcion.encode("utf-8")) > 65535:
        errors.append("La descripción es demasiado larga.")
    return errors


def es_donador(peluche, user_id):
    return peluche.id_donador == user_id


def obtener_peluche(id_peluche):
    """Distingue un peluche inexistente de un error de base de datos."""
    peluche = Peluche.get_by_id(id_peluche)
    if peluche is False:
        abort(503, description="No se pudo consultar el peluche.")
    if peluche is None:
        abort(404, description="El peluche no existe.")
    return peluche


def mostrar_errores(errors):
    for error in errors:
        flash(error, "error")
