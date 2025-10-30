# eps_server.py - Comentado en detalle

# ==============================================================================
# IMPORTACIONES
# Se importan las librerías necesarias para que el servidor funcione.
# ==============================================================================

# 'os' permite interactuar con el sistema operativo, en este caso, para asegurar que se use la librería local 'requests'.
import os
# 'sys' permite manipular el intérprete de Python, aquí se usa para añadir la carpeta actual a las rutas de búsqueda.
import sys
# Desde 'flask', importamos las herramientas principales:
# - Flask: Es la clase principal para crear nuestra aplicación web.
# - request: Es un objeto global que contiene toda la información de la petición que acaba de llegar (datos, headers, etc.).
# - jsonify: Es una función que convierte un diccionario de Python en un formato de texto estándar llamado JSON, que es el lenguaje universal para las APIs web.
from flask import Flask, request, jsonify

# Esta línea añade la carpeta actual al 'sys.path'. Esto le dice a Python que,
# además de buscar librerías en sus carpetas de instalación, también busque
# en la carpeta donde está este script. Es crucial para que pueda encontrar y
# usar los archivos 'affiliates.py' y 'clinical.py'.
sys.path.insert(0, os.path.dirname(__file__))

# ==============================================================================
# IMPORTACIÓN DE LA LÓGICA DE NEGOCIO
# Aquí importamos TODAS las funciones que hemos programado en los otros archivos.
# El servidor actuará como un intermediario, llamando a estas funciones
# cuando reciba una petición en la ruta correcta.
# ==============================================================================
from affiliates import (
    registerAffiliate, listAffiliates, searchById, stats, exportCsv,
    recordSurvey, surveyStats,
    registerUser, openCloseSession
)
from clinical import (
    scheduleAppointment, listAppointments, cancelAppointment,
    createPrescription, listPrescriptions
)

# ==============================================================================
# INICIALIZACIÓN DE LA APLICACIÓN FLASK
# Creamos una instancia de la aplicación Flask. La variable 'app' representará
# nuestro servidor web.
# ==============================================================================
app = Flask(__name__)

# ==============================================================================
# RUTAS O "ENDPOINTS" DEL SERVIDOR
# Cada bloque que empieza con '@app.route(...)' define una URL que nuestro
# servidor va a escuchar. Cuando alguien haga una petición a esa URL,
# la función que está justo debajo se ejecutará.
# ==============================================================================

# === RUTA DE PRUEBA DE SALUD ===
# Esta es una ruta muy simple para verificar si el servidor está encendido y responde.
@app.route("/health")
def health():
    """
    Endpoint: /health
    Método: GET
    Propósito: Devuelve un mensaje simple para confirmar que el servidor está activo.
    No requiere datos de entrada.
    Responde: {"status": "ok"}
    """
    # jsonify convierte el diccionario de Python en una respuesta JSON válida.
    return jsonify({"status": "ok"})


# === RUTAS DE USUARIOS Y SESIONES ===

@app.route("/user/register", methods=['POST'])
def user_register_route():
    """
    Endpoint: /user/register
    Método: POST
    Propósito: Registrar un nuevo usuario (paciente, doctor, administrativo).
    Espera recibir un JSON con: {"name", "password", "role"}.
    Llama a la función 'registerUser' de affiliates.py.
    """
    # 'request.get_json()' extrae los datos JSON que el cliente envió en el cuerpo de la petición POST.
    data = request.get_json()
    # Llama a la función de lógica de negocio con los datos recibidos.
    result = registerUser(data["name"], data["password"], data["role"])
    # Devuelve una respuesta JSON. Si el registro fue exitoso, 'result' será "ok".
    return jsonify({"message": result})

@app.route("/user/session", methods=['POST'])
def user_session_route():
    """
    Endpoint: /user/session
    Método: POST
    Propósito: Abrir o cerrar la sesión de un usuario.
    Espera recibir un JSON con: {"name", "password", "session" (True o False)}.
    Llama a la función 'openCloseSession' de affiliates.py.
    """
    data = request.get_json()
    # Llama a la función de lógica de negocio para actualizar el estado de la sesión.
    result = openCloseSession(data["name"], data["password"], data["session"])
    # Devuelve una respuesta JSON indicando el resultado de la operación.
    return jsonify({"message": result})


# === RUTAS DE AFILIADOS ===

@app.route("/affiliate/register", methods=['POST'])
def affiliate_register_route():
    """
    Endpoint: /affiliate/register
    Método: POST
    Propósito: Registrar un nuevo afiliado en el sistema.
    Espera un JSON con todos los datos del afiliado.
    Llama a la función 'registerAffiliate' de affiliates.py.
    """
    data = request.get_json()
    # Llama a la función de lógica con todos los campos necesarios.
    result = registerAffiliate(
        data["id"], data["names"], data["surnames"], data["birth"],
        data["plan"], data["gender"], data["email"]
    )
    return jsonify({"message": result})

@app.route("/affiliates")
def affiliates_list_route():
    """
    Endpoint: /affiliates
    Método: GET
    Propósito: Obtener la lista de todos los afiliados.
    No requiere datos de entrada.
    Llama a la función 'listAffiliates' de affiliates.py.
    """
    # Llama a la función que lee y ordena todos los afiliados.
    result = listAffiliates()
    # Devuelve la lista completa de afiliados en formato JSON.
    return jsonify({"affiliates": result})

@app.route("/affiliate")
def affiliate_search_route():
    """
    Endpoint: /affiliate
    Método: GET
    Propósito: Buscar un afiliado específico por su ID.
    El ID se pasa como un parámetro en la URL (ej: /affiliate?id=1010).
    Llama a la función 'searchById' de affiliates.py.
    """
    # 'request.args.get()' extrae los parámetros de la URL.
    affiliate_id = request.args.get("id")
    # Llama a la función de búsqueda.
    result = searchById(affiliate_id)
    # Devuelve los datos del afiliado encontrado (o 'None' si no existe).
    return jsonify(result)

@app.route("/affiliates/stats")
def affiliates_stats_route():
    """
    Endpoint: /affiliates/stats
    Método: GET
    Propósito: Obtener estadísticas sobre los afiliados (totales por plan, edades, etc.).
    Llama a la función 'stats' de affiliates.py.
    """
    result = stats()
    return jsonify(result)

@app.route("/affiliates/export")
def affiliates_export_route():
    """
    Endpoint: /affiliates/export
    Método: GET
    Propósito: Asegura que los archivos CSV de datos se creen en el disco del servidor.
    Llama a la función 'exportCsv' de affiliates.py.
    """
    result = exportCsv()
    return jsonify({"message": result})


# === RUTAS DE ENCUESTAS ===

@app.route("/survey/record", methods=['POST'])
def survey_record_route():
    """
    Endpoint: /survey/record
    Método: POST
    Propósito: Registrar la calificación de una encuesta para un afiliado.
    Espera un JSON con: {"id", "rating"}.
    Llama a la función 'recordSurvey' de affiliates.py.
    """
    data = request.get_json()
    result = recordSurvey(data["id"], data["rating"])
    return jsonify({"message": result})

@app.route("/surveys/stats")
def surveys_stats_route():
    """
    Endpoint: /surveys/stats
    Método: GET
    Propósito: Obtener estadísticas de las encuestas (promedio global o segmentado).
    Opcionalmente, puede recibir un parámetro en la URL (ej: /surveys/stats?by=plan).
    Llama a la función 'surveyStats' de affiliates.py.
    """
    segment = request.args.get("by") # 'by' puede ser 'plan' o 'gender'.
    result = surveyStats(segment)
    return jsonify(result)


# === RUTAS CLÍNICAS (CITAS Y PRESCRIPCIONES) ===

@app.route("/appointment/schedule", methods=['POST'])
def appointment_schedule_route():
    """
    Endpoint: /appointment/schedule
    Método: POST
    Propósito: Agendar una nueva cita médica.
    Espera un JSON con los datos del paciente, doctor, fecha y hora.
    Llama a la función 'scheduleAppointment' de clinical.py.
    """
    data = request.get_json()
    result = scheduleAppointment(
        data["patient_name"], data["patient_password"], data["doctor_name"],
        data["date"], data["time"]
    )
    return jsonify({"message": result})

@app.route("/appointments")
def appointments_list_route():
    """
    Endpoint: /appointments
    Método: GET
    Propósito: Listar las citas de un usuario (paciente o doctor).
    Espera los datos del usuario como parámetros en la URL (ej: /appointments?name=juan&password=clave123).
    Llama a la función 'listAppointments' de clinical.py.
    """
    name = request.args.get("name")
    password = request.args.get("password")
    result = listAppointments(name, password)
    return jsonify({"appointments": result})

@app.route("/appointment/cancel", methods=['POST'])
def appointment_cancel_route():
    """
    Endpoint: /appointment/cancel
    Método: POST
    Propósito: Cancelar una cita médica agendada.
    Espera un JSON con los datos del paciente y el ID de la cita a cancelar.
    Llama a la función 'cancelAppointment' de clinical.py.
    """
    data = request.get_json()
    result = cancelAppointment(data["patient_name"], data["patient_password"], data["appointment_id"])
    return jsonify({"message": result})

@app.route("/prescription/create", methods=['POST'])
def prescription_create_route():
    """
    Endpoint: /prescription/create
    Método: POST
    Propósito: Crear una nueva prescripción médica asociada a una cita.
    Espera un JSON con los datos del doctor, paciente, ID de la cita y el texto de la prescripción.
    Llama a la función 'createPrescription' de clinical.py.
    """
    data = request.get_json()
    result = createPrescription(
        data["doctor_name"], data["doctor_password"], data["patient_name"],
        data["appt_id"], data["text"]
    )
    return jsonify({"message": result})

@app.route("/prescriptions")
def prescriptions_list_route():
    """
    Endpoint: /prescriptions
    Método: GET
    Propósito: Listar las prescripciones de un usuario según su rol.
    Espera los datos del usuario y su rol como parámetros en la URL.
    Llama a la función 'listPrescriptions' de clinical.py.
    """
    role = request.args.get("role")
    name = request.args.get("name")
    password = request.args.get("password")
    result = listPrescriptions(role, name, password)
    return jsonify({"prescriptions": result})

# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# Este bloque de código solo se ejecuta si corremos este archivo directamente
# con el comando 'python eps_server.py'. No se ejecutaría si otro archivo
# lo importa.
# ==============================================================================
if __name__ == "__main__":
    # 'app.run()' inicia el servidor Flask.
    # host='0.0.0.0' hace que el servidor sea visible en la red local, no solo en la propia máquina.
    # port=8080 especifica el puerto en el que va a escuchar.
    # debug=False se usa en producción para no mostrar información sensible en caso de error.
    app.run(host='0.0.0.0', port=8080, debug=False)