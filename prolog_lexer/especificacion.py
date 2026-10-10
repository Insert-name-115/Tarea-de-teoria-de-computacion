# -------------------------------------------------------------------
# PUNTO 1 - Especificación del subconjunto de Prolog
# -------------------------------------------------------------------
# Comentarios:
# - Cada categoría léxica (token) se describe con:
#     'token'      -> nombre del token
#     'descripcion'-> el patrón explicado en palabras
#     'validos'    -> ejemplos que SÍ son de esta categoría
#     'invalidos'  -> ejemplos que NO lo son
#     'atributo'   -> información extra que guarda el token
#
# Convenciones del grupo (decisiones de diseño):
# - Átomos y variables usan solo letras ASCII (a-z, A-Z). Letras como
#   'é' o 'ñ' solo se permiten dentro de comillas.
# - Los números NO llevan signo: "-5" son dos tokens (OP_RESTA, ENTERO).
# - Un real necesita parte entera y parte decimal: "3.14".
#   "3." y ".5" no son reales. No se usa notación exponencial.
# - Escapes en cadenas y átomos entre comillas: una barra invertida
#   seguida de cualquier carácter (\n, \t, \\, \', \"...).
#   También '' dentro de '...' y "" dentro de "..." representan la comilla.
# - Cadenas y átomos entre comillas no pueden tener saltos de línea.
# - Los comentarios /* ... */ no se anidan.
# - Espacios, tabs y saltos de línea se reconocen como ESPACIO y luego
#   se ignoran (solo sirven para contar líneas y columnas).
# -------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import List


@dataclass
class CategoriaLexica:
    token: str
    descripcion: str
    validos: List[str]
    invalidos: List[str] = field(default_factory=list)
    atributo: str = "-"


# Operadores y delimitadores: lexemas fijos  (lexema -> token)
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
# Tienen la misma forma que un ATOMO -> se resuelve por prioridad (punto 2).
PALABRAS_RESERVADAS = {
    "is": "OP_IS",
    "mod": "OP_MOD",
}

# Prefijos de operadores que NO son operadores por sí solos
INVALIDOS_OPERADOR = {
    ":-": [":"],
    "?-": ["?"],
    "-->": ["--"],
    "\\=": ["\\"],
    "=..": ["=."],
}

# Tokens que se reconocen pero luego se descartan
TOKENS_IGNORADOS = {"ESPACIO", "COMENTARIO_LINEA", "COMENTARIO_BLOQUE"}


# -------------------------------------------------------------------
# Catálogo de tokens
# -------------------------------------------------------------------
CATEGORIAS: List[CategoriaLexica] = [
    CategoriaLexica(
        token="ATOMO",
        descripcion="Letra minúscula seguida de letras, dígitos o guion bajo.",
        validos=["padre", "persona_1", "x", "juanPerez"],
        invalidos=["Padre", "1abc", "_x", "per-sona"],
        atributo="Índice en la tabla de lexemas",
    ),
    CategoriaLexica(
        token="ATOMO_COMILLAS",
        descripcion="Texto entre comillas simples; admite espacios, símbolos, escapes y ''.",
        validos=["'Juan Pérez'", "':-'", "'it''s'", "'a\\nb'", "''"],
        invalidos=["'sin cierre", "'a\nb'", "'x'y'"],
        atributo="Índice en la tabla de lexemas",
    ),
    CategoriaLexica(
        token="VARIABLE",
        descripcion="Letra mayúscula, o guion bajo seguido de al menos un carácter; "
                    "luego letras, dígitos o guion bajo.",
        validos=["X", "Persona", "_Temporal", "_x1", "Lista_2"],
        invalidos=["persona", "1X", "_"],
        atributo="Índice en la tabla de lexemas",
    ),
    CategoriaLexica(
        token="VARIABLE_ANONIMA",
        descripcion="El guion bajo solo.",
        validos=["_"],
        invalidos=["__", "_X"],
    ),
    CategoriaLexica(
        token="ENTERO",
        descripcion="Uno o más dígitos, sin signo.",
        validos=["0", "25", "007"],
        invalidos=["-5", "2a", "3.14"],
        atributo="Valor numérico (int)",
    ),
    CategoriaLexica(
        token="REAL",
        descripcion="Dígitos, un punto y dígitos.",
        validos=["3.14", "0.5", "10.0"],
        invalidos=["3.", ".5", "1.5e10", "1.2.3"],
        atributo="Valor numérico (float)",
    ),
    CategoriaLexica(
        token="CADENA",
        descripcion='Texto entre comillas dobles; admite escapes y "".',
        validos=['"hola"', '"Hola mundo"', '"dice \\"si\\""', '""'],
        invalidos=['"sin cierre', '"a\nb"'],
        atributo="Índice en la tabla de lexemas",
    ),
    CategoriaLexica(
        token="COMENTARIO_LINEA",
        descripcion="Desde % hasta el final de la línea (se ignora).",
        validos=["% Hechos", "%", "%% doble"],
        invalidos=["Hechos %"],
    ),
    CategoriaLexica(
        token="COMENTARIO_BLOQUE",
        descripcion="Desde /* hasta el primer */ (no anidado; se ignora).",
        validos=["/* hola */", "/**/", "/* a\nb */", "/* ** */"],
        invalidos=["/* sin cierre", "/* a */ b */"],
    ),
    CategoriaLexica(
        token="ESPACIO",
        descripcion="Uno o más espacios, tabulaciones o saltos de línea (se ignora).",
        validos=[" ", "\t", "\n", "  \n\t "],
        invalidos=["x "],
    ),
]

# Palabras reservadas (is, mod)
for lexema, token in PALABRAS_RESERVADAS.items():
    CATEGORIAS.append(CategoriaLexica(
        token=token,
        descripcion=f"Átomo operador '{lexema}' (palabra reservada).",
        validos=[lexema],
        invalidos=[lexema.upper(), lexema + "x"],
    ))

# Operadores y delimitadores
for lexema, token in OPERADORES.items():
    CATEGORIAS.append(CategoriaLexica(
        token=token,
        descripcion=f"Literal {lexema}",
        validos=[lexema],
        invalidos=INVALIDOS_OPERADOR.get(lexema, []),
    ))


def buscar_categoria(token: str) -> CategoriaLexica:
    for c in CATEGORIAS:
        if c.token == token:
            return c
    raise KeyError(f"No existe la categoría {token}")


def mostrar_visible(texto: str) -> str:
    """Hace visibles los saltos de línea (⏎) y tabs (⇥) reales de un ejemplo."""
    return texto.replace("\n", "⏎").replace("\t", "⇥").replace("|", "\\|")


def tabla_markdown() -> str:
    """Genera la tabla de especificación en Markdown (para copiar al informe)."""
    from .expresiones_regulares import EXPRESIONES

    filas = [
        "| Token | Descripción | Expresión regular | Ejemplos válidos | Ejemplos inválidos | Atributo |",
        "|---|---|---|---|---|---|",
    ]
    for c in CATEGORIAS:
        er = mostrar_visible(EXPRESIONES[c.token])
        validos = ", ".join(f"`{mostrar_visible(v)}`" for v in c.validos)
        invalidos = ", ".join(f"`{mostrar_visible(v)}`" for v in c.invalidos) or "-"
        filas.append(f"| {c.token} | {mostrar_visible(c.descripcion)} | `{er}` "
                     f"| {validos} | {invalidos} | {c.atributo} |")
    return "\n".join(filas)
