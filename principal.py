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
    \n3  Mostrar historial de acciones
    \n4  Subir archivos a la base de datos del hospital 
    \n5  Para salir del sistema
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
        print(intento.historial())

    elif opcion == "4":
        while True:
            opdb = input("""Ingrese:
            \n1  Insertar historias.json en la base de datos
            \n2  Consultar todos los registros
            \n3  Buscar paciente por ID
            \n4  Volver al menu principal
            \n Opcion: """).strip()

            if opdb == "1":
                print(intento.insertar_json())

            elif opdb == "2":
                print(intento.consultar_registros())

            elif opdb == "3":
                id_buscar = input("Ingrese el ID del paciente: ").strip()
                print(intento.consultar_por_id(id_buscar))

            elif opdb == "4":
                break

            else:
                print("Opción no válida. Seleccione una opción del 1 al 4.")

    elif opcion == "5":
        print("Saliendo del sistema...")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción del 1 al 5.")