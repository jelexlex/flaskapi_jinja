from flask import Blueprint, render_template, request, redirect, url_for
import requests

rutas_tipo_responsable = Blueprint("rutas_tipo_responsable", __name__)


API_BASE = "http://localhost:5031/api"
TABLA = "tipo_responsable"     
NOMBRE_CLAVE = "id"            

# ------------------- LISTAR tipos de responsable -------------------
@rutas_tipo_responsable.route("/tipo_responsable", methods=["GET"])
def tipo_responsable():
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        tipos = data.get("datos", []) if isinstance(data, dict) else data
    except Exception as e:
        print("Error al obtener tipos de responsable:", e)
        tipos = []
    return render_template("tipo_responsable.html", tipos=tipos, tipo=None, modo="crear")


# ------------------- CREAR tipo de responsable -------------------
@rutas_tipo_responsable.route("/tipo_responsable/crear", methods=["POST"])
def crear_tipo_responsable():
    try:
        payload = {
            "titulo": request.form.get("titulo"),
            "descripcion": request.form.get("descripcion")
        }
        r = requests.post(f"{API_BASE}/{TABLA}", json=payload, timeout=10)
        if r.status_code not in (200, 201):
            return f"Error al crear: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error al crear tipo de responsable: {e}"

    return redirect(url_for("rutas_tipo_responsable.tipo_responsable"))


# ------------------- BUSCAR tipo de responsable -------------------
@rutas_tipo_responsable.route("/tipo_responsable/buscar", methods=["POST"])
def buscar_tipo_responsable():
    id_buscar = request.form.get("id_buscar") or request.form.get("id")
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        datos = data.get("datos", []) if isinstance(data, dict) else data
        tipo = next((t for t in datos if str(t.get("id")) == str(id_buscar)), None)
        if tipo:
            return render_template("tipo_responsable.html", tipos=datos, tipo=tipo, modo="actualizar")
    except Exception as e:
        return f"Error en la búsqueda: {e}"

    return render_template("tipo_responsable.html",
                           tipos=requests.get(f"{API_BASE}/{TABLA}").json().get("datos", []),
                           tipo=None,
                           mensaje="Tipo de responsable no encontrado",
                           modo="crear")


# ------------------- ACTUALIZAR tipo de responsable -------------------
@rutas_tipo_responsable.route("/tipo_responsable/actualizar", methods=["POST"])
def actualizar_tipo_responsable():
    id_actual = request.form.get("id")
    datos = {
        "titulo": request.form.get("titulo"),
        "descripcion": request.form.get("descripcion")
    }

    posibles_endpoints = [
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id_actual}",
        f"{API_BASE}/{TABLA}/{id_actual}",
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id_actual}?esquema=por%20defecto"
    ]

    last_resp = None
    for endpoint in posibles_endpoints:
        try:
            r = requests.put(endpoint, json=datos, timeout=10)
            last_resp = r
            if r.status_code in (200, 204):
                return redirect(url_for("rutas_tipo_responsable.tipo_responsable"))
        except Exception as e:
            print(f"PUT a {endpoint} falló: {e}")

    if last_resp is not None:
        return f"No se pudo actualizar. Última respuesta: {last_resp.status_code} - {last_resp.text}"
    return "No se pudo actualizar el tipo de responsable."


# ------------------- ELIMINAR tipo de responsable -------------------
@rutas_tipo_responsable.route("/tipo_responsable/eliminar/<int:id>", methods=["POST"])
def eliminar_tipo_responsable(id):
    posibles_endpoints = [
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id}",
        f"{API_BASE}/{TABLA}/{id}",
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id}?esquema=por%20defecto",
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id}"
    ]

    last_resp = None
    detalles = []
    for endpoint in posibles_endpoints:
        try:
            r = requests.delete(endpoint, timeout=10)
            detalles.append((endpoint, r.status_code, r.text))
            last_resp = r
            if r.status_code in (200, 204):
                return redirect(url_for("rutas_tipo_responsable.tipo_responsable"))
        except Exception as e:
            detalles.append((endpoint, "EXC", str(e)))
            print(f"DELETE a {endpoint} falló: {e}")

    detalle_str = "\n".join([f"{ep} -> {st} - {tx}" for ep, st, tx in detalles])
    return f"No se pudo eliminar el tipo de responsable. Intentos:\n{detalle_str}"
