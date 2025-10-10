from flask import Blueprint, render_template, request, redirect, url_for
import requests


rutas_tipo_producto = Blueprint("rutas_tipo_producto", __name__)


API_BASE = "http://localhost:5031/api"
TABLA = "tipo_producto"
NOMBRE_CLAVE = "id"

# ------------------- LISTAR -------------------
@rutas_tipo_producto.route("/tipo_producto", methods=["GET"])
def tipo_producto():
    try:
        r = requests.get(f"{API_BASE}/{TABLA}")
        data = r.json()
        tipos = data.get("datos", []) if isinstance(data, dict) else data
    except Exception as e:
        print("⚠️ Error al obtener tipos de producto:", e)
        tipos = []
    return render_template("tipo_producto.html", tipos=tipos, tipo=None, modo="crear")

# ------------------- CREAR -------------------
@rutas_tipo_producto.route("/tipo_producto/crear", methods=["POST"])
def crear_tipo_producto():
    try:
        payload = {
            "nombre": request.form.get("nombre"),
            "descripcion": request.form.get("descripcion")
        }
        r = requests.post(f"{API_BASE}/{TABLA}", json=payload, timeout=10)
        if r.status_code not in (200, 201):
            return f"❌ Error al crear tipo de producto: {r.status_code} - {r.text}"
    except Exception as e:
        return f"⚠️ Error al crear tipo de producto: {e}"

    return redirect(url_for("rutas_tipo_producto.tipo_producto"))

# ------------------- BUSCAR -------------------
@rutas_tipo_producto.route("/tipo_producto/buscar", methods=["POST"])
def buscar_tipo_producto():
    id_buscar = request.form.get("id_buscar")
    try:
        r = requests.get(f"{API_BASE}/{TABLA}")
        data = r.json()
        tipos = data.get("datos", []) if isinstance(data, dict) else data
        tipo = next((t for t in tipos if str(t.get("id")) == str(id_buscar)), None)
        if tipo:
            return render_template("tipo_producto.html", tipos=tipos, tipo=tipo, modo="actualizar")
    except Exception as e:
        return f"⚠️ Error al buscar tipo de producto: {e}"

    return render_template(
        "tipo_producto.html",
        tipos=tipos,
        tipo=None,
        mensaje="Tipo de producto no encontrado",
        modo="crear"
    )

# ------------------- ACTUALIZAR -------------------
@rutas_tipo_producto.route("/tipo_producto/actualizar", methods=["POST"])
def actualizar_tipo_producto():
    id_actual = request.form.get("id")
    datos = {
        "nombre": request.form.get("nombre"),
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
                return redirect(url_for("rutas_tipo_producto.tipo_producto"))
        except Exception as e:
            print(f"⚠️ PUT a {endpoint} falló: {e}")

    if last_resp is not None:
        return f"❌ No se pudo actualizar. Última respuesta: {last_resp.status_code} - {last_resp.text}"
    return "❌ No se pudo actualizar el tipo de producto. Sin respuesta del servidor."

# ------------------- ELIMINAR -------------------
@rutas_tipo_producto.route("/tipo_producto/eliminar/<int:id>", methods=["POST"])
def eliminar_tipo_producto(id):
    posibles_endpoints = [
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id}",
        f"{API_BASE}/{TABLA}/{id}",
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id}?esquema=por%20defecto"
    ]

    last_resp = None
    detalles = []
    for endpoint in posibles_endpoints:
        try:
            r = requests.delete(endpoint, timeout=10)
            detalles.append((endpoint, r.status_code, r.text))
            last_resp = r
            if r.status_code in (200, 204):
                return redirect(url_for("rutas_tipo_producto.tipo_producto"))
        except Exception as e:
            detalles.append((endpoint, "EXC", str(e)))
            print(f"⚠️ DELETE a {endpoint} falló: {e}")

    detalle_str = "\n".join([f"{ep} -> {st} - {tx}" for ep, st, tx in detalles])
    return f"❌ No se pudo eliminar el tipo de producto. Intentos:\n{detalle_str}"
