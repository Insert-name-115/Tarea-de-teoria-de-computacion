"""
PUNTO 2 - Expresiones regulares.

Una expresión regular (sintaxis del módulo `re` de Python) por cada categoría.

Notación usada:
  [a-z]   una letra minúscula          [^...]  cualquier carácter salvo los listados
  X*      cero o más                    X+      una o más
  X?      opcional                      (?:...) agrupación
  \\.     un punto literal (los símbolos especiales se escapan con \\)

Resolución de superposiciones (cuando un texto calza con varios patrones):
  1. MÁXIMA COINCIDENCIA: se elige el lexema más largo.
       "\\==" gana a "\\=" y a "==";  "=.." gana a "=";  ":-" gana a ":";
       "_X" (VARIABLE) gana a "_" (VARIABLE_ANONIMA);  "/*..*/" gana a "/".
  2. PRIORIDAD: si dos patrones reconocen el mismo lexema más largo, gana el que
     aparece primero en PRIORIDAD. Solo ocurre con las palabras reservadas:
       "is" calza con OP_IS y con ATOMO -> gana OP_IS.
       "isa" solo calza con ATOMO      -> ATOMO.
"""

import re
from typing import Dict, List, Optional, Tuple

from .especificacion import OPERADORES, PALABRAS_RESERVADAS

# Bloques reutilizables
LETRA_DIGITO = r"[a-zA-Z0-9_]"
ESCAPE = r"\\[ntr\\'\"]"

EXPRESIONES: Dict[str, str] = {
    # Palabras reservadas (van antes que ATOMO en la prioridad)
    **{token: re.escape(lexema) for lexema, token in PALABRAS_RESERVADAS.items()},
    "ATOMO": rf"[a-z]{LETRA_DIGITO}*",
    "ATOMO_COMILLAS": rf"'(?:[^'\\\n]|{ESCAPE}|'')*'",
    "VARIABLE": rf"_{LETRA_DIGITO}+|[A-Z]{LETRA_DIGITO}*",
    "VARIABLE_ANONIMA": r"_",
    "ENTERO": r"[0-9]+",
    "REAL": r"[0-9]+\.[0-9]+(?:[eE][+-]?[0-9]+)?",
    "CADENA": rf'"(?:[^"\\\n]|{ESCAPE}|"")*"',
    "COMENTARIO_LINEA": r"%[^\n]*",
    "COMENTARIO_BLOQUE": r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/",
    "ESPACIO": r"[ \t\r\n]+",
    # Operadores y delimitadores: el lexema literal, escapado
    **{token: re.escape(lexema) for lexema, token in OPERADORES.items()},
}

# Orden de prioridad para desempates (mismo largo): el primero gana.
PRIORIDAD: List[str] = list(EXPRESIONES.keys())

_COMPILADAS = {token: re.compile(er) for token, er in EXPRESIONES.items()}


def calza_completo(token: str, lexema: str) -> bool:
    """¿El lexema completo pertenece al lenguaje de la ER del token?"""
    return _COMPILADAS[token].fullmatch(lexema) is not None


def clasificar(lexema: str) -> Tuple[Optional[str], List[str]]:
    """
    Devuelve (token_elegido, todos_los_tokens_que_calzan) para un lexema completo.
    Sirve para mostrar las superposiciones y cómo las resuelve la prioridad.
    """
    candidatos = [t for t in PRIORIDAD if calza_completo(t, lexema)]
    return (candidatos[0] if candidatos else None), candidatos


def coincidencia_mas_larga(texto: str, inicio: int = 0) -> Tuple[Optional[str], str]:
    """
    Aplica máxima coincidencia + prioridad desde la posición `inicio`.
    Devuelve (token, lexema) o (None, "") si ningún patrón calza.
    """
    mejor_token, mejor_lexema = None, ""
    for token in PRIORIDAD:
        m = _COMPILADAS[token].match(texto, inicio)
        # '>' estricto: ante empate se queda el de mayor prioridad (el primero)
        if m and len(m.group()) > len(mejor_lexema):
            mejor_token, mejor_lexema = token, m.group()
    return mejor_token, mejor_lexema
