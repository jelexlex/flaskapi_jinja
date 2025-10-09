from flask import Blueprint, render_template, request, redirect, url_for
import requests

rutas_variables = Blueprint("rutas_variables", __name__)

# ✅ Endpoint correcto
API_URL = "http://localhost:5031/api/variable_estrategica"


# ------------------- LISTAR variables estratégicas -------------------
@rutas_variables.route("/variables", methods=["GET"])
def variables():
    try:
        respuesta = requests.get(API_URL)
        data = respuesta.json()
        variables = data.get("datos", [])  # 👈 aquí extraemos la lista real
    except Exception as e:
        print(f"Error al obtener variables: {e}")
        variables = []

    return render_template(
        "variable_estrategica.html",
        variables=variables,
        variable=None,
        modo="crear"
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
        if respuesta.status_code in (200, 201):
            return redirect(url_for("rutas_variables.variables"))
        else:
            return f"Error al crear variable: {respuesta.text}"
    except Exception as e:
        return f"Error al crear variable estratégica: {e}"


@rutas_variables.route("/variables/buscar", methods=["POST"])
def buscar_variable():
    codigo = request.form.get("codigo_buscar")

    try:
        # 📡 Obtener todas las variables desde la API
        respuesta = requests.get(API_URL)
        if respuesta.status_code == 200:
            data = respuesta.json().get("datos", [])
            # 🔎 Buscar la variable que coincida con el ID ingresado
            variable = next((v for v in data if str(v["id"]) == str(codigo)), None)

            if variable:
                return render_template(
                    "variable_estrategica.html",
                    variables=data,
                    variable=variable,
                    modo="actualizar"
                )
    except Exception as e:
        return f"Error en la búsqueda: {e}"

    # ❌ Si no se encontró
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
