from flask import Blueprint, render_template, request, redirect, url_for
import requests

# Crear el Blueprint
rutas_estado = Blueprint("rutas_estado", __name__)

# URL base de la API
API_BASE = "http://localhost:5031/api"
TABLA = "estado"
NOMBRE_CLAVE = "id"

# ------------------- LISTAR ESTADOS -------------------
@rutas_estado.route("/estado", methods=["GET"])
def estado():
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        estados = data.get("datos", data) if isinstance(data, dict) else data

        if isinstance(estados, dict):
            estados = [estados]
    except Exception as exc:
        print("Error al obtener estados:", exc)
        estados = []

    return render_template("estado.html",
                           estados=estados,
                           estado=None,
                           modo="crear",
                           mensaje=None)


# ------------------- CREAR ESTADO -------------------
@rutas_estado.route("/estado/crear", methods=["POST"])
def crear_estado():
    try:
        payload = {
            "nombre": request.form.get("nombre"),
            "descripcion": request.form.get("descripcion")
        }
        r = requests.post(f"{API_BASE}/{TABLA}", json=payload, timeout=10)
        if r.status_code not in (200, 201):
            return f"Error al crear estado: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error al crear estado: {e}"

    return redirect(url_for("rutas_estado.estado"))


# ------------------- BUSCAR ESTADO -------------------
@rutas_estado.route("/estado/buscar", methods=["POST"])
def buscar_estado():
    id_buscar = request.form.get("id_buscar")
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        estados = data.get("datos", data) if isinstance(data, dict) else data
        if isinstance(estados, dict):
            estados = [estados]

        item = next((t for t in estados if str(t.get("id")) == str(id_buscar)), None)

        if item:
            return render_template("estado.html",
                                   estados=estados,
                                   estado=item,
                                   modo="actualizar",
                                   mensaje=None)
    except Exception as e:
        return f"Error en la búsqueda: {e}"

    return render_template("estado.html",
                           estados=estados,
                           estado=None,
                           modo="crear",
                           mensaje="Estado no encontrado")


# ------------------- ACTUALIZAR ESTADO -------------------
@rutas_estado.route("/estado/actualizar", methods=["POST"])
def actualizar_estado():
    id_actual = request.form.get("id")
    datos = {
        "nombre": request.form.get("nombre"),
        "descripcion": request.form.get("descripcion")
    }

    posibles_endpoints = [
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id_actual}",
        f"{API_BASE}/{TABLA}/{id_actual}"
    ]

    last_resp = None
    for endpoint in posibles_endpoints:
        try:
            r = requests.put(endpoint, json=datos, timeout=10)
            last_resp = r
            if r.status_code in (200, 204):
                return redirect(url_for("rutas_estado.estado"))
        except Exception as e:
            print(f"PUT a {endpoint} falló: {e}")

    if last_resp is not None:
        return f"No se pudo actualizar. Última respuesta: {last_resp.status_code} - {last_resp.text}"
    return "No se pudo actualizar el estado."


# ------------------- ELIMINAR ESTADO -------------------
@rutas_estado.route("/estado/eliminar/<int:id>", methods=["POST"])
def eliminar_estado(id):
    posibles_endpoints = [
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id}",
        f"{API_BASE}/{TABLA}/{id}"
    ]

    for endpoint in posibles_endpoints:
        try:
            r = requests.delete(endpoint, timeout=10)
            if r.status_code in (200, 204):
                return redirect(url_for("rutas_estado.estado"))
        except Exception as e:
            print(f"DELETE a {endpoint} falló: {e}")

    return "No se pudo eliminar el estado."
