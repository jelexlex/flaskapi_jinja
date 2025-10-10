from flask import Blueprint, render_template, request, redirect, url_for
import requests

rutas_variables = Blueprint("rutas_variables", __name__)


API_BASE = "http://localhost:5031/api"
TABLA = "variable_estrategica"
NOMBRE_CLAVE = "id"

# ------------------- LISTAR variables -------------------
@rutas_variables.route("/variables", methods=["GET"])
def variables():
    try:
        r = requests.get(f"{API_BASE}/{TABLA}")
        data = r.json()
        
        variables = data.get("datos", []) if isinstance(data, dict) else data
    except Exception as e:
        print("Error al obtener variables:", e)
        variables = []
    return render_template("variable_estrategica.html", variables=variables, variable=None, modo="crear")


# ------------------- CREAR variable -------------------
@rutas_variables.route("/variables/crear", methods=["POST"])
def crear_variable():
    try:
        payload = {
            "titulo": request.form.get("titulo"),
            "descripcion": request.form.get("descripcion")
        }
        
        r = requests.post(f"{API_BASE}/{TABLA}", json=payload, timeout=10)
        if r.status_code not in (200, 201):
            return f"Error al crear: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Error al crear variable: {e}"

    return redirect(url_for("rutas_variables.variables"))


# ------------------- BUSCAR variable -------------------
@rutas_variables.route("/variables/buscar", methods=["POST"])
def buscar_variable():
    id_buscar = request.form.get("id_buscar") or request.form.get("id") or request.form.get("codigo_buscar")
    try:
        r = requests.get(f"{API_BASE}/{TABLA}", timeout=10)
        data = r.json()
        datos = data.get("datos", []) if isinstance(data, dict) else data
        
        variable = next((v for v in datos if str(v.get("id")) == str(id_buscar)), None)
        if variable:
            return render_template("variable_estrategica.html", variables=datos, variable=variable, modo="actualizar")
    except Exception as e:
        return f"Error en la búsqueda: {e}"

    # no encontrado
    return render_template("variable_estrategica.html",
                           variables=requests.get(f"{API_BASE}/{TABLA}").json().get("datos", []),
                           variable=None,
                           mensaje="Variable estratégica no encontrada",
                           modo="crear")


# ------------------- ACTUALIZAR variable (intenta rutas posibles) -------------------
@rutas_variables.route("/variables/actualizar", methods=["POST"])
def actualizar_variable():
    id_actual = request.form.get("id") or request.form.get("codigo")
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
                return redirect(url_for("rutas_variables.variables"))
        except Exception as e:
            print(f"PUT a {endpoint} falló: {e}")

    # Si llegamos aquí, fallaron todos
    if last_resp is not None:
        return f"No se pudo actualizar la variable. Última respuesta: {last_resp.status_code} - {last_resp.text}"
    return "No se pudo actualizar la variable. Sin respuesta del servidor."


# ------------------- ELIMINAR variable (intenta rutas posibles) -------------------
@rutas_variables.route("/variables/eliminar/<int:id>", methods=["POST"])
def eliminar_variable(id):
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
                return redirect(url_for("rutas_variables.variables"))
        except Exception as e:
            detalles.append((endpoint, "EXC", str(e)))
            print(f"DELETE a {endpoint} falló: {e}")

    
    detalle_str = "\n".join([f"{ep} -> {st} - {tx}" for ep, st, tx in detalles])
    return f"No se pudo eliminar la variable. Intentos:\n{detalle_str}"
