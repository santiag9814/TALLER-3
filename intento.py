from pathlib import Path
from datetime import datetime
import csv
import json
import random

import config

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None

carpeta_ubicacion = Path(__file__).resolve().parent
carpeta_exportaciones = carpeta_ubicacion / "exportaciones"
carpeta_exportaciones.mkdir(exist_ok=True)
archivo_historial = carpeta_ubicacion / "log.txt"


def _registrar(accion):
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with archivo_historial.open("a", encoding="utf-8") as salida:
        salida.write(f"[{hora}] {accion}\n")


def id():
    return f"ID_{random.randint(1, 9999)}"

def fr():
    return f"{random.randint(1, 105)} Años"

def fc():
    return f"{random.randint(20, 250)} ppm"

def spo2():
    return f"{random.randint(30, 100)}%"

def historiascli():
    num = 1
    archivo = carpeta_ubicacion / f"Jornada {num}.txt"

    while archivo.exists():
        num += 1
        archivo = carpeta_ubicacion / f"Jornada {num}.txt"

    archivo.touch()
    _registrar(f"Creó {archivo.name}")
    return archivo


def cargar_archivo_seleccionado():
    while True:
        entrada = input("ingrese la cantidad de pacientes que desea anotar en la jornada: ").strip()
        try:
            N = int(entrada)
            if N < 1:
                print("La cantidad debe ser al menos 1.")
                continue
            break
        except ValueError:
            print("Ingrese un número entero válido.")

    archivo_jornada = historiascli()
    with archivo_jornada.open("a", encoding="utf-8") as archivito:
        for _ in range(N):
            archivito.write(f"{id()},{fr()},{fc()},{spo2()}\n")

    _registrar(f"Registró {N} pacientes en {archivo_jornada.name}")
    return f"Se han registrado {N} pacientes en la jornada."


def leer_jornadas():
    
    registros = []

    def numero_jornada(archivo):
        try:
            return int(archivo.stem.rsplit(" ", 1)[-1])
        except ValueError:
            return 0

    for archivo in sorted(carpeta_ubicacion.glob("Jornada *.txt"), key=numero_jornada):
        with archivo.open("r", encoding="utf-8") as jornada:
            for linea in jornada:
                campos = [campo.strip() for campo in linea.split(",")]
                if len(campos) != 4:
                    continue
                registros.append({
                    "id": campos[0],
                    "edad": campos[1],
                    "co2": campos[2],
                    "spo2": campos[3],
                })

    return registros


def exportar_json():
    
    registros = leer_jornadas()
    archivo = carpeta_exportaciones / "historias.json"
    with archivo.open("w", encoding="utf-8") as salida:
        json.dump(registros, salida, ensure_ascii=False, indent=4)

    if not registros:
        _registrar(f"Generó {archivo.name} vacío (sin jornadas)")
        return f"No hay jornadas; se creó {archivo.name} vacío."

    verbo = "exportó" if len(registros) == 1 else "exportaron"
    palabra = "registro" if len(registros) == 1 else "registros"
    _registrar(f"Exportó {len(registros)} {palabra} a {archivo.name}")
    return f"Se {verbo} {len(registros)} {palabra} a {archivo.name}."


def exportar_csv():
    
    registros = leer_jornadas()
    archivo = carpeta_exportaciones / "historias.csv"
    with archivo.open("w", encoding="utf-8-sig", newline="") as salida:
        escritor = csv.DictWriter(salida, fieldnames=["id", "edad", "co2", "spo2"])
        escritor.writeheader()
        escritor.writerows(registros)

    if not registros:
        _registrar(f"Generó {archivo.name} solo con el encabezado (sin jornadas)")
        return f"No hay jornadas; se creó {archivo.name} solo con el encabezado."

    verbo = "exportó" if len(registros) == 1 else "exportaron"
    palabra = "registro" if len(registros) == 1 else "registros"
    _registrar(f"Exportó {len(registros)} {palabra} a {archivo.name}")
    return f"Se {verbo} {len(registros)} {palabra} a {archivo.name}."

def historial():
    """Muestra las acciones con su hora y un resumen de ID y edad."""
    lineas = ["=== Historial del sistema ==="]

    eventos = []
    if archivo_historial.exists():
        eventos = [
            linea.strip()
            for linea in archivo_historial.read_text(encoding="utf-8").splitlines()
            if linea.strip()
        ]

    if eventos:
        lineas.extend(eventos)
    else:
        lineas.append("  (sin acciones registradas)")

    lineas.append("")
    lineas.append("=== Resumen de pacientes ===")
    registros = leer_jornadas()
    if registros:
        lineas.append(f"{'ID':<14}{'Edad'}")
        for registro in registros:
            lineas.append(f"{registro['id']:<14}{registro['edad']}")
        lineas.append(f"\nTotal: {len(registros)} pacientes")
    else:
        lineas.append("  (sin pacientes registrados)")

    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# MongoDB Atlas
# ---------------------------------------------------------------------------

def _uri_configurada():
   
    uri = (getattr(config, "MONGO_URI", "") or "").strip()
    marcadores = ("TU_USUARIO", "TU_CONTRASENA", "<password>", "<db_username>",
                  "<db_password>", "xxxxx")
    return bool(uri) and not any(marcador in uri for marcador in marcadores)


def conectar():
    
    if MongoClient is None:
        raise RuntimeError("Falta pymongo. Instálalo con: pip install pymongo dnspython")
    if not _uri_configurada():
        raise RuntimeError("Configura tu MONGO_URI real en config.py antes de conectar.")

    cliente = MongoClient(getattr(config, "MONGO_URI"), serverSelectionTimeoutMS=10000)
    cliente.admin.command("ping")  # Verifica que la conexión funcione

    base = cliente[getattr(config, "DB_NAME", "hospital")]
    nombre_coleccion = getattr(config, "COLECCION", "signos vitales")
    if nombre_coleccion not in base.list_collection_names():
        base.create_collection(nombre_coleccion)

    return cliente, base, base[nombre_coleccion]


def crear_base_de_datos():
    
    try:
        cliente, base, coleccion = conectar()
    except Exception as error:
        return f"No se pudo conectar a MongoDB Atlas: {error}"

    try:
        return (f"Conexión lista. Base de datos '{base.name}' "
                f"y colección '{coleccion.name}' disponibles.")
    finally:
        cliente.close()


def insertar_json():
    archivo = carpeta_exportaciones / "historias.json"
    if not archivo.exists():
        return f"No existe {archivo.name}. Primero exporta los datos a JSON."

    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        return f"No se pudo leer {archivo.name}: {error}"

    if isinstance(datos, dict):
        datos = [datos]
    if not isinstance(datos, list) or not datos:
        return f"{archivo.name} no contiene registros para insertar."

    documentos = []
    for registro in datos:
        if not isinstance(registro, dict):
            continue
        documentos.append({
            "id": str(registro.get("id", "")),
            "edad": str(registro.get("edad", "")),
            "co2": str(registro.get("co2", "")),
            "spo2": str(registro.get("spo2", "")),
            "fecha_carga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    if not documentos:
        return f"{archivo.name} no tiene registros válidos."

    try:
        cliente, base, coleccion = conectar()
    except Exception as error:
        return f"No se pudo conectar a MongoDB Atlas: {error}"

    try:
        resultado = coleccion.insert_many(documentos)
        _registrar(f"Insertó {len(resultado.inserted_ids)} registros desde {archivo.name} a Atlas")
        return (f"Se insertaron {len(resultado.inserted_ids)} registros en "
                f"'{base.name}.{coleccion.name}'.")
    except Exception as error:
        return f"No se pudo insertar en Atlas: {error}"
    finally:
        cliente.close()


def consultar_registros(filtro=None, limite=20):
    
    filtro = filtro or {}
    try:
        cliente, base, coleccion = conectar()
    except Exception as error:
        return f"No se pudo conectar a MongoDB Atlas: {error}"

    try:
        documentos = list(coleccion.find(filtro, {"_id": 0}).limit(limite))
    except Exception as error:
        return f"No se pudo consultar Atlas: {error}"
    finally:
        cliente.close()

    if not documentos:
        return "No hay registros en la colección 'signos vitales'."

    lineas = [f"{'ID':<14}{'Edad':<12}{'CO2':<12}{'SpO2'}"]
    for documento in documentos:
        lineas.append(
            f"{str(documento.get('id', '')):<14}"
            f"{str(documento.get('edad', '')):<12}"
            f"{str(documento.get('co2', '')):<12}"
            f"{documento.get('spo2', '')}"
        )
    lineas.append(f"\nMostrando {len(documentos)} registro(s) de '{base.name}.{coleccion.name}'.")

    _registrar(f"Consultó registros en Atlas ({len(documentos)} resultado(s))")
    return "\n".join(lineas)


def consultar_por_id(id_paciente):
    
    return consultar_registros({"id": str(id_paciente).strip()})

