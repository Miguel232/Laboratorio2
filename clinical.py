# clinical.py - Comentado en detalle

# ==============================================================================
# IMPORTACIONES
# ==============================================================================
import os
import json
from datetime import datetime
# ¡IMPORTANTE! Esta es la línea que conecta los dos módulos de lógica.
# Importamos la función 'findUser' desde 'affiliates.py' para poder
# autenticar y validar usuarios (pacientes y doctores) antes de realizar
# acciones clínicas.
from affiliates import findUser

# ==============================================================================
# CONSTANTES Y FUNCIONES DE APOYO
# ==============================================================================
APPTS_FILE = "appointments.txt"  # Archivo para guardar citas (formato JSONL)
PRESC_FILE = "prescriptions.txt" # Archivo para guardar prescripciones (formato JSONL)

# ... (Las funciones de apoyo _ensure, _load_jsonl, _rewrite_jsonl son similares
#      a las de affiliates.py, pero adaptadas para manejar archivos JSONL genéricos) ...

def _next_id(rows):
    """
    Calcula el siguiente ID numérico para un nuevo registro (cita o prescripción).
    Busca el ID más alto actual en la lista y le suma 1.
    Retorna: El nuevo ID como un string.
    """
    if not rows:
        return "1"
    # 'r.get("id", 0)' es una forma segura de obtener el ID. Si un registro no tuviera
    # la clave "id", devolvería 0 en lugar de dar un error.
    max_id = max(int(r.get("id", 0)) for r in rows)
    return str(max_id + 1)

def _valid_slot(date_str, time_str):
    """
    Valida si una fecha y hora propuestas para una cita cumplen las reglas del negocio:
    - Formato de fecha y hora correctos.
    - Día de la semana de Lunes a Viernes.
    - Hora entre las 08:00 y las 16:00.
    - Minutos deben ser 00 o 30 (intervalos de 30 minutos).
    Retorna: Un string indicando el resultado ("ok", "invalid data", "out of range").
    """
    try:
        fecha = datetime.strptime(date_str, "%d/%m/%Y").date()
        hora = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return "invalid data"

    # fecha.weekday() devuelve 0 para Lunes, 1 para Martes, ..., 6 para Domingo.
    if fecha.weekday() > 4:  # Mayor que 4 significa Sábado o Domingo.
        return "out of range"

    # Validaciones de hora y minutos.
    if not (datetime.strptime("08:00", "%H:%M").time() <= hora <= datetime.strptime("16:00", "%H:%M").time()):
        return "out of range"
    if hora.minute not in (0, 30):
        return "out of range"

    return "ok"

# ==============================================================================
# API CLÍNICA (Funciones que el servidor puede llamar)
# ==============================================================================

def scheduleAppointment(patient_name, patient_password, doctor_name, date_str, time_str):
    """
    Lógica completa para agendar una cita. Realiza una cadena de validaciones:
    1. Que los datos no estén vacíos.
    2. Que el doctor exista y tenga el rol 'doctor'.
    3. Que el paciente exista, su contraseña sea correcta y haya iniciado sesión.
    4. Que la fecha y hora sean un horario válido.
    5. Que no haya un choque de horario (el mismo doctor a la misma hora).
    Si todo es correcto, crea la nueva cita y la guarda en el archivo.
    """
    # 1. Validación de datos de entrada.
    if any(not s.strip() for s in [patient_name, patient_password, doctor_name, date_str, time_str]):
        return "invalid data"

    # 2. Validación del doctor usando la función importada.
    doctor = findUser(doctor_name)
    if not doctor or doctor.get("role") != "doctor":
        return "doctor not found"

    # 3. Validación y autenticación del paciente.
    patient = findUser(patient_name)
    if not patient or patient.get("password") != patient_password or not patient.get("session", False):
        return "user not logged in"

    # 4. Validación del horario.
    estado_slot = _valid_slot(date_str, time_str)
    if estado_slot != "ok":
        return estado_slot  # Retorna el error específico ("invalid data" o "out of range").

    # 5. Validación de colisión de citas.
    citas = _load_jsonl(APPTS_FILE)
    if any(c["doctor"] == doctor_name and c["date"] == date_str and c["time"] == time_str and c["status"] == "scheduled" for c in citas):
        return "slot taken"

    # 6. Si todo está bien, se crea y guarda la cita.
    nueva_cita = {
        "id": _next_id(citas), "patient": patient_name, "doctor": doctor_name,
        "date": date_str, "time": time_str, "status": "scheduled"
    }
    citas.append(nueva_cita)
    _rewrite_jsonl(APPTS_FILE, citas)
    return "ok"

def listAppointments(name, password):
    """
    Lista las citas de un usuario. Primero lo autentica, y luego filtra la lista
    de todas las citas para devolver solo aquellas donde el usuario es el paciente
    O el doctor.
    """
    # Autenticación del usuario que hace la petición.
    user = findUser(name)
    if not user or user.get("password") != password or not user.get("session", False):
        return "user not logged in"

    citas = _load_jsonl(APPTS_FILE)
    # Filtra la lista usando una "list comprehension" de Python.
    return [c for c in citas if c.get("patient") == name or c.get("doctor") == name]

def cancelAppointment(patient_name, patient_password, appointment_id):
    """
    Permite a un paciente cancelar una de sus propias citas.
    Valida al paciente, busca la cita por su ID, y si la encuentra y le pertenece,
    cambia su estado a 'cancelled'.
    """
    # Autenticación del paciente.
    patient = findUser(patient_name)
    if not patient or patient.get("password") != patient_password or not patient.get("session", False):
        return "user not logged in"

    citas = _load_jsonl(APPTS_FILE)
    cita_encontrada = False
    for c in citas:
        # Busca la cita específica que cumpla todas las condiciones.
        if (c.get("id") == str(appointment_id) and
            c.get("patient") == patient_name and
            c.get("status") == "scheduled"):
            c["status"] = "cancelled"  # Modifica el estado.
            cita_encontrada = True
            break  # Rompe el bucle una vez que la encuentra y modifica.

    if not cita_encontrada:
        return "not found"

    _rewrite_jsonl(APPTS_FILE, citas)  # Guarda la lista actualizada con el estado cambiado.
    return "ok"

# ... (Las funciones createPrescription y listPrescriptions siguen una lógica similar de
#      autenticación de roles y manipulación de datos) ...