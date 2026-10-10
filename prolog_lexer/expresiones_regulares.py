# -------------------------------------------------------------------
# PUNTO 2 - Expresiones regulares
# -------------------------------------------------------------------
# Comentarios:
# - Hay una expresión regular (ER) por cada token, escrita con la
#   sintaxis del módulo 're' de Python:
#     [a-z]  una letra minúscula       [^...]  cualquiera menos los listados
#     X*     cero o más veces          X+      una o más veces
#     (?:..) agrupa sin capturar       \.      un punto literal
#
# - Cuando un texto calza con varias ER se aplican dos reglas:
#   1) MÁXIMA COINCIDENCIA: gana el lexema más largo.
#        \==  gana a  \=  y a  ==
#        =..  gana a  =
#        :-   gana a  :
#        _X   (VARIABLE) gana a  _  (VARIABLE_ANONIMA)
#        /*...*/ (comentario) gana a  /  (división)
#   2) PRIORIDAD: si dos ER reconocen el MISMO lexema, gana la que
#      aparece primero en el diccionario EXPRESIONES.
#        "is"  calza con OP_IS y con ATOMO  -> gana OP_IS
#        "isa" solo calza con ATOMO          -> ATOMO
# -------------------------------------------------------------------

import re
from typing import Dict, List, Optional, Tuple

from .especificacion import OPERADORES, PALABRAS_RESERVADAS

LETRA_O_DIGITO = r"[a-zA-Z0-9_]"
ESCAPE = r"\\[^\n]"  # barra invertida + cualquier carácter (menos salto de línea)

EXPRESIONES: Dict[str, str] = {
    # Palabras reservadas: van ANTES que ATOMO para tener más prioridad
    "OP_IS": r"is",
    "OP_MOD": r"mod",

    "ATOMO": rf"[a-z]{LETRA_O_DIGITO}*",
    "ATOMO_COMILLAS": rf"'(?:[^'\\\n]|{ESCAPE}|'')*'",
    "VARIABLE": rf"_{LETRA_O_DIGITO}+|[A-Z]{LETRA_O_DIGITO}*",
    "VARIABLE_ANONIMA": r"_",
    "ENTERO": r"[0-9]+",
    "REAL": r"[0-9]+\.[0-9]+",
    "CADENA": rf'"(?:[^"\\\n]|{ESCAPE}|"")*"',
    "COMENTARIO_LINEA": r"%[^\n]*",
    "COMENTARIO_BLOQUE": r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/",
    "ESPACIO": r"[ \t\r\n]+",
}

# Operadores y delimitadores: la ER es el mismo lexema (escapado)
for lexema, token in OPERADORES.items():
    EXPRESIONES[token] = re.escape(lexema)

assert set(PALABRAS_RESERVADAS.values()) <= set(EXPRESIONES), "Falta una ER de palabra reservada"

# Orden de prioridad: el primero de la lista gana en caso de empate
PRIORIDAD: List[str] = list(EXPRESIONES.keys())

ER_COMPILADAS = {token: re.compile(er) for token, er in EXPRESIONES.items()}


def calza_completo(token: str, lexema: str) -> bool:
    """¿El lexema COMPLETO pertenece al lenguaje de la ER del token?"""
    return ER_COMPILADAS[token].fullmatch(lexema) is not None


def clasificar(lexema: str) -> Tuple[Optional[str], List[str]]:
    """
    Devuelve (token_elegido, lista_de_tokens_que_calzan).
    Sirve para mostrar las superposiciones y cómo se resuelven.
    """
    candidatos = [t for t in PRIORIDAD if calza_completo(t, lexema)]
    elegido = candidatos[0] if candidatos else None
    return elegido, candidatos


def coincidencia_mas_larga(texto: str, inicio: int = 0) -> Tuple[Optional[str], str]:
    """
    Aplica máxima coincidencia + prioridad desde la posición 'inicio'.
    Devuelve (token, lexema), o (None, "") si ninguna ER calza.
    """
    mejor_token, mejor_lexema = None, ""
    for token in PRIORIDAD:
        m = ER_COMPILADAS[token].match(texto, inicio)
        # '>' estricto: si empatan en largo se queda el de mayor prioridad
        if m and len(m.group()) > len(mejor_lexema):
            mejor_token, mejor_lexema = token, m.group()
    return mejor_token, mejor_lexema
