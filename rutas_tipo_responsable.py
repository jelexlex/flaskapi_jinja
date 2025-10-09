from flask import Blueprint, render_template, request, redirect, url_for
import requests

# 📌 URL base de la API
API_URL = "http://localhost:5031/api/tipo_responsable"

# 📌 Nombre del blueprint
rutas_tipo_responsable = Blueprint("rutas_tipo_responsable", __name__)

# ------------------- LISTAR -------------------
@rutas_tipo_responsable.route("/tipo_responsable")
def tipo_responsable():
    try:
        r = requests.get(API_URL)
        tipos = r.json() if r.status_code == 200 else []
    except Exception as e:
        tipos = []
        print(f"⚠️ Error al obtener los tipos de responsable: {e}")

    # 👇 tipo=None asegura que en la vista no se intente acceder a .id de un string
    return render_template("tipo_responsable.html", tipos=tipos, tipo=None, modo="crear", mensaje=None)


# ------------------- CREAR -------------------
@rutas_tipo_responsable.route("/tipo_responsable/crear", methods=["POST"])
def crear_tipo_responsable():
    data = {
        "id": int(request.form["id"]),
        "titulo": request.form["titulo"],
        "descripcion": request.form["descripcion"]
    }
    r = requests.post(API_URL, json=data)

    if r.status_code in (200, 201):
        return redirect(url_for("rutas_tipo_responsable.tipo_responsable"))
    else:
        return render_template("tipo_responsable.html", tipos=[], tipo=None, modo="crear", mensaje=f"No se pudo crear. Código: {r.status_code}")


# ------------------- BUSCAR -------------------
@rutas_tipo_responsable.route("/tipo_responsable/buscar", methods=["POST"])
def buscar_tipo_responsable():
    id_buscar = request.form["id_buscar"]
    try:
        r = requests.get(f"{API_URL}/{id_buscar}")
        if r.status_code == 200:
            tipo = r.json()

            # 👇 Si la API devuelve un string, lo convertimos en dict vacío para evitar el error
            if isinstance(tipo, str):
                tipo = None

            r_lista = requests.get(API_URL)
            tipos = r_lista.json() if r_lista.status_code == 200 else []
            return render_template("tipo_responsable.html", tipos=tipos, tipo=tipo, modo="editar", mensaje=None)
        else:
            return render_template("tipo_responsable.html", tipos=[], tipo=None, modo="crear", mensaje="No se encontró el tipo de responsable.")
    except Exception as e:
        return f"⚠️ Error al buscar tipo de responsable: {e}"


# ------------------- ACTUALIZAR -------------------
@rutas_tipo_responsable.route("/tipo_responsable/actualizar", methods=["POST"])
def actualizar_tipo_responsable():
    id_tipo = int(request.form["id"])
    data = {
        "titulo": request.form["titulo"],
        "descripcion": request.form["descripcion"]
    }
    r = requests.put(f"{API_URL}/{id_tipo}", json=data)

    if r.status_code in (200, 204):
        return redirect(url_for("rutas_tipo_responsable.tipo_responsable"))
    else:
        return f"No se pudo actualizar. Código: {r.status_code}"


# ------------------- ELIMINAR -------------------
@rutas_tipo_responsable.route("/tipo_responsable/eliminar/<int:id>", methods=["POST"])
def eliminar_tipo_responsable(id):
    try:
        # 👇 Cambia esto si tu API no usa /id/
        r = requests.delete(f"{API_URL}/id/{id}")  

        if r.status_code in (200, 204):
            return redirect(url_for("rutas_tipo_responsable.tipo_responsable"))
        else:
            return f"No se pudo eliminar el tipo de responsable. Código: {r.status_code} - {r.text}"
    except Exception as e:
        return f"⚠️ Error al eliminar tipo de responsable: {e}"
