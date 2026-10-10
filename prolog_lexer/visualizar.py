"""
Visualización de los AFD (apoyo para el informe).

- `a_dot(afd)` genera el código Graphviz (DOT) del autómata.
- `tabla_transiciones(afd)` genera una tabla de texto con estados y transiciones.

Si Graphviz está instalado (comando `dot`), `guardar(afd, carpeta)` también crea
la imagen PNG. Si no, el archivo .dot se puede abrir en https://dreampuf.github.io/GraphvizOnline
"""

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

from .automatas import AFD, ALFABETO, DIGITOS, MAYUSCULAS, MINUSCULAS, OTRO

_NOMBRES_ESPECIALES = {" ": "␣", "\t": "\\t", "\n": "\\n", "\r": "\\r", OTRO: "otro"}


def _mostrar(s: str) -> str:
    return _NOMBRES_ESPECIALES.get(s, s)


def etiqueta(simbolos: Set[str]) -> str:
    """Resume un conjunto de símbolos: 'a-z, A-Z, 0-9, _' o 'todo excepto *'."""
    faltan = ALFABETO - simbolos
    if len(faltan) <= 4 and len(simbolos) > len(faltan):
        if not faltan:
            return "cualquiera"
        return "todo excepto " + " ".join(_mostrar(s) for s in sorted(faltan))

    partes, resto = [], set(simbolos)
    for grupo, texto in ((MINUSCULAS, "a-z"), (MAYUSCULAS, "A-Z"), (DIGITOS, "0-9")):
        if grupo <= resto:
            partes.append(texto)
            resto -= grupo
    partes += [_mostrar(s) for s in sorted(resto)]
    return ", ".join(partes)


def _agrupar(afd: AFD) -> Dict[Tuple[str, str], Set[str]]:
    """Junta las transiciones que van del mismo origen al mismo destino."""
    grupos: Dict[Tuple[str, str], Set[str]] = {}
    for (origen, s), destino in afd.transiciones.items():
        grupos.setdefault((origen, destino), set()).add(s)
    return grupos


def _orden(estado: str):
    return int(estado[1:]) if estado[1:].isdigit() else estado


def _escapar_dot(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace('"', '\\"')


def a_dot(afd: AFD) -> str:
    lineas = [
        f'digraph "{afd.nombre}" {{',
        "  rankdir=LR;",
        '  node [fontname="Helvetica"]; edge [fontname="Helvetica", fontsize=10];',
        '  inicio [shape=point, label=""];',
    ]
    for estado in sorted(afd.estados, key=_orden):
        if estado in afd.aceptacion:
            lineas.append(
                f'  {estado} [shape=doublecircle, label="{estado}\\n{afd.aceptacion[estado]}"];'
            )
        else:
            lineas.append(f"  {estado} [shape=circle];")
    lineas.append(f"  inicio -> {afd.inicial};")
    for (origen, destino), simbolos in _agrupar(afd).items():
        lineas.append(f'  {origen} -> {destino} [label="{_escapar_dot(etiqueta(simbolos))}"];')
    lineas.append("}")
    return "\n".join(lineas)


def tabla_transiciones(afd: AFD) -> str:
    """Tabla legible: estado | tipo | transiciones."""
    filas: List[str] = [f"AFD {afd.nombre}: {len(afd.estados)} estados, inicial = {afd.inicial}"]
    grupos = _agrupar(afd)
    for estado in sorted(afd.estados, key=_orden):
        tipo = []
        if estado == afd.inicial:
            tipo.append("inicial")
        if estado in afd.aceptacion:
            tipo.append(f"acepta {afd.aceptacion[estado]}")
        salidas = [
            f"[{etiqueta(sims)}] -> {destino}"
            for (origen, destino), sims in grupos.items()
            if origen == estado
        ]
        filas.append(f"  {estado:>4} ({', '.join(tipo) or '-'}): {';  '.join(salidas) or '(sin salidas)'}")
    return "\n".join(filas)


def guardar(afd: AFD, carpeta: Path) -> Path:
    """Escribe <nombre>.dot y, si existe Graphviz, también <nombre>.png."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_dot = carpeta / f"{afd.nombre.lower()}.dot"
    ruta_dot.write_text(a_dot(afd), encoding="utf-8")
    if shutil.which("dot"):
        subprocess.run(["dot", "-Tpng", str(ruta_dot), "-o", str(ruta_dot.with_suffix(".png"))], check=True)
    return ruta_dot
