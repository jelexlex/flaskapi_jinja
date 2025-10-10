from flask import Blueprint, render_template, request, redirect, url_for
import requests

rutas_entregable = Blueprint("rutas_entregable", __name__)

API_BASE = "http://localhost:5031/api"
TABLA = "entregable"
NOMBRE_CLAVE = "id"

# ------------------- LISTAR ENTREGABLES -------------------
@rutas_entregable.route("/entregable", methods=["GET"])
def entregable():
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        # soportar respuesta con o sin "datos"
        entregables = data.get("datos", data) if isinstance(data, dict) else data

        # si la API devolviera un solo objeto como dict -> convertir a lista
        if isinstance(entregables, dict):
            entregables = [entregables]

        # normalizar fechas (quitar la parte "T..." si existe y convertir null a '')
        def clean_fecha(f):
            if not f:
                return ""
            try:
                return f.split("T")[0] if isinstance(f, str) and "T" in f else str(f)
            except:
                return str(f)

        for e in entregables:
            e["fecha_inicio"] = clean_fecha(e.get("fecha_inicio"))
            e["fecha_fin_prevista"] = clean_fecha(e.get("fecha_fin_prevista"))
            e["fecha_modificacion"] = clean_fecha(e.get("fecha_modificacion"))
            e["fecha_finalizacion"] = clean_fecha(e.get("fecha_finalizacion"))

    except Exception as exc:
        print("Error al obtener entregables:", exc)
        entregables = []

    return render_template("entregable.html",
                           entregables=entregables,
                           entregable=None,
                           modo="crear",
                           mensaje=None)


# ------------------- CREAR ENTREGABLE -------------------
@rutas_entregable.route("/entregable/crear", methods=["POST"])
def crear_entregable():
    try:
        payload = {
            "codigo": request.form.get("codigo"),
            "titulo": request.form.get("titulo"),
            "descripcion": request.form.get("descripcion"),
            "fecha_inicio": request.form.get("fecha_inicio") or None,
            "fecha_fin_prevista": request.form.get("fecha_fin_prevista") or None,
            "fecha_modificacion": request.form.get("fecha_modificacion") or None,
            "fecha_finalizacion": request.form.get("fecha_finalizacion") or None
        }
        r = requests.post(f"{API_BASE}/{TABLA}", json=payload, timeout=10)
        if r.status_code not in (200, 201):
            return f"Error al crear: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error al crear entregable: {e}"

    return redirect(url_for("rutas_entregable.entregable"))


# ------------------- BUSCAR ENTREGABLE -------------------
@rutas_entregable.route("/entregable/buscar", methods=["POST"])
def buscar_entregable():
    id_buscar = request.form.get("id_buscar") or request.form.get("id")
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        datos = data.get("datos", []) if isinstance(data, dict) else data

        # normalizar (si viene dict único)
        if isinstance(datos, dict):
            datos = [datos]

        item = next((t for t in datos if str(t.get("id")) == str(id_buscar)), None)
        # limpiar fechas del item y de la lista
        def clean_fecha(f):
            if not f:
                return ""
            try:
                return f.split("T")[0] if isinstance(f, str) and "T" in f else str(f)
            except:
                return str(f)

        for d in datos:
            d["fecha_inicio"] = clean_fecha(d.get("fecha_inicio"))
            d["fecha_fin_prevista"] = clean_fecha(d.get("fecha_fin_prevista"))
            d["fecha_modificacion"] = clean_fecha(d.get("fecha_modificacion"))
            d["fecha_finalizacion"] = clean_fecha(d.get("fecha_finalizacion"))

        if item:
            # también limpiar el item concreto
            item["fecha_inicio"] = clean_fecha(item.get("fecha_inicio"))
            item["fecha_fin_prevista"] = clean_fecha(item.get("fecha_fin_prevista"))
            item["fecha_modificacion"] = clean_fecha(item.get("fecha_modificacion"))
            item["fecha_finalizacion"] = clean_fecha(item.get("fecha_finalizacion"))

            return render_template("entregable.html",
                                   entregables=datos,
                                   entregable=item,
                                   modo="actualizar",
                                   mensaje=None)
    except Exception as e:
        return f"Error en la búsqueda: {e}"

    # si no encontrado, recargar lista y mostrar mensaje
    try:
        lista = requests.get(f"{API_BASE}/{TABLA}").json().get("datos", [])
    except:
        lista = []
    return render_template("entregable.html",
                           entregables=lista,
                           entregable=None,
                           modo="crear",
                           mensaje="Entregable no encontrado")


# ------------------- ACTUALIZAR ENTREGABLE -------------------
@rutas_entregable.route("/entregable/actualizar", methods=["POST"])
def actualizar_entregable():
    id_actual = request.form.get("id") or request.form.get("id_buscar")
    datos = {
        "codigo": request.form.get("codigo"),
        "titulo": request.form.get("titulo"),
        "descripcion": request.form.get("descripcion"),
        "fecha_inicio": request.form.get("fecha_inicio") or None,
        "fecha_fin_prevista": request.form.get("fecha_fin_prevista") or None,
        "fecha_modificacion": request.form.get("fecha_modificacion") or None,
        "fecha_finalizacion": request.form.get("fecha_finalizacion") or None
    }

    posibles_endpoints = [
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id_actual}",  # /api/entregable/id/5
        f"{API_BASE}/{TABLA}/{id_actual}",                 # /api/entregable/5
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


# ------------------- ELIMINAR ENTREGABLE -------------------
@rutas_entregable.route("/entregable/eliminar/<int:id>", methods=["POST"])
def eliminar_entregable(id):
    posibles_endpoints = [
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id}",
        f"{API_BASE}/{TABLA}/{id}",
        f"{API_BASE}/{TABLA}/{NOMBRE_CLAVE}/{id}?esquema=por%20defecto"
    ]

    detalles = []
    for endpoint in posibles_endpoints:
        try:
            r = requests.delete(endpoint, timeout=10)
            detalles.append((endpoint, r.status_code, r.text))
            if r.status_code in (200, 204):
                return redirect(url_for("rutas_entregable.entregable"))
        except Exception as e:
            detalles.append((endpoint, "EXC", str(e)))
            print(f"DELETE a {endpoint} falló: {e}")

    detalle_str = "\n".join([f"{ep} -> {st} - {tx}" for ep, st, tx in detalles])
    return f"No se pudo eliminar el entregable. Intentos:\n{detalle_str}"
