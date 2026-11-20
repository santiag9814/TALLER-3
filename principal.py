import intento
import csv
import json
import os
from pathlib import Path

CARPETA_PROGRAMA = Path(__file__).resolve().parent
CARPETA_EXPORTACIONES = os.path.join(CARPETA_PROGRAMA, "exportaciones")

print("="*100)
print("Bienvenido al administrador de historias clinicas")
print("="*100)

while True:
    opcion = input("""Ingrese:
    \n1  Cargar pacientes (jornada)
    \n2  Exportar datos a JSON o CSV
    \n3  algo pendiente
    \n4  para salir del sistema
    \n Opcion: """).strip()

    if opcion == "1":
        print(intento.cargar_archivo_seleccionado())
    
    elif opcion == "2":

        while True:
            opi = input("""Ingrese:
            \n1  Exportar a JSON ( crear archivo para subir a la base de datos)
            \n2  Exportar a CSV( crear archivo con datos para trabajar internamete)
            \n3  para salir volver al menu principal
            \n Opcion: """).strip()

            if opi == "1":
                if not os.path.exists(CARPETA_EXPORTACIONES):
                    os.makedirs(CARPETA_EXPORTACIONES)
                print(intento.exportar_json())

            elif opi == "2":
                if not os.path.exists(CARPETA_EXPORTACIONES):
                    os.makedirs(CARPETA_EXPORTACIONES)
                print(intento.exportar_csv())

            elif opi == "3":
                break

    elif opcion == "3":
        print("en desarrollo ;)")
        break

    elif opcion == "4":
        print("Saliendo del sistema...")
        break
    else:
        print("Opción no válida. Por favor, seleccione una opción del 1 al 4.")