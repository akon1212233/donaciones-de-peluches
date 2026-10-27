from flask import abort, flash, g, redirect, render_template, request, session, url_for

from flask_app import app, bcrypt
from flask_app.controllers.functions import (
    mostrar_errores,
    obtener_peluche,
    es_donador,
    sesion_requerida,
    validar_peluche,
    validar_registro,
)
from flask_app.models.peluche import Peluche
from flask_app.models.usuario import Usuario

@app.route("/", methods=["GET"])
def index():
    if session.get("usuario_id"):
        return redirect(url_for("dashboard"))
    return render_template("registro.html", datos={})


@app.route("/registro", methods=["POST"])
def registro():
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "apellido": request.form.get("apellido", "").strip(),
        "email": request.form.get("email", "").strip().lower(),
    }
    errors = validar_registro(request.form)
    if errors:
        mostrar_errores(errors)
        return render_template("registro.html", datos=datos), 400

    datos["password_hash"] = bcrypt.generate_password_hash(
        request.form["password"]
    ).decode("utf-8")
    user_id = Usuario.save(datos)
    if user_id is False or not user_id:
        datos.pop("password_hash")
        flash("No se pudo registrar el usuario.", "error")
        return render_template("registro.html", datos=datos), 503

    session.clear()
    session["usuario_id"] = user_id
    flash("Registro exitoso.", "success")
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not email or not password or len(password.encode("utf-8")) > 72:
        flash("Ingresa un correo y una contraseña válidos.", "error")
        return redirect(url_for("index"))

    user = Usuario.get_by_email(email)
    if user is False:
        abort(503, description="No se pudo iniciar sesión.")
    valid_password = False
    if user is not None:
        try:
            valid_password = bcrypt.check_password_hash(user.password_hash, password)
        except (ValueError, TypeError):
            valid_password = False
    if not valid_password:
        flash("Correo o contraseña incorrectos.", "error")
        return redirect(url_for("index"))

    session.clear()
    session["usuario_id"] = user.id_usuario
    return redirect(url_for("dashboard"))


@app.route("/cerrar_sesion", methods=["POST"])
def cerrar_sesion():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard", methods=["GET"])
@sesion_requerida
def dashboard():
    peluches = Peluche.get_all()
    if peluches is False:
        abort(503, description="No se pudieron cargar las donaciones.")

    usuarios = {g.user.id_usuario: g.user}
    for peluche in peluches:
        if peluche.id_donador not in usuarios:
            user = Usuario.get_by_id(peluche.id_donador)
            if user is False:
                abort(503, description="No se pudieron cargar los donadores.")
            usuarios[peluche.id_donador] = user
    return render_template(
        "dashboard.html", usuario=g.user, peluches=peluches, usuarios=usuarios
    )


@app.route("/nueva", methods=["GET", "POST"])
@sesion_requerida
def nueva_donacion():
    datos = {}
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
        }
        errors = validar_peluche(datos)
        if errors:
            mostrar_errores(errors)
            return render_template(
                "nueva_donacion.html", datos=datos
            ), 400

        datos["id_donador"] = g.user.id_usuario
        result = Peluche.save(datos)
        if result is False or not result:
            flash("No se pudo guardar la donación. Verifica que el nombre siga disponible.", "error")
            return render_template(
                "nueva_donacion.html", datos=datos
            ), 503
        flash("Donación creada.", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "nueva_donacion.html", datos=datos
    )


@app.route("/editar/<int:id_peluche>", methods=["GET", "POST"])
@sesion_requerida
def editar_donacion(id_peluche):
    peluche = obtener_peluche(id_peluche)
    if not es_donador(peluche, g.user.id_usuario):
        abort(403, description="Solo puedes editar tus propias donaciones.")

    datos = {"nombre": peluche.nombre, "descripcion": peluche.descripcion}
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
        }
        errors = validar_peluche(datos, exclude_id=id_peluche)
        if errors:
            mostrar_errores(errors)
            return render_template(
                "editar_donacion.html", datos=datos, peluche=peluche
            ), 400

        datos.update(id_peluche=id_peluche, id_donador=g.user.id_usuario)
        result = Peluche.update(datos)
        if result is False:
            flash("No se pudo actualizar la donación. Verifica que el nombre siga disponible.", "error")
            return render_template(
                "editar_donacion.html", datos=datos, peluche=peluche
            ), 503
        flash("Donación guardada.", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "editar_donacion.html", datos=datos, peluche=peluche
    )


@app.route("/borrar/<int:id_peluche>", methods=["POST"])
@sesion_requerida
def borrar_donacion(id_peluche):
    peluche = obtener_peluche(id_peluche)
    if not es_donador(peluche, g.user.id_usuario):
        abort(403, description="Solo puedes borrar tus propias donaciones.")
    result = Peluche.delete(id_peluche, g.user.id_usuario)
    if result is False:
        abort(503, description="No se pudo borrar la donación.")
    if result == 0:
        abort(404, description="La donación ya no está disponible.")
    flash("Donación eliminada.", "success")
    return redirect(url_for("dashboard"))


@app.route("/ver/<int:id_peluche>", methods=["GET"])
@sesion_requerida
def ver_donacion(id_peluche):
    peluche = obtener_peluche(id_peluche)
    donador = Usuario.get_by_id(peluche.id_donador)
    adoptante = None
    if peluche.id_adoptante is not None:
        adoptante = Usuario.get_by_id(peluche.id_adoptante)
    if donador is False or adoptante is False:
        abort(503, description="No se pudieron cargar los datos del usuario.")
    result = Peluche.increment_views(id_peluche)
    if result is False:
        abort(503, description="No se pudo registrar la visita.")
    if result == 0:
        abort(404, description="El peluche ya no existe.")
    peluche = obtener_peluche(id_peluche)
    return render_template(
        "detalle_peluche.html", peluche=peluche, donador=donador,
        adoptante=adoptante, usuario=g.user
    )


@app.route("/adoptar/<int:id_peluche>", methods=["POST"])
@sesion_requerida
def adoptar_peluche(id_peluche):
    peluche = obtener_peluche(id_peluche)
    if es_donador(peluche, g.user.id_usuario):
        abort(403)
    result = Peluche.adopt(id_peluche, g.user.id_usuario)
    if result is False:
        abort(503, description="No se pudo completar la adopción.")
    if result == 0:
        flash("El peluche ya no está disponible para adoptar.", "error")
    else:
        flash("Peluche adoptado.", "success")
    return redirect(url_for("dashboard"))


@app.get('/salud')
def salud():
    from flask_app.config.mysqlconnection import connectToMySQL
    resultado = connectToMySQL().query_db('SELECT id_estado FROM estados LIMIT 1')
    return ({'estado': 'ok'}, 200) if resultado else ({'estado': 'no disponible'}, 503)
