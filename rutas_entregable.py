from flask import Blueprint, render_template, request, redirect, url_for
import requests

rutas_entregable = Blueprint("rutas_entregable", __name__)

# 📌 Configuración base
API_BASE = "http://localhost:5031/api"
TABLA = "entregable"     # 👈 Nombre de la tabla en tu API
NOMBRE_CLAVE = "id"      # 👈 Nombre de la columna clave

# ------------------- LISTAR entregables -------------------
@rutas_entregable.route("/entregable", methods=["GET"])
def entregable():
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        entregables = data.get("datos", []) if isinstance(data, dict) else data
    except Exception as e:
        print("Error al obtener entregables:", e)
        entregables = []
    return render_template("entregable.html", entregables=entregables, entregable=None, modo="crear")


# ------------------- CREAR entregable -------------------
@rutas_entregable.route("/entregable/crear", methods=["POST"])
def crear_entregable():
    try:
        payload = {
            "codigo": request.form.get("codigo"),
            "titulo": request.form.get("titulo"),
            "descripcion": request.form.get("descripcion"),
            "fecha_inicio": request.form.get("fecha_inicio"),
            "fecha_fin_prevista": request.form.get("fecha_fin_prevista"),
            "fecha_modificacion": request.form.get("fecha_modificacion"),
            "fecha_finalizacion": request.form.get("fecha_finalizacion")
        }
        r = requests.post(f"{API_BASE}/{TABLA}", json=payload, timeout=10)
        if r.status_code not in (200, 201):
            return f"Error al crear: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error al crear entregable: {e}"

    return redirect(url_for("rutas_entregable.entregable"))


# ------------------- BUSCAR entregable -------------------
@rutas_entregable.route("/entregable/buscar", methods=["POST"])
def buscar_entregable():
    id_buscar = request.form.get("id_buscar") or request.form.get("id")
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        datos = data.get("datos", []) if isinstance(data, dict) else data
        item = next((t for t in datos if str(t.get("id")) == str(id_buscar)), None)
        if item:
            return render_template("entregable.html", entregables=datos, entregable=item, modo="actualizar")
    except Exception as e:
        return f"Error en la búsqueda: {e}"

    return render_template(
        "entregable.html",
        entregables=requests.get(f"{API_BASE}/{TABLA}").json().get("datos", []),
        entregable=None,
        mensaje="Entregable no encontrado",
        modo="crear"
    )


# ------------------- ACTUALIZAR entregable -------------------
@rutas_entregable.route("/entregable/actualizar", methods=["POST"])
def actualizar_entregable():
    id_actual = request.form.get("id")
    datos = {
        "codigo": request.form.get("codigo"),
        "titulo": request.form.get("titulo"),
        "descripcion": request.form.get("descripcion"),
        "fecha_inicio": request.form.get("fecha_inicio"),
        "fecha_fin_prevista": request.form.get("fecha_fin_prevista"),
        "fecha_modificacion": request.form.get("fecha_modificacion"),
        "fecha_finalizacion": request.form.get("fecha_finalizacion")
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
                return redirect(url_for("rutas_entregable.entregable"))
        except Exception as e:
            print(f"PUT a {endpoint} falló: {e}")

    if last_resp is not None:
        return f"No se pudo actualizar. Última respuesta: {last_resp.status_code} - {last_resp.text}"
    return "No se pudo actualizar el entregable."


# ------------------- ELIMINAR entregable -------------------
@rutas_entregable.route("/entregable/eliminar/<int:id>", methods=["POST"])
def eliminar_entregable(id):
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
                return redirect(url_for("rutas_entregable.entregable"))
        except Exception as e:
            detalles.append((endpoint, "EXC", str(e)))
            print(f"DELETE a {endpoint} falló: {e}")

    detalle_str = "\n".join([f"{ep} -> {st} - {tx}" for ep, st, tx in detalles])
    return f"No se pudo eliminar el entregable. Intentos:\n{detalle_str}"
