# ===============================================================
# Módulo: rutas_usuarios.py
# Descripción: Maneja las rutas para listar, crear, buscar,
# actualizar y eliminar usuarios. Se conecta a la API en C#.
# ===============================================================

from flask import Blueprint, render_template, request, redirect, url_for
import requests

rutas_usuarios = Blueprint("rutas_usuarios", __name__)
API_URL = "http://localhost:5031/api/usuario"  # Endpoint base de la API

# ===============================================================
# RUTA: LISTAR USUARIOS
# ===============================================================
@rutas_usuarios.route("/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        respuesta = requests.get(API_URL)
        usuarios = respuesta.json().get("datos", [])
    except Exception as e:
        print("❌ Error al conectar con la API:", e)
        usuarios = []

    return render_template("usuarios.html", usuarios=usuarios, usuario=None, modo="crear")


# ===============================================================
# RUTA: BUSCAR USUARIO POR EMAIL
# ===============================================================
@rutas_usuarios.route("/usuarios/buscar", methods=["POST"])
def buscar_usuario():
    email = request.form.get("email_buscar")

    try:
        respuesta = requests.get(f"{API_URL}/email/{email}")
        if respuesta.status_code == 200:
            datos = respuesta.json().get("datos", [])
            if datos:
                usuario = datos[0]
                usuarios = requests.get(API_URL).json().get("datos", [])
                return render_template("usuarios.html", usuarios=usuarios, usuario=usuario, modo="actualizar")
    except Exception as e:
        print("❌ Error al buscar usuario:", e)

    usuarios = requests.get(API_URL).json().get("datos", [])
    return render_template("usuarios.html", usuarios=usuarios, usuario=None, mensaje="Usuario no encontrado", modo="crear")


# ===============================================================
# RUTA: CREAR USUARIO (con contraseña encriptada)
# ===============================================================
@rutas_usuarios.route("/usuarios", methods=["POST"])
def crear_usuario():
    datos = {
        "email": request.form.get("email"),
        "contrasena": request.form.get("contrasena"),
        "ruta_avatar": request.form.get("ruta_avatar"),
        "activo": True  # por defecto activo
    }

    try:
        r = requests.post(f"{API_URL}?camposEncriptar=contrasena", json=datos)
        if r.status_code not in (200, 201):
            return f"❌ Error al crear usuario: {r.status_code} - {r.text}"
    except Exception as e:
        return f"❌ Error al crear usuario: {e}"

    return redirect(url_for("rutas_usuarios.listar_usuarios"))


# ===============================================================
# RUTA: ACTUALIZAR USUARIO (por id)
# ===============================================================
@rutas_usuarios.route("/usuarios/actualizar/<int:id_usuario>", methods=["POST"])
def actualizar_usuario(id_usuario):
    datos = {
        "contrasena": request.form.get("contrasena"),
        "ruta_avatar": request.form.get("ruta_avatar"),
        "activo": request.form.get("activo") == "true"
    }

    try:
        r = requests.put(f"{API_URL}/id/{id_usuario}?camposEncriptar=contrasena", json=datos)
        if r.status_code not in (200, 204):
            return f"❌ No se pudo actualizar el usuario. Código: {r.status_code} - {r.text}"
    except Exception as e:
        return f"❌ Error al actualizar usuario: {e}"

    return redirect(url_for("rutas_usuarios.listar_usuarios"))


# ===============================================================
# RUTA: ELIMINAR USUARIO (por id)
# ===============================================================
@rutas_usuarios.route("/usuarios/eliminar/<int:id_usuario>", methods=["POST"])
def eliminar_usuario(id_usuario):
    try:
        # Estructura real: /api/{tabla}/{nombreClave}/{valorClave}
        endpoint = f"http://localhost:5031/api/usuario/id/{id_usuario}"
        r = requests.delete(endpoint)

        if r.status_code not in (200, 204):
            return f"❌ No se pudo eliminar el usuario. Código: {r.status_code} - {r.text}"

    except Exception as e:
        return f"❌ Error al eliminar usuario: {e}"

    return redirect(url_for("rutas_usuarios.listar_usuarios"))
