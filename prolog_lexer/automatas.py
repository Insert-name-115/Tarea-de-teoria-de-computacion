# -------------------------------------------------------------------
# PUNTO 3 - Modelado con autómatas (AFD)
# -------------------------------------------------------------------
# Comentarios:
# - Igual que en el Laboratorio 1, cada AFD se define con:
#     'estados'            -> conjunto de estados
#     'alfabeto'           -> conjunto de símbolos de entrada
#     'transiciones'       -> mapea (estado, símbolo) -> nuevo_estado
#     'estado_inicial'     -> estado de partida
#     'estados_aceptacion' -> estado de aceptación -> token que reconoce
#
# - El alfabeto NO son caracteres sueltos, sino CLASES de caracteres
#   (minuscula, mayuscula, digito, ...). Así las tablas quedan cortas.
#   La función 'clase_de' traduce cada carácter del texto a su clase.
#
# - Si no hay transición para (estado, símbolo), el AFD pasa a un
#   estado de error implícito y se detiene (AFD parcial).
#
# - Las palabras reservadas (is, mod) se reconocen primero como ATOMO
#   y luego se buscan en la tabla PALABRAS_RESERVADAS.
# -------------------------------------------------------------------

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .especificacion import OPERADORES, PALABRAS_RESERVADAS

# -------------------------------------------------------------------
# Alfabeto (clases de caracteres)
# -------------------------------------------------------------------
SIMBOLOS_OPERADOR = set(":?->=.<+*/!;,()[]{}|")

CARACTERES_ESPECIALES = {
    "_": "guion_bajo",
    " ": "espacio",
    "\t": "espacio",
    "\r": "espacio",
    "\n": "salto",
    "'": "comilla_simple",
    '"': "comilla_doble",
    "\\": "barra_inv",
    "%": "porcentaje",
}

ALFABETO: Set[str] = (
    {"minuscula", "mayuscula", "digito", "otro"}
    | set(CARACTERES_ESPECIALES.values())
    | SIMBOLOS_OPERADOR
)

LETRA_O_DIGITO = ["minuscula", "mayuscula", "digito", "guion_bajo"]


def clase_de(c: str) -> str:
    """Traduce un carácter a su símbolo del alfabeto."""
    if "a" <= c <= "z":
        return "minuscula"
    if "A" <= c <= "Z":
        return "mayuscula"
    if "0" <= c <= "9":
        return "digito"
    if c in CARACTERES_ESPECIALES:
        return CARACTERES_ESPECIALES[c]
    if c in SIMBOLOS_OPERADOR:
        return c
    return "otro"  # @, #, $, é, ñ, ...


def todos_menos(*excluidos: str) -> Set[str]:
    """Todos los símbolos del alfabeto excepto los indicados."""
    return ALFABETO - set(excluidos)


# -------------------------------------------------------------------
# Clase AFD
# -------------------------------------------------------------------
@dataclass
class AFD:
    nombre: str
    estados: Set[str]
    alfabeto: Set[str]
    transiciones: Dict[Tuple[str, str], str]
    estado_inicial: str
    estados_aceptacion: Dict[str, str]  # estado -> token

    def paso(self, estado: str, simbolo: str) -> Optional[str]:
        """Realiza una transición. Si no existe devuelve None (error)."""
        return self.transiciones.get((estado, simbolo))

    def simular(self, cadena: str):
        """
        Simula el AFD sobre una cadena.
        Devuelve (estado_final, log); estado_final es None si se trabó.
        Cada paso del log es (i, estado, caracter, simbolo, nuevo_estado).
        """
        actual = self.estado_inicial
        log = []
        for i, c in enumerate(cadena):
            simbolo = clase_de(c)
            siguiente = self.paso(actual, simbolo)
            log.append((i, actual, c, simbolo, siguiente))
            if siguiente is None:
                return None, log
            actual = siguiente
        return actual, log

    def acepta(self, cadena: str) -> bool:
        final, _ = self.simular(cadena)
        return final in self.estados_aceptacion

    def token_de(self, cadena: str) -> Optional[str]:
        """Token que reconoce la cadena completa (o None)."""
        final, _ = self.simular(cadena)
        return self.estados_aceptacion.get(final)

    def reconocer(self, texto: str, inicio: int = 0) -> Tuple[Optional[str], str]:
        """
        MÁXIMA COINCIDENCIA: avanza mientras haya transición y recuerda
        el último estado de aceptación visitado. Devuelve (token, lexema).
        """
        actual = self.estado_inicial
        ultimo_token, fin = None, inicio
        i = inicio
        while i < len(texto):
            actual = self.paso(actual, clase_de(texto[i]))
            if actual is None:
                break
            i += 1
            if actual in self.estados_aceptacion:
                ultimo_token, fin = self.estados_aceptacion[actual], i
        return ultimo_token, texto[inicio:fin]


# -------------------------------------------------------------------
# AFD 1: ATOMO        ER: [a-z][a-zA-Z0-9_]*
#   Inicio --minuscula--> Atomo
#   Atomo  --letra|digito|_--> Atomo        (ACEPTA)
# -------------------------------------------------------------------
afd_atomo = AFD(
    nombre="ATOMO",
    estados={"Inicio", "Atomo"},
    alfabeto=ALFABETO,
    transiciones={
        ("Inicio", "minuscula"): "Atomo",
        **{("Atomo", s): "Atomo" for s in LETRA_O_DIGITO},
    },
    estado_inicial="Inicio",
    estados_aceptacion={"Atomo": "ATOMO"},
)

# -------------------------------------------------------------------
# AFD 2: VARIABLE     ER: _ | _[a-zA-Z0-9_]+ | [A-Z][a-zA-Z0-9_]*
#   Inicio  --guion_bajo--> Anonima          (ACEPTA VARIABLE_ANONIMA)
#   Inicio  --mayuscula--> Variable          (ACEPTA VARIABLE)
#   Anonima --letra|digito|_--> Variable
#   Variable--letra|digito|_--> Variable
# -------------------------------------------------------------------
afd_variable = AFD(
    nombre="VARIABLE",
    estados={"Inicio", "Anonima", "Variable"},
    alfabeto=ALFABETO,
    transiciones={
        ("Inicio", "guion_bajo"): "Anonima",
        ("Inicio", "mayuscula"): "Variable",
        **{("Anonima", s): "Variable" for s in LETRA_O_DIGITO},
        **{("Variable", s): "Variable" for s in LETRA_O_DIGITO},
    },
    estado_inicial="Inicio",
    estados_aceptacion={"Anonima": "VARIABLE_ANONIMA", "Variable": "VARIABLE"},
)

# -------------------------------------------------------------------
# AFD 3: NUMERO       ER: [0-9]+  |  [0-9]+\.[0-9]+
#   Inicio      --digito--> Entero           (ACEPTA ENTERO)
#   Entero      --digito--> Entero
#   Entero      --'.'-->    EnteroPunto      (todavía no es real)
#   EnteroPunto --digito--> Real             (ACEPTA REAL)
#   Real        --digito--> Real
# -------------------------------------------------------------------
afd_numero = AFD(
    nombre="NUMERO",
    estados={"Inicio", "Entero", "EnteroPunto", "Real"},
    alfabeto=ALFABETO,
    transiciones={
        ("Inicio", "digito"): "Entero",
        ("Entero", "digito"): "Entero",
        ("Entero", "."): "EnteroPunto",
        ("EnteroPunto", "digito"): "Real",
        ("Real", "digito"): "Real",
    },
    estado_inicial="Inicio",
    estados_aceptacion={"Entero": "ENTERO", "Real": "REAL"},
)


# -------------------------------------------------------------------
# AFD 4 y 5: ATOMO_COMILLAS y CADENA (misma forma, distinta comilla)
#   ER: C([^C\\\n] | \\. | CC)*C        (C = la comilla)
#   Inicio  --C--> Abierto
#   Abierto --cualquiera menos C, \ y salto--> Abierto
#   Abierto --barra_inv--> Escape
#   Escape  --cualquiera menos salto--> Abierto
#   Abierto --C--> Cerrado                   (ACEPTA)
#   Cerrado --C--> Abierto                   ('' = comilla dentro del texto)
# -------------------------------------------------------------------
def crear_afd_comillas(comilla: str, token: str, prefijo: str) -> AFD:
    abierto, escape, cerrado = f"{prefijo}_Abierto", f"{prefijo}_Escape", f"{prefijo}_Cerrado"
    return AFD(
        nombre=token,
        estados={"Inicio", abierto, escape, cerrado},
        alfabeto=ALFABETO,
        transiciones={
            ("Inicio", comilla): abierto,
            **{(abierto, s): abierto for s in todos_menos(comilla, "barra_inv", "salto")},
            (abierto, "barra_inv"): escape,
            **{(escape, s): abierto for s in todos_menos("salto")},
            (abierto, comilla): cerrado,
            (cerrado, comilla): abierto,
        },
        estado_inicial="Inicio",
        estados_aceptacion={cerrado: token},
    )


afd_atomo_comillas = crear_afd_comillas("comilla_simple", "ATOMO_COMILLAS", "AC")
afd_cadena = crear_afd_comillas("comilla_doble", "CADENA", "CAD")

# -------------------------------------------------------------------
# AFD 6: COMENTARIO_LINEA     ER: %[^\n]*
#   Inicio    --porcentaje--> ComLinea       (ACEPTA)
#   ComLinea  --cualquiera menos salto--> ComLinea
# -------------------------------------------------------------------
afd_comentario_linea = AFD(
    nombre="COMENTARIO_LINEA",
    estados={"Inicio", "ComLinea"},
    alfabeto=ALFABETO,
    transiciones={
        ("Inicio", "porcentaje"): "ComLinea",
        **{("ComLinea", s): "ComLinea" for s in todos_menos("salto")},
    },
    estado_inicial="Inicio",
    estados_aceptacion={"ComLinea": "COMENTARIO_LINEA"},
)

# -------------------------------------------------------------------
# AFD 7: COMENTARIO_BLOQUE    ER: /\*[^*]*\*+([^*/][^*]*\*+)*/
#   Inicio      --'/'--> CB_Barra
#   CB_Barra    --'*'--> CB_Dentro
#   CB_Dentro   --cualquiera menos '*'--> CB_Dentro
#   CB_Dentro   --'*'--> CB_Asterisco
#   CB_Asterisco--'*'--> CB_Asterisco
#   CB_Asterisco--cualquiera menos '*' y '/'--> CB_Dentro
#   CB_Asterisco--'/'--> CB_Cerrado          (ACEPTA)
# -------------------------------------------------------------------
afd_comentario_bloque = AFD(
    nombre="COMENTARIO_BLOQUE",
    estados={"Inicio", "CB_Barra", "CB_Dentro", "CB_Asterisco", "CB_Cerrado"},
    alfabeto=ALFABETO,
    transiciones={
        ("Inicio", "/"): "CB_Barra",
        ("CB_Barra", "*"): "CB_Dentro",
        **{("CB_Dentro", s): "CB_Dentro" for s in todos_menos("*")},
        ("CB_Dentro", "*"): "CB_Asterisco",
        ("CB_Asterisco", "*"): "CB_Asterisco",
        **{("CB_Asterisco", s): "CB_Dentro" for s in todos_menos("*", "/")},
        ("CB_Asterisco", "/"): "CB_Cerrado",
    },
    estado_inicial="Inicio",
    estados_aceptacion={"CB_Cerrado": "COMENTARIO_BLOQUE"},
)

# -------------------------------------------------------------------
# AFD 8: ESPACIO      ER: [ \t\r\n]+
#   Inicio  --espacio|salto--> Espacio       (ACEPTA)
#   Espacio --espacio|salto--> Espacio
# -------------------------------------------------------------------
afd_espacio = AFD(
    nombre="ESPACIO",
    estados={"Inicio", "Espacio"},
    alfabeto=ALFABETO,
    transiciones={
        ("Inicio", "espacio"): "Espacio",
        ("Inicio", "salto"): "Espacio",
        ("Espacio", "espacio"): "Espacio",
        ("Espacio", "salto"): "Espacio",
    },
    estado_inicial="Inicio",
    estados_aceptacion={"Espacio": "ESPACIO"},
)

# -------------------------------------------------------------------
# AFD 9: OPERADORES Y DELIMITADORES
# Comentarios:
# - Es un árbol de prefijos: cada estado representa lo leído hasta ahora.
# - Los estados de aceptación tienen el nombre del token que reconocen.
# - Estados intermedios SIN aceptación: DosPuntos (':'), Interrogacion ('?'),
#   MenosMenos ('--'), IgualPunto ('=.'), BarraInv ('\').
# -------------------------------------------------------------------
afd_operadores = AFD(
    nombre="OPERADORES",
    estados=(
        {"Inicio", "DosPuntos", "Interrogacion", "MenosMenos", "IgualPunto", "BarraInv"}
        | set(OPERADORES.values())
    ),
    alfabeto=ALFABETO,
    transiciones={
        # :-   ?-
        ("Inicio", ":"): "DosPuntos",
        ("DosPuntos", "-"): "OP_REGLA",
        ("Inicio", "?"): "Interrogacion",
        ("Interrogacion", "-"): "OP_CONSULTA",
        # -   -->
        ("Inicio", "-"): "OP_RESTA",
        ("OP_RESTA", "-"): "MenosMenos",
        ("MenosMenos", ">"): "OP_DCG",
        # =   ==   =..   =<
        ("Inicio", "="): "OP_UNIFICA",
        ("OP_UNIFICA", "="): "OP_IDENTICO",
        ("OP_UNIFICA", "."): "IgualPunto",
        ("IgualPunto", "."): "OP_UNIV",
        ("OP_UNIFICA", "<"): "OP_MENOR_IGUAL",
        # \=   \==   \+
        ("Inicio", "barra_inv"): "BarraInv",
        ("BarraInv", "="): "OP_NO_UNIFICA",
        ("OP_NO_UNIFICA", "="): "OP_NO_IDENTICO",
        ("BarraInv", "+"): "OP_NEGACION",
        # <   >   >=
        ("Inicio", "<"): "OP_MENOR",
        ("Inicio", ">"): "OP_MAYOR",
        ("OP_MAYOR", "="): "OP_MAYOR_IGUAL",
        # +   *   **   /   //
        ("Inicio", "+"): "OP_SUMA",
        ("Inicio", "*"): "OP_MULT",
        ("OP_MULT", "*"): "OP_POTENCIA",
        ("Inicio", "/"): "OP_DIV",
        ("OP_DIV", "/"): "OP_DIV_ENTERA",
        # Control y delimitadores de un carácter
        ("Inicio", "!"): "CORTE",
        ("Inicio", ";"): "PUNTO_Y_COMA",
        ("Inicio", ","): "COMA",
        ("Inicio", "("): "PARENTESIS_IZQ",
        ("Inicio", ")"): "PARENTESIS_DER",
        ("Inicio", "["): "CORCHETE_IZQ",
        ("Inicio", "]"): "CORCHETE_DER",
        ("Inicio", "{"): "LLAVE_IZQ",
        ("Inicio", "}"): "LLAVE_DER",
        ("Inicio", "|"): "BARRA",
        ("Inicio", "."): "PUNTO",
    },
    estado_inicial="Inicio",
    estados_aceptacion={token: token for token in OPERADORES.values()},
)


# -------------------------------------------------------------------
# AFD INTEGRADO (construcción del producto / unión de AFD)
# Comentarios:
# - Se simulan todos los AFD "en paralelo": un estado del integrado es
#   la tupla con el estado actual de cada AFD (None si ese AFD murió).
# - Solo se crean los estados alcanzables desde el inicio (recorrido BFS).
# - Si varios AFD aceptan a la vez, gana el primero de la lista.
# - Nombre de cada estado: los estados vivos unidos con '/'.
#   Ej: después de leer '/' quedan vivos CB_Barra y OP_DIV -> "CB_Barra/OP_DIV".
# -------------------------------------------------------------------
def unir_afds(afds: List[AFD], nombre: str) -> AFD:
    inicio = tuple(a.estado_inicial for a in afds)
    nombres = {inicio: "Inicio"}
    pendientes = deque([inicio])
    transiciones = {}
    estados_aceptacion = {}

    while pendientes:
        actual = pendientes.popleft()

        # ¿Algún AFD acepta en este estado? (gana el primero)
        for afd, q in zip(afds, actual):
            if q is not None and q in afd.estados_aceptacion:
                estados_aceptacion[nombres[actual]] = afd.estados_aceptacion[q]
                break

        for simbolo in sorted(ALFABETO):
            siguiente = tuple(
                afd.paso(q, simbolo) if q is not None else None
                for afd, q in zip(afds, actual)
            )
            if all(q is None for q in siguiente):
                continue  # todos murieron -> estado de error implícito
            if siguiente not in nombres:
                nombres[siguiente] = "/".join(q for q in siguiente if q is not None)
                pendientes.append(siguiente)
            transiciones[(nombres[actual], simbolo)] = nombres[siguiente]

    assert len(set(nombres.values())) == len(nombres), "Nombres de estado repetidos"
    return AFD(nombre, set(nombres.values()), ALFABETO, transiciones, "Inicio", estados_aceptacion)


AFDS_POR_CATEGORIA = [
    afd_atomo,
    afd_atomo_comillas,
    afd_variable,
    afd_numero,
    afd_cadena,
    afd_comentario_linea,
    afd_comentario_bloque,
    afd_espacio,
    afd_operadores,
]

afd_integrado = unir_afds(AFDS_POR_CATEGORIA, "INTEGRADO")


def reconocer_token(texto: str, inicio: int = 0) -> Tuple[Optional[str], str]:
    """
    Usa el AFD integrado con máxima coincidencia y luego revisa la tabla
    de palabras reservadas (is, mod). Devuelve (token, lexema).
    """
    token, lexema = afd_integrado.reconocer(texto, inicio)
    if token == "ATOMO" and lexema in PALABRAS_RESERVADAS:
        token = PALABRAS_RESERVADAS[lexema]
    return token, lexema


def token_de_lexema(lexema: str) -> Optional[str]:
    """Token del lexema COMPLETO según los autómatas (None si no es un token)."""
    token, reconocido = reconocer_token(lexema)
    return token if reconocido == lexema and lexema else None
