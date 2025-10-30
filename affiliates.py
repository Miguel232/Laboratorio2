# affiliates.py - Comentado en detalle

# ==============================================================================
# IMPORTACIONES
# Se importan las librerías estándar de Python necesarias.
# ==============================================================================
import os      # Para interactuar con el sistema operativo (verificar si un archivo existe).
import csv     # Para leer y escribir archivos en formato CSV (Comma-Separated Values).
import json    # Para trabajar con datos en formato JSON (para el archivo de usuarios).
from datetime import datetime, date  # Para manejar fechas y calcular edades.

# ==============================================================================
# CONSTANTES GLOBALES
# Definir los nombres de los archivos como constantes hace que el código sea
# más limpio y fácil de modificar si en el futuro queremos cambiar los nombres.
# ==============================================================================
AFF_FILE = "affiliates.csv"     # Archivo para guardar los datos de los afiliados.
SURV_FILE = "surveys.csv"       # Archivo para guardar las respuestas de las encuestas.
USERS_FILE = "users.txt"        # Archivo para guardar los usuarios (en formato JSONL).

# ==============================================================================
# FUNCIONES DE APOYO (HELPERS) PARA MANEJAR ARCHIVOS
# Estas funciones "privadas" (por convención, empiezan con _) nos ayudan a no
# repetir código. Se encargan de las tareas comunes de leer y escribir en los
# archivos de datos.
# ==============================================================================

def _ensure_aff_files():
    """
    Propósito: Verifica si los archivos 'affiliates.csv' y 'surveys.csv' existen.
    Si no existen, los crea y les escribe la primera línea (la cabecera o header)
    para definir las columnas. Esto previene errores si el programa se ejecuta por primera vez.
    """
    if not os.path.exists(AFF_FILE):
        with open(AFF_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "names", "surnames", "birth", "plan", "gender", "email"])
    if not os.path.exists(SURV_FILE):
        with open(SURV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "rating"])

def _read_affiliates():
    """
    Propósito: Lee todas las líneas del archivo 'affiliates.csv' y las convierte
    en una lista de diccionarios. Cada diccionario representa un afiliado.
    Retorna: Una lista de diccionarios. Ejemplo: [{'id': '1010', 'names': 'Ana', ...}, ...]
    """
    _ensure_aff_files()  # Se asegura de que el archivo exista antes de intentar leerlo.
    lista = []
    with open(AFF_FILE, newline="", encoding="utf-8") as f:
        # csv.DictReader es muy útil porque lee cada fila y automáticamente usa la
        # cabecera para crear un diccionario con las claves correctas.
        reader = csv.DictReader(f)
        for fila in reader:
            lista.append(fila)
    return lista

def _write_affiliates(lista):
    """
    Propósito: Sobrescribe COMPLETAMENTE el archivo 'affiliates.csv' con los datos
    que se le pasan en la 'lista'. Es importante entender que borra todo lo anterior.
    Por eso, el patrón de uso es: 1. Leer todo, 2. Modificar la lista en memoria, 3. Escribir todo de nuevo.
    Parámetros:
        - lista: Una lista de diccionarios de afiliados.
    """
    with open(AFF_FILE, "w", newline="", encoding="utf-8") as f:
        campos = ["id", "names", "surnames", "birth", "plan", "gender", "email"]
        # csv.DictWriter hace lo opuesto a DictReader: convierte una lista de diccionarios
        # a formato CSV, asegurando que cada valor vaya en la columna correcta.
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()      # Escribe la línea de cabecera.
        writer.writerows(lista)   # Escribe todas las filas de la lista de una vez.

# ... (Las funciones _read_surveys y _write_surveys siguen el mismo patrón que las de afiliados) ...

def _ensure_users():
    """
    Propósito: Si el archivo 'users.txt' no existe, lo crea vacío.
    """
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            pass  # 'pass' es una instrucción que no hace nada, aquí solo sirve para crear el archivo.

def _load_users():
    """
    Propósito: Lee el archivo 'users.txt'. Este archivo usa el formato JSONL (JSON por Línea),
    lo que significa que cada línea es un objeto JSON independiente.
    Retorna: Una lista de diccionarios, donde cada diccionario es un usuario.
    """
    _ensure_users()
    lista = []
    with open(USERS_FILE, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()  # Elimina espacios en blanco y saltos de línea invisibles.
            if linea:  # Si la línea no está vacía
                usuario = json.loads(linea)  # Convierte el texto JSON de la línea a un diccionario de Python.
                lista.append(usuario)
    return lista

def _rewrite_users(lista):
    """
    Propósito: Sobrescribe completamente el archivo 'users.txt' con la lista de usuarios.
    """
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for u in lista:
            linea = json.dumps(u)  # Convierte un diccionario de Python a un string en formato JSON.
            f.write(linea + "\n")  # Escribe el string JSON y un salto de línea para mantener el formato JSONL.

def _find_user(lista, nombre):
    """
    Propósito: Busca un usuario por su nombre dentro de una lista de usuarios.
    Retorna: El diccionario del usuario si lo encuentra, o 'None' si no lo encuentra.
    """
    for u in lista:
        if u["name"] == nombre:
            return u
    return None

# ==============================================================================
# FUNCIONES DE VALIDACIÓN DE DATOS
# Estas funciones pequeñas y reutilizables se encargan de verificar si un dato
# concreto cumple con las reglas del negocio.
# ==============================================================================

def convertir_fecha(cadena):
    """Intenta convertir un string 'dd/mm/yyyy' a un objeto de fecha. Si el formato es incorrecto, lanza un error 'ValueError'."""
    return datetime.strptime(cadena, "%d/%m/%Y").date()

def calcular_edad(fecha_nacimiento):
    """Calcula la edad actual de una persona a partir de su fecha de nacimiento."""
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad

def plan_valido(p):
    """Verifica que el plan sea uno de los valores permitidos."""
    return p in ("A", "B", "C")

def genero_valido(g):
    """Verifica que el género sea uno de los valores permitidos."""
    return g in ("M", "F", "X")

def correo_valido(e):
    """Realiza una validación muy básica de un correo electrónico."""
    return isinstance(e, str) and "@" in e and "." in e

# ==============================================================================
# API DE AFILIADOS (Funciones que el servidor puede llamar)
# ==============================================================================

def registerAffiliate(id_afiliado, nombres, apellidos, nacimiento, plan, genero, correo):
    """
    Lógica completa para registrar un nuevo afiliado.
    1. Valida que todos los datos sean correctos.
    2. Valida que el ID no esté ya en uso.
    3. Si todo está bien, lee los afiliados, añade el nuevo y reescribe el archivo.
    Retorna: Un string indicando el resultado ("ok", "invalid data", "id already exists", etc.).
    """
    # Validación de datos vacíos
    if any(not s.strip() for s in [id_afiliado, nombres, apellidos, nacimiento, plan, genero, correo]):
        return "invalid data"
    # Validación de formato de fecha
    try:
        convertir_fecha(nacimiento)
    except ValueError:
        return "invalid date format"
    # Validación de datos específicos (plan, género, correo)
    if not plan_valido(plan) or not genero_valido(genero) or not correo_valido(correo):
        return "invalid data"

    # Lee los afiliados existentes para verificar duplicados.
    afiliados = _read_affiliates()
    if any(af["id"] == id_afiliado for af in afiliados):
        return "id already exists"

    # Si todas las validaciones pasan, se crea el nuevo afiliado.
    nuevo = {"id": id_afiliado, "names": nombres, "surnames": apellidos, "birth": nacimiento, "plan": plan, "gender": genero, "email": correo}
    afiliados.append(nuevo)
    _write_affiliates(afiliados)
    return "ok"

def listAffiliates():
    """
    Lee todos los afiliados y los ordena alfabéticamente por apellido.
    Utiliza el algoritmo de ordenamiento de burbuja como lo pide el requerimiento.
    Retorna: La lista de afiliados ordenada.
    """
    afiliados = _read_affiliates()
    n = len(afiliados)
    # Algoritmo de Burbuja: Compara pares de elementos adyacentes y los intercambia si están en el orden incorrecto.
    # Repite este proceso hasta que toda la lista esté ordenada.
    for i in range(n):
        for j in range(0, n - i - 1):
            if afiliados[j]["surnames"].lower() > afiliados[j+1]["surnames"].lower():
                afiliados[j], afiliados[j+1] = afiliados[j+1], afiliados[j]
    return afiliados

def searchById(id_afiliado):
    """Busca un afiliado por su ID."""
    afiliados = _read_affiliates()
    for af in afiliados:
        if af["id"] == id_afiliado:
            return af
    return None

def stats():
    """
    Calcula varias estadísticas sobre la población de afiliados.
    - Total de afiliados por cada plan.
    - Edad promedio por género.
    - Edad mínima y máxima de todos los afiliados.
    Retorna: Un diccionario anidado con todos los resultados.
    """
    afiliados = _read_affiliates()
    if not afiliados: return {}

    totales_plan = {"A": 0, "B": 0, "C": 0}
    edades_por_genero = {"M": [], "F": [], "X": []}
    todas_las_edades = []

    for af in afiliados:
        # Contar por plan
        if af.get("plan") in totales_plan:
            totales_plan[af["plan"]] += 1
        
        # Recolectar edades
        try:
            edad = calcular_edad(convertir_fecha(af["birth"]))
            todas_las_edades.append(edad)
            if af.get("gender") in edades_por_genero:
                edades_por_genero[af["gender"]].append(edad)
        except (ValueError, KeyError):
            continue # Ignora afiliados con datos de fecha o género incorrectos.

    # Calcular promedios
    promedios_genero = {g: (sum(e) / len(e)) if e else 0.0 for g, e in edades_por_genero.items()}

    return {
        "totales": totales_plan,
        "promedios_por_genero": promedios_genero,
        "edad_minima": min(todas_las_edades) if todas_las_edades else 0,
        "edad_maxima": max(todas_las_edades) if todas_las_edades else 0
    }

# ... (Las demás funciones como recordSurvey, surveyStats, registerUser, etc., siguen la misma estructura de validación, lectura, modificación y escritura) ...
def findUser(nombre):
    """
    Esta función es especial porque es usada por el otro módulo de lógica ('clinical.py').
    Permite que la capa clínica pueda verificar la existencia y los datos de un usuario
    sin tener que acceder directamente al archivo de usuarios.
    """
    return _find_user(_load_users(), nombre)