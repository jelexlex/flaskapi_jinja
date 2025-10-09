from flask import Blueprint, render_template, request, redirect, url_for
import requests

rutas_variables = Blueprint("rutas_variables", __name__)

# endpoint real que me dijiste
API_URL = "http://localhost:5031/api/variable_estrategica"


# ------------------- LISTAR -------------------
@rutas_variables.route("/variables", methods=["GET"])
def variables():
    try:
        r = requests.get(API_URL)
        data = r.json()
        variables = data.get("datos", [])
    except Exception as e:
        print(f"Error al obtener variables: {e}")
        variables = []

    return render_template("variable_estrategica.html", variables=variables, variable=None, modo="crear")


# ------------------- CREAR -------------------
@rutas_variables.route("/variables/crear", methods=["POST"])
def crear_variable():
    datos = {
        "id": request.form.get("codigo"),
        "titulo": request.form.get("titulo"),
        "descripcion": request.form.get("descripcion")
    }

    try:
        r = requests.post(API_URL, json=datos)
        if r.status_code in (200, 201):
            return redirect(url_for("rutas_variables.variables"))
        else:
            return f"Error al crear variable: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error al crear variable estratégica: {e}"


# ------------------- BUSCAR (cliente) -------------------
@rutas_variables.route("/variables/buscar", methods=["POST"])
def buscar_variable():
    codigo = request.form.get("codigo_buscar")
    try:
        r = requests.get(API_URL)
        data = r.json().get("datos", [])
        # buscar localmente porque la API no tiene /codigo/<id>
        variable = next((v for v in data if str(v.get("id")) == str(codigo)), None)
        if variable:
            return render_template("variable_estrategica.html", variables=data, variable=variable, modo="actualizar")
    except Exception as e:
        return f"Error en la búsqueda: {e}"

    variables = requests.get(API_URL).json().get("datos", [])
    return render_template("variable_estrategica.html", variables=variables, variable=None, mensaje="Variable estratégica no encontrada", modo="crear")


# ------------------- ACTUALIZAR (con fallback de rutas) -------------------
@rutas_variables.route("/variables/actualizar", methods=["POST"])
def actualizar_variable():
    codigo = request.form.get("codigo")
    datos = {
        "titulo": request.form.get("titulo"),
        "descripcion": request.form.get("descripcion")
    }

    # Intentos de PUT en posibles rutas que la API podría esperar
    posibles_endpoints = [
        f"{API_URL}/codigo/{codigo}",  # si API usa "/codigo/<id>"
        f"{API_URL}/{codigo}",         # si API usa "/<id>"
    ]

    last_resp = None
    for endpoint in posibles_endpoints:
        try:
            r = requests.put(endpoint, json=datos)
            last_resp = r
            if r.status_code in (200, 204):
                return redirect(url_for("rutas_variables.variables"))
        except Exception as e:
            print(f"Intento PUT a {endpoint} falló: {e}")

    # Si llegamos aquí, todos los PUT fallaron
    msg = "No se pudo actualizar la variable. "
    if last_resp is not None:
        msg += f"Última respuesta: {last_resp.status_code} - {last_resp.text}"
    else:
        msg += "No hubo respuesta del servidor."
    return msg


# ------------------- ELIMINAR (con fallback de rutas) -------------------
@rutas_variables.route("/variables/eliminar/<string:codigo>", methods=["POST"])
def eliminar_variables(codigo):
    """
    Ruta para eliminar una variable de la API según su código.
    Envía una petición DELETE al endpoint correspondiente.
    """
    try:
        requests.delete(f"{API_URL}/codigo/{codigo}")
    except Exception as e:
        return f"Error al eliminar variable: {e}"

    return redirect(url_for("rutas_variables.variables"))


