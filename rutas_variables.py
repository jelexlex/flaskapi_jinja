from flask import Blueprint, render_template, request, redirect, url_for
import requests

rutas_variables = Blueprint("rutas_variables", __name__)
API_URL = "http://localhost:5000/api/variables"  # Cambia esto si tu API tiene otra URL

# ------------------- LISTAR variables estratégicas -------------------
@rutas_variables.route("/variables", methods=["GET"])
def variables():
    try:
        respuesta = requests.get(API_URL)
        variables = respuesta.json().get("datos", [])
    except Exception as e:
        variables = []
        print(f"Error al obtener variables: {e}")

    return render_template(
        "variable_estrategica.html",
        variables=variables,
        variable=None,
        modo="crear"  # Por defecto el formulario está en modo creación
    )

# ------------------- CREAR variable estratégica -------------------
@rutas_variables.route("/variables/crear", methods=["POST"])
def crear_variable():
    datos = {
        "id": request.form.get("codigo"),
        "titulo": request.form.get("titulo"),
        "descripcion": request.form.get("descripcion")
    }

    try:
        respuesta = requests.post(API_URL, json=datos)
        if respuesta.status_code == 201:
            return redirect(url_for("rutas_variables.variables"))
        else:
            return f"Error al crear variable: {respuesta.text}"
    except Exception as e:
        return f"Error al crear variable estratégica: {e}"

# ------------------- BUSCAR variable estratégica -------------------
@rutas_variables.route("/variables/buscar", methods=["POST"])
def buscar_variable():
    codigo = request.form.get("codigo_buscar")

    if codigo:
        try:
            respuesta = requests.get(f"{API_URL}/codigo/{codigo}")
            if respuesta.status_code == 200:
                datos = respuesta.json().get("datos", [])
                if datos:
                    variable = datos[0]
                    variables = requests.get(API_URL).json().get("datos", [])
                    return render_template(
                        "variable_estrategica.html",
                        variables=variables,
                        variable=variable,
                        modo="actualizar"
                    )
        except Exception as e:
            return f"Error en la búsqueda: {e}"

    variables = requests.get(API_URL).json().get("datos", [])
    return render_template(
        "variable_estrategica.html",
        variables=variables,
        variable=None,
        mensaje="Variable estratégica no encontrada",
        modo="crear"
    )

# ------------------- ACTUALIZAR variable estratégica -------------------
@rutas_variables.route("/variables/actualizar", methods=["POST"])
def actualizar_variable():
    codigo = request.form.get("codigo")
    datos = {
        "titulo": request.form.get("titulo"),
        "descripcion": request.form.get("descripcion")
    }

    try:
        requests.put(f"{API_URL}/codigo/{codigo}", json=datos)
    except Exception as e:
        return f"Error al actualizar variable estratégica: {e}"

    return redirect(url_for("rutas_variables.variables"))

# ------------------- ELIMINAR variable estratégica -------------------
@rutas_variables.route("/variables/eliminar/<string:codigo>", methods=["POST"])
def eliminar_variable(codigo):
    try:
        requests.delete(f"{API_URL}/codigo/{codigo}")
    except Exception as e:
        return f"Error al eliminar variable estratégica: {e}"

    return redirect(url_for("rutas_variables.variables"))
