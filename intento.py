from pathlib import Path
import csv
import json
import random

carpeta_ubicacion = Path(__file__).resolve().parent
carpeta_exportaciones = carpeta_ubicacion / "exportaciones"
carpeta_exportaciones.mkdir(exist_ok=True)

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
        return f"No hay jornadas; se creó {archivo.name} vacío."

    verbo = "exportó" if len(registros) == 1 else "exportaron"
    palabra = "registro" if len(registros) == 1 else "registros"
    return f"Se {verbo} {len(registros)} {palabra} a {archivo.name}."


def exportar_csv():
    
    registros = leer_jornadas()
    archivo = carpeta_exportaciones / "historias.csv"
    with archivo.open("w", encoding="utf-8-sig", newline="") as salida:
        escritor = csv.DictWriter(salida, fieldnames=["id", "edad", "co2", "spo2"])
        escritor.writeheader()
        escritor.writerows(registros)

    if not registros:
        return f"No hay jornadas; se creó {archivo.name} solo con el encabezado."

    verbo = "exportó" if len(registros) == 1 else "exportaron"
    palabra = "registro" if len(registros) == 1 else "registros"
    return f"Se {verbo} {len(registros)} {palabra} a {archivo.name}."

