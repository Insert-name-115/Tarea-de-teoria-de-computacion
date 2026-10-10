# -------------------------------------------------------------------
# Ejecuta los puntos 1, 2 y 3 de la tarea:  python main.py
# Los diagramas quedan en la carpeta automatas/ (.dot, y .png si está
# instalado Graphviz). Los .dot se pueden ver en https://dreampuf.github.io/GraphvizOnline
# -------------------------------------------------------------------

import shutil

from punto1_especificacion import mostrar_especificacion
from punto2_expresiones import reconocer_er
from punto3_automatas import AFDS, afd_atomo, afd_integrado, dibujar_afd, tabla_pasos

# Punto 1: especificación de tokens
print("=== PUNTO 1: Especificación ===")
mostrar_especificacion()

# Punto 2: casos donde varias ER calzan y cuál se elige
print("\n=== PUNTO 2: Máxima coincidencia y prioridad (ER) ===")
casos = ["\\==", "\\=", "=..", ":-", "_", "_X", "is", "isa", "3.14", "3.", "/* c */", "//"]
for texto in casos:
    print(f"{texto!r:<12} -> {reconocer_er(texto)}")

# Punto 3: los mismos casos con el AFD integrado (deben dar lo mismo)
print("\n=== PUNTO 3: AFD integrado ===")
for texto in casos:
    resultado = afd_integrado.reconocer(texto)
    print(f"{texto!r:<12} -> {resultado}   coincide con ER: {resultado == reconocer_er(texto)}")

# Ejemplo de simulación
cadena = "persona_1"
final, log = afd_atomo.simular(cadena)
print(f"\nSimulación del AFD ATOMO con {cadena!r}")
tabla_pasos(log)
print("Estado final:", final, "| ¿Acepta?", final in afd_atomo.aceptacion)

# Dibujar los autómatas
for afd in AFDS + [afd_integrado]:
    dot = dibujar_afd(afd)
    dot.save(f"automatas/{afd.nombre.lower()}.dot")
    if shutil.which("dot"):
        dot.render(f"automatas/{afd.nombre.lower()}", cleanup=True)
dibujar_afd(afd_atomo, log).save("automatas/simulacion_atomo.dot")
print("\nDiagramas guardados en la carpeta automatas/")
