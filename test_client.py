# =============================
# archivo: test_client.py
# Prueba simple: usuarios + afiliados + encuestas
# Requiere: eps_server.py en ejecución
# =============================

import eps_client as cli

URL = "http://localhost:8080"

print("== HEALTH ==")
print(cli.health(URL))

print("\n== USUARIOS ==")
print(cli.registerUser(URL, "admin1", "adm", "administrativo"))
print(cli.registerUser(URL, "dr_carlos", "abc", "doctor"))
print(cli.registerUser(URL, "maria", "111", "patient"))

print("\n== SESIONES ==")
print(cli.openSession(URL, "maria", "111"))
print(cli.openSession(URL, "dr_carlos", "abc"))
print(cli.closeSession(URL, "dr_carlos", "abc"))  # ejemplo de cierre inmediato

print("\n== AFILIADOS ==")
print(cli.registerAffiliate(
    URL, _id="1010", names="Ana", surnames="Garcia", birth="12/03/1999",
    plan="A", gender="F", email="ana@example.com"
))
print(cli.listAffiliates(URL))
print(cli.searchAffiliate(URL, "1010"))

print("\n== ENCUESTAS ==")
print(cli.recordSurvey(URL, _id="1010", rating=5))
print(cli.surveyStats(URL, segment_by="plan"))
print(cli.exportCsv(URL))