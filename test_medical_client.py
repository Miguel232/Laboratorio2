# =============================
# archivo: test_medical_client.py
# Flujo simple: paciente + doctor -> cita -> prescripción (sin asserts)
# Requiere: eps_server.py en ejecución y eps_client.py en el mismo directorio
# =============================

import os
import eps_client as cli
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')  # Py3.7+
except Exception:
    pass


URL = "http://localhost:8080"

# Limpieza opcional (para que la primera cita quede con id=1)
for f in ("users.txt", "appointments.txt", "prescriptions.txt"):
    try:
        if os.path.exists(f):
            os.remove(f)
    except Exception as e:
        print(f"No se pudo borrar {f}:", e)

print("== HEALTH ==")
print(cli.health(URL))

print("\n== REGISTRO DE USUARIOS ==")
print(cli.registerUser(URL, "dr_lina", "abc", "doctor"))
print(cli.registerUser(URL, "juan", "222", "patient"))

print("\n== ABRIR SESIÓN ==")
print(cli.openSession(URL, "juan", "222"))
print(cli.openSession(URL, "dr_lina", "abc"))

print("\n== AGENDAR CITA ==")
# Viernes (horario válido): 19/09/2025 09:00
print(cli.scheduleAppointment(URL, patient="juan", password="222",
                              doctor="dr_lina", date_ddmmyyyy="19/09/2025", time_hhmm="09:00"))

print("\n== LISTAR CITAS DEL PACIENTE ==")
print(cli.listAppointments(URL, name="juan", password="222"))

print("\n== CREAR PRESCRIPCIÓN (usa appt_id=1 si es la primera cita) ==")
print(cli.createPrescription(URL, doctor="dr_lina", password="abc",
                             patient="juan", appt_id=1,
                             text="Ibuprofeno 400 mg cada 8h por 3 días"))

print("\n== LISTAR PRESCRIPCIONES COMO PACIENTE ==")
print(cli.listPrescriptions(URL, role="patient", name="juan", password="222"))

print("\n== LISTAR PRESCRIPCIONES COMO DOCTOR ==")
print(cli.listPrescriptions(URL, role="doctor", name="dr_lina", password="abc"))

print("\n== CERRAR SESIÓN ==")
print(cli.closeSession(URL, "juan", "222"))
print(cli.closeSession(URL, "dr_lina", "abc"))