# =============================
# archivo: eps_client.py  (estilo simple, urlencoded)
# Requiere: pip install requests
# =============================


import requests

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

# ---------- Salud ----------
def health(url):
    response = requests.get(url + "/health")
    return response.content.decode("utf-8", errors="replace")

# ---------- Usuarios (roles/sesión) ----------
def registerUser(url, name, password, role):
    body = f"name={name}&password={password}&role={role}"
    response = requests.post(url + "/user/register", data=body, headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")

def openSession(url, name, password):
    body = f"name={name}&password={password}&flag=true"
    response = requests.post(url + "/user/session", data=body, headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")

def closeSession(url, name, password):
    body = f"name={name}&password={password}&flag=false"
    response = requests.post(url + "/user/session", data=body, headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")

# ---------- Citas médicas ----------
def scheduleAppointment(url, patient, password, doctor, date_ddmmyyyy, time_hhmm):
    body = f"patient={patient}&password={password}&doctor={doctor}&date={date_ddmmyyyy}&time={time_hhmm}"
    response = requests.post(url + "/appointment/schedule", data=body, headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")

def listAppointments(url, name, password):
    # GET con query en la URL (mismo estilo simple)
    response = requests.get(url + f"/appointment/list?name={name}&password={password}")
    return response.content.decode("utf-8", errors="replace")

def cancelAppointment(url, patient, password, appt_id):
    body = f"patient={patient}&password={password}&id={appt_id}"
    response = requests.post(url + "/appointment/cancel", data=body, headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")

# ---------- Prescripciones ----------
def createPrescription(url, doctor, password, patient, appt_id, text):
    body = f"doctor={doctor}&password={password}&patient={patient}&appt_id={appt_id}&text={text}"
    response = requests.post(url + "/prescription/create", data=body, headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")

def listPrescriptions(url, role, name, password):
    response = requests.get(url + f"/prescription/list?role={role}&name={name}&password={password}")
    return response.content.decode("utf-8", errors="replace")

# ---------- Afiliados / Encuestas (como el lab original) ----------
def registerAffiliate(url, _id, names, surnames, birth, plan, gender, email):
    body = f"id={_id}&names={names}&surnames={surnames}&birth={birth}&plan={plan}&gender={gender}&email={email}"
    response = requests.post(url + "/register", data=body, headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")

def listAffiliates(url):
    response = requests.get(url + "/list")
    return response.content.decode("utf-8", errors="replace")

def searchAffiliate(url, _id):
    response = requests.get(url + f"/search?id={_id}")
    return response.content.decode("utf-8", errors="replace")

def stats(url):
    response = requests.get(url + "/stats")
    return response.content.decode("utf-8", errors="replace")

def recordSurvey(url, _id, rating):
    body = f"id={_id}&rating={rating}"
    response = requests.post(url + "/survey", data=body, headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")

def surveyStats(url, segment_by=None):
    if segment_by:
        response = requests.get(url + f"/survey_stats?segment_by={segment_by}")
    else:
        response = requests.get(url + "/survey_stats")
    return response.content.decode("utf-8", errors="replace")

def exportCsv(url):
    response = requests.post(url + "/export", data="", headers=HEADERS)
    return response.content.decode("utf-8", errors="replace")
