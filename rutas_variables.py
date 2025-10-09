# Importar módulos necesarios de Flask y la librería requests para conectarse a la API externa
from flask import Blueprint, render_template, request, redirect, url_for
import requests

# Crear el Blueprint de variables estratégicas
# "rutas_variables" es el nombre del módulo
# __name__ permite ubicar las plantillas dentro del proyecto
rutas_variables = Blueprint("rutas_variables", __name__)

# URL base de la API en C# que gestiona las variables estratégicas
API_URL = "http://localhost:5031/api/variable_estrategica"

# ------------------- LISTAR variables estratégicas -------------------
@rutas_variables.route("/variables")
def variables():
    """
    Ruta para listar todas las variables estratégicas disponibles en la API.
    Llama al endpoint /api/variable_estrategica y extrae la lista de variables desde la clave "datos".
    """
    try:
        respuesta = requests.get(API_URL)
        variables = respuesta.json().get("datos", [])
    except Exception as e:
        variables = []
        print("Error al conectar con la API:", e)

    # Retorna la plantilla variable_estrategica.html con la lista de variables
    return render_template(
        "variable_estrategica.html",
        variables=variables,
        variable=None,
        modo="crear"
    )

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
        "nombre": request.form.get("nombre"),
        "descripcion": request.form.get("descripcion"),
        "tipo": request.form.get("tipo"),
        "valor_objetivo": float(request.form.get("valor_objetivo", 0))
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
