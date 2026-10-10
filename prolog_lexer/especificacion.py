"""
PUNTO 1 - Especificación del subconjunto de Prolog.

Para cada categoría léxica se indica:
  - nombre del token
  - descripción del patrón (en palabras)
  - ejemplos válidos
  - ejemplos inválidos
  - atributo asociado (cuando corresponde)

Convenciones generales del subconjunto:
  - Las letras de átomos y variables son solo ASCII (a-z, A-Z).
    Caracteres como 'é' o 'ñ' solo se admiten dentro de comillas.
  - Los números NO llevan signo: "-5" son dos tokens (OP_RESTA, ENTERO).
  - Los reales llevan parte entera y decimal ("3.14"); el exponente es opcional
    ("1.5e10", "2.0E-3"). "3." y ".5" no son reales.
  - Secuencias de escape admitidas en cadenas y átomos entre comillas:
    \\n  \\t  \\r  \\\\  \\'  \\"   (además, '' dentro de '...' y "" dentro de "...")
  - Las cadenas y átomos entre comillas no pueden contener saltos de línea.
  - Los comentarios de bloque /* ... */ no se anidan.
  - Espacios, tabulaciones y saltos de línea se reconocen como ESPACIO y luego
    se ignoran (pero sirven para llevar la cuenta de línea y columna).
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class CategoriaLexica:
    token: str
    descripcion: str
    validos: List[str]
    invalidos: List[str] = field(default_factory=list)
    atributo: str = "-"


# ---------------------------------------------------------------------------
# Operadores y delimitadores: son lexemas fijos (literales).
# lexema -> nombre del token
# ---------------------------------------------------------------------------
OPERADORES = {
    # Cláusulas y consultas
    ":-": "OP_REGLA",
    "?-": "OP_CONSULTA",
    "-->": "OP_DCG",
    # Unificación y comparación
    "=": "OP_UNIFICA",
    "\\=": "OP_NO_UNIFICA",
    "==": "OP_IDENTICO",
    "\\==": "OP_NO_IDENTICO",
    "=..": "OP_UNIV",
    "<": "OP_MENOR",
    "=<": "OP_MENOR_IGUAL",
    ">": "OP_MAYOR",
    ">=": "OP_MAYOR_IGUAL",
    # Aritméticos
    "+": "OP_SUMA",
    "-": "OP_RESTA",
    "*": "OP_MULT",
    "/": "OP_DIV",
    "//": "OP_DIV_ENTERA",
    "**": "OP_POTENCIA",
    # Control
    "\\+": "OP_NEGACION",
    "!": "CORTE",
    ";": "PUNTO_Y_COMA",
    ",": "COMA",
    # Delimitadores
    "(": "PARENTESIS_IZQ",
    ")": "PARENTESIS_DER",
    "[": "CORCHETE_IZQ",
    "]": "CORCHETE_DER",
    "{": "LLAVE_IZQ",
    "}": "LLAVE_DER",
    "|": "BARRA",
    ".": "PUNTO",
}

# Átomos que funcionan como operadores (palabras reservadas).
# Tienen la misma forma que un ATOMO, por eso necesitan prioridad (ver punto 2).
PALABRAS_RESERVADAS = {
    "is": "OP_IS",
    "mod": "OP_MOD",
}

# Ejemplos inválidos para operadores: prefijos que no son operadores por sí solos.
_INVALIDOS_OPERADOR = {
    ":-": [":"],
    "?-": ["?"],
    "-->": ["--"],
    "\\=": ["\\"],
    "=..": ["=."],
}


# ---------------------------------------------------------------------------
# Catálogo de tokens
# ---------------------------------------------------------------------------
CATEGORIAS: List[CategoriaLexica] = [
    CategoriaLexica(
        "ATOMO",
        "Letra minúscula seguida de letras, dígitos o guion bajo.",
        ["padre", "persona_1", "x", "juanPerez"],
        ["Padre", "1abc", "_x", "per-sona"],
        "Índice en la tabla de lexemas",
    ),
    CategoriaLexica(
        "ATOMO_COMILLAS",
        "Texto entre comillas simples; admite espacios, símbolos, escapes y ''.",
        ["'Juan Pérez'", "':-'", "'it''s'", "'a\\nb'", "''"],
        ["'sin cierre", "'a\nb'", "'mal\\q'"],
        "Índice en la tabla de lexemas",
    ),
    CategoriaLexica(
        "VARIABLE",
        "Letra mayúscula, o guion bajo seguido de al menos un carácter, "
        "continuado por letras, dígitos o guion bajo.",
        ["X", "Persona", "_Temporal", "_x1", "Lista_2"],
        ["persona", "1X", "_"],
        "Índice en la tabla de lexemas",
    ),
    CategoriaLexica(
        "VARIABLE_ANONIMA",
        "El guion bajo solo.",
        ["_"],
        ["__", "_X"],
    ),
    CategoriaLexica(
        "ENTERO",
        "Uno o más dígitos, sin signo.",
        ["0", "25", "007"],
        ["-5", "2a", "3.14"],
        "Valor numérico (int)",
    ),
    CategoriaLexica(
        "REAL",
        "Dígitos, punto, dígitos y exponente opcional (e/E, signo opcional, dígitos).",
        ["3.14", "0.5", "1.5e10", "2.0E-3"],
        ["3.", ".5", "1e10", "1.5e"],
        "Valor numérico (float)",
    ),
    CategoriaLexica(
        "CADENA",
        'Texto entre comillas dobles; admite escapes y "".',
        ['"hola"', '"Hola mundo"', '"dice \\"si\\""', '""'],
        ['"sin cierre', '"a\nb"'],
        "Índice en la tabla de lexemas",
    ),
    CategoriaLexica(
        "COMENTARIO_LINEA",
        "Desde % hasta el final de la línea (se ignora).",
        ["% Hechos", "%", "%% doble"],
        ["Hechos %"],
    ),
    CategoriaLexica(
        "COMENTARIO_BLOQUE",
        "Desde /* hasta el primer */ (no anidado; se ignora).",
        ["/* hola */", "/**/", "/* a\nb */", "/* ** */"],
        ["/* sin cierre", "/* a */ b */"],
    ),
    CategoriaLexica(
        "ESPACIO",
        "Uno o más espacios, tabulaciones o saltos de línea (se ignora).",
        [" ", "\t", "\n", "  \n\t "],
        ["x "],
    ),
]

# Palabras reservadas (is, mod)
for _lexema, _token in PALABRAS_RESERVADAS.items():
    CATEGORIAS.append(
        CategoriaLexica(
            _token,
            f"Átomo operador '{_lexema}' (palabra reservada).",
            [_lexema],
            [_lexema.upper(), _lexema + "x"],
        )
    )

# Operadores y delimitadores
for _lexema, _token in OPERADORES.items():
    CATEGORIAS.append(
        CategoriaLexica(
            _token,
            f"Literal {_lexema}",
            [_lexema],
            _INVALIDOS_OPERADOR.get(_lexema, []),
        )
    )

# Tokens que el analizador reconoce pero descarta.
TOKENS_IGNORADOS = {"ESPACIO", "COMENTARIO_LINEA", "COMENTARIO_BLOQUE"}


def categoria(token: str) -> CategoriaLexica:
    for c in CATEGORIAS:
        if c.token == token:
            return c
    raise KeyError(token)


def _mostrar(lexema: str) -> str:
    """Hace visibles los saltos de línea (⏎) y tabulaciones (⇥) reales de un ejemplo."""
    return lexema.replace("\n", "⏎").replace("\t", "⇥").replace("|", "\\|")


def tabla_markdown() -> str:
    """Genera la tabla de especificación en Markdown (útil para el informe).
    En los ejemplos, ⏎ es un salto de línea real y ⇥ una tabulación real."""
    from .expresiones_regulares import EXPRESIONES

    filas = [
        "| Token | Descripción | Expresión regular | Ejemplos válidos | Ejemplos inválidos | Atributo |",
        "|---|---|---|---|---|---|",
    ]
    for c in CATEGORIAS:
        er = _mostrar(EXPRESIONES[c.token])
        validos = ", ".join(f"`{_mostrar(v)}`" for v in c.validos)
        invalidos = ", ".join(f"`{_mostrar(v)}`" for v in c.invalidos) or "-"
        filas.append(
            f"| {c.token} | {_mostrar(c.descripcion)} | `{er}` | {validos} | {invalidos} | {c.atributo} |"
        )
    return "\n".join(filas)
