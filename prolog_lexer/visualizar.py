# -------------------------------------------------------------------
# Funciones para visualizar los AFD y mostrar pasos
# -------------------------------------------------------------------
# Comentarios:
# - 'dibujar_afd' dibuja el grafo del AFD con Graphviz. Si se le pasa el
#   camino recorrido (log de 'simular'), lo resalta en azul.
# - 'tabla_pasos' muestra en consola las transiciones tomadas.
# - 'tabla_transiciones' lista estados y transiciones (útil para el informe).
# - 'guardar_afd' guarda el .dot y, si está instalado Graphviz ('dot'),
#   también el .png. Los .dot se pueden ver en
#   https://dreampuf.github.io/GraphvizOnline
# -------------------------------------------------------------------

import shutil
from pathlib import Path
from typing import List, Optional

import graphviz

from .automatas import AFD, ALFABETO


def etiqueta(simbolos: List[str]) -> str:
    """Si son casi todos los símbolos, escribe 'todo menos ...' para acortar."""
    faltan = ALFABETO - set(simbolos)
    if len(simbolos) > 8:
        return "todo menos " + ", ".join(sorted(faltan)) if faltan else "cualquiera"
    return ", ".join(sorted(simbolos))


def dibujar_afd(afd: AFD, log: Optional[list] = None) -> graphviz.Digraph:
    dot = graphviz.Digraph(name=afd.nombre, format="png")
    dot.attr(rankdir="LR")
    dot.node("", shape="point")  # nodo invisible para la flecha inicial

    # Pares (origen, destino) recorridos en la simulación
    recorridos = {(estado, sig) for (_, estado, _, _, sig) in (log or []) if sig}
    estado_final = log[-1][4] if log else None

    # Dibujar estados (doble círculo si es de aceptación)
    for s in sorted(afd.estados):
        if s in afd.estados_aceptacion:
            texto = f"{s}\\n[{afd.estados_aceptacion[s]}]" if s != afd.estados_aceptacion[s] else s
            forma = "doublecircle"
        else:
            texto, forma = s, "circle"
        grosor = "3" if s == estado_final else "1"
        dot.node(s, label=texto, shape=forma, penwidth=grosor)

    # Flecha al estado inicial
    dot.edge("", afd.estado_inicial)

    # Agrupar símbolos por (origen, destino)
    etiquetas = {}
    for (origen, simbolo), destino in afd.transiciones.items():
        etiquetas.setdefault((origen, destino), []).append(simbolo)

    for (origen, destino), simbolos in etiquetas.items():
        if (origen, destino) in recorridos:
            dot.edge(origen, destino, label=etiqueta(simbolos), color="blue", penwidth="2")
        else:
            dot.edge(origen, destino, label=etiqueta(simbolos))

    return dot


def tabla_pasos(log: list) -> str:
    if not log:
        return "  No hubo transiciones."
    filas = [f"  {'#':>2}  {'Estado actual':<20} {'Carácter':<9} {'Símbolo':<15} Nuevo estado"]
    for i, estado, c, simbolo, siguiente in log:
        filas.append(f"  {i:>2}  {estado:<20} {c!r:<9} {simbolo:<15} {siguiente or 'ERROR'}")
    return "\n".join(filas)


def tabla_transiciones(afd: AFD) -> str:
    etiquetas = {}
    for (origen, simbolo), destino in afd.transiciones.items():
        etiquetas.setdefault(origen, {}).setdefault(destino, []).append(simbolo)

    filas = [f"AFD {afd.nombre}: {len(afd.estados)} estados, inicial = {afd.estado_inicial}"]
    for estado in sorted(afd.estados, key=lambda s: (s != afd.estado_inicial, s)):
        tipo = f"ACEPTA {afd.estados_aceptacion[estado]}" if estado in afd.estados_aceptacion else "-"
        salidas = [f"[{etiqueta(sims)}] -> {dest}" for dest, sims in etiquetas.get(estado, {}).items()]
        filas.append(f"  {estado:<14} ({tipo}): {';  '.join(salidas) or '(sin salidas)'}")
    return "\n".join(filas)


def guardar_afd(afd: AFD, carpeta: Path, log: Optional[list] = None) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    dot = dibujar_afd(afd, log)
    ruta = carpeta / f"{afd.nombre.lower()}.dot"
    dot.save(ruta)
    if shutil.which("dot"):
        dot.render(ruta, outfile=ruta.with_suffix(".png"))
    return ruta
