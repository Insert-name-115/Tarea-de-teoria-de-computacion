"""
PUNTO 3 - Modelado con autómatas.

Se construye un AFD por cada categoría principal y luego un AFD INTEGRADO que
reconoce todos los tokens a la vez.

- Alfabeto: caracteres ASCII imprimibles + '\\t', '\\n', '\\r'. Cualquier otro
  carácter (por ejemplo 'é' o 'ñ') se lee como el símbolo especial OTRO.
- Las transiciones que no aparecen en la tabla van a un estado de error
  implícito (AFD parcial): el autómata se detiene y rechaza.
- `aceptacion` asocia cada estado de aceptación con el token que reconoce.

AFD integrado: se obtiene con la construcción del PRODUCTO (unión) de los AFD
de cada categoría. Cada estado del integrado es una tupla con el estado actual
de cada AFD componente. Si en un estado aceptan varios componentes, el token es
el del componente con mayor prioridad (mismo orden que en el punto 2).
"""

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .especificacion import OPERADORES, PALABRAS_RESERVADAS

# ---------------------------------------------------------------------------
# Alfabeto y conjuntos de símbolos
# ---------------------------------------------------------------------------
OTRO = "OTRO"  # símbolo que representa cualquier carácter fuera del alfabeto
ALFABETO: Set[str] = {chr(i) for i in range(32, 127)} | {"\t", "\n", "\r", OTRO}

MINUSCULAS = set("abcdefghijklmnopqrstuvwxyz")
MAYUSCULAS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITOS = set("0123456789")
LETRA_DIGITO = MINUSCULAS | MAYUSCULAS | DIGITOS | {"_"}
ESCAPES = set("ntr\\'\"")


def simbolo(c: str) -> str:
    """Convierte un carácter del texto en un símbolo del alfabeto."""
    return c if c in ALFABETO else OTRO


def todos_excepto(*excluidos: str) -> Set[str]:
    return ALFABETO - set(excluidos)


# ---------------------------------------------------------------------------
# Clase AFD
# ---------------------------------------------------------------------------
@dataclass
class AFD:
    nombre: str
    estados: Set[str]
    transiciones: Dict[Tuple[str, str], str]  # (estado, símbolo) -> estado
    inicial: str
    aceptacion: Dict[str, str]  # estado de aceptación -> token reconocido

    def mover(self, estado: str, sim: str) -> Optional[str]:
        """Una transición. Devuelve None si no existe (estado de error)."""
        return self.transiciones.get((estado, sim))

    def acepta(self, cadena: str) -> Optional[str]:
        """Procesa la cadena completa. Devuelve el token si termina en aceptación."""
        estado = self.inicial
        for c in cadena:
            estado = self.mover(estado, simbolo(c))
            if estado is None:
                return None
        return self.aceptacion.get(estado)

    def reconocer(self, texto: str, inicio: int = 0) -> Tuple[Optional[str], str]:
        """
        Máxima coincidencia: avanza mientras haya transición y recuerda el
        ÚLTIMO estado de aceptación visitado. Devuelve (token, lexema).
        """
        estado = self.inicial
        ultimo_token, fin = None, inicio
        i = inicio
        while i < len(texto):
            estado = self.mover(estado, simbolo(texto[i]))
            if estado is None:
                break
            i += 1
            if estado in self.aceptacion:
                ultimo_token, fin = self.aceptacion[estado], i
        return ultimo_token, texto[inicio:fin]

    def traza(self, cadena: str) -> List[Tuple[str, str, Optional[str]]]:
        """Lista de pasos (estado, carácter, siguiente) para mostrar en el informe."""
        pasos, estado = [], self.inicial
        for c in cadena:
            siguiente = self.mover(estado, simbolo(c))
            pasos.append((estado, c, siguiente))
            if siguiente is None:
                break
            estado = siguiente
        return pasos


class _Constructor:
    """Ayuda a escribir los AFD de forma corta: t('q0', letras, 'q1')."""

    def __init__(self):
        self.transiciones: Dict[Tuple[str, str], str] = {}
        self.estados: Set[str] = set()

    def t(self, origen: str, simbolos: Iterable[str], destino: str):
        self.estados |= {origen, destino}
        for s in simbolos:
            self.transiciones[(origen, s)] = destino

    def afd(self, nombre: str, inicial: str, aceptacion: Dict[str, str]) -> AFD:
        return AFD(nombre, self.estados | {inicial}, self.transiciones, inicial, aceptacion)


# ---------------------------------------------------------------------------
# AFD de cada categoría
# ---------------------------------------------------------------------------
def afd_atomo() -> AFD:
    # ER: [a-z][a-zA-Z0-9_]*
    c = _Constructor()
    c.t("q0", MINUSCULAS, "q1")
    c.t("q1", LETRA_DIGITO, "q1")
    return c.afd("ATOMO", "q0", {"q1": "ATOMO"})


def afd_variable() -> AFD:
    # ER: _  |  _[a-zA-Z0-9_]+  |  [A-Z][a-zA-Z0-9_]*
    c = _Constructor()
    c.t("q0", {"_"}, "q1")          # q1: leyó solo "_"
    c.t("q0", MAYUSCULAS, "q2")
    c.t("q1", LETRA_DIGITO, "q2")
    c.t("q2", LETRA_DIGITO, "q2")
    return c.afd("VARIABLE", "q0", {"q1": "VARIABLE_ANONIMA", "q2": "VARIABLE"})


def afd_numero() -> AFD:
    # ER: [0-9]+  |  [0-9]+\.[0-9]+([eE][+-]?[0-9]+)?
    c = _Constructor()
    c.t("q0", DIGITOS, "q1")        # parte entera
    c.t("q1", DIGITOS, "q1")
    c.t("q1", {"."}, "q2")          # punto: aún no es real
    c.t("q2", DIGITOS, "q3")        # parte decimal
    c.t("q3", DIGITOS, "q3")
    c.t("q3", {"e", "E"}, "q4")     # exponente
    c.t("q4", {"+", "-"}, "q5")
    c.t("q4", DIGITOS, "q6")
    c.t("q5", DIGITOS, "q6")
    c.t("q6", DIGITOS, "q6")
    return c.afd("NUMERO", "q0", {"q1": "ENTERO", "q3": "REAL", "q6": "REAL"})


def _afd_entre_comillas(comilla: str, token: str) -> AFD:
    # ER: C([^C\\\n] | \\[ntr\\'"] | CC)*C     (C = la comilla)
    c = _Constructor()
    c.t("q0", {comilla}, "q1")
    c.t("q1", todos_excepto(comilla, "\\", "\n"), "q1")
    c.t("q1", {"\\"}, "q2")         # inicio de secuencia de escape
    c.t("q2", ESCAPES, "q1")
    c.t("q1", {comilla}, "q3")      # comilla de cierre
    c.t("q3", {comilla}, "q1")      # comilla doble ('') = comilla dentro del texto
    return c.afd(token, "q0", {"q3": token})


def afd_atomo_comillas() -> AFD:
    return _afd_entre_comillas("'", "ATOMO_COMILLAS")


def afd_cadena() -> AFD:
    return _afd_entre_comillas('"', "CADENA")


def afd_comentario_linea() -> AFD:
    # ER: %[^\n]*
    c = _Constructor()
    c.t("q0", {"%"}, "q1")
    c.t("q1", todos_excepto("\n"), "q1")
    return c.afd("COMENTARIO_LINEA", "q0", {"q1": "COMENTARIO_LINEA"})


def afd_comentario_bloque() -> AFD:
    # ER: /\*[^*]*\*+([^*/][^*]*\*+)*/
    c = _Constructor()
    c.t("q0", {"/"}, "q1")
    c.t("q1", {"*"}, "q2")          # dentro del comentario
    c.t("q2", todos_excepto("*"), "q2")
    c.t("q2", {"*"}, "q3")          # vio '*', puede venir el cierre
    c.t("q3", {"*"}, "q3")
    c.t("q3", todos_excepto("*", "/"), "q2")
    c.t("q3", {"/"}, "q4")          # cierre */
    return c.afd("COMENTARIO_BLOQUE", "q0", {"q4": "COMENTARIO_BLOQUE"})


def afd_espacio() -> AFD:
    # ER: [ \t\r\n]+
    c = _Constructor()
    c.t("q0", {" ", "\t", "\r", "\n"}, "q1")
    c.t("q1", {" ", "\t", "\r", "\n"}, "q1")
    return c.afd("ESPACIO", "q0", {"q1": "ESPACIO"})


def afd_literal(lexema: str, token: str) -> AFD:
    """AFD en cadena para un lexema fijo (operadores, delimitadores, is, mod)."""
    c = _Constructor()
    for i, car in enumerate(lexema):
        c.t(f"q{i}", {car}, f"q{i + 1}")
    return c.afd(token, "q0", {f"q{len(lexema)}": token})


def afd_operadores() -> AFD:
    """Todos los operadores y delimitadores juntos (unión de los literales)."""
    return unir([afd_literal(lex, tok) for lex, tok in OPERADORES.items()], "OPERADORES")


# ---------------------------------------------------------------------------
# Unión de AFD por construcción del producto
# ---------------------------------------------------------------------------
def unir(afds: List[AFD], nombre: str = "INTEGRADO") -> AFD:
    """
    Construye un AFD que simula todos los AFD de la lista en paralelo.
    Estado = tupla (estado de AFD 1, estado de AFD 2, ...), con None si ese
    AFD ya murió. Solo se generan los estados alcanzables (recorrido BFS).
    El orden de la lista es la prioridad para elegir el token.
    """
    inicio = tuple(a.inicial for a in afds)
    nombres = {inicio: "q0"}
    pendientes = deque([inicio])
    transiciones: Dict[Tuple[str, str], str] = {}
    aceptacion: Dict[str, str] = {}
    alfabeto = sorted(ALFABETO)

    while pendientes:
        actual = pendientes.popleft()
        nombre_actual = nombres[actual]

        # ¿Acepta algún componente? Gana el de mayor prioridad (el primero).
        for a, q in zip(afds, actual):
            if q is not None and q in a.aceptacion:
                aceptacion[nombre_actual] = a.aceptacion[q]
                break

        for s in alfabeto:
            siguiente = tuple(
                a.mover(q, s) if q is not None else None for a, q in zip(afds, actual)
            )
            if all(q is None for q in siguiente):
                continue  # todos murieron: estado de error implícito
            if siguiente not in nombres:
                nombres[siguiente] = f"q{len(nombres)}"
                pendientes.append(siguiente)
            transiciones[(nombre_actual, s)] = nombres[siguiente]

    return AFD(nombre, set(nombres.values()), transiciones, "q0", aceptacion)


def afds_por_categoria() -> List[AFD]:
    """AFD de cada categoría, en orden de PRIORIDAD (igual que en el punto 2)."""
    return [
        *[afd_literal(lex, tok) for lex, tok in PALABRAS_RESERVADAS.items()],
        afd_atomo(),
        afd_atomo_comillas(),
        afd_variable(),
        afd_numero(),
        afd_cadena(),
        afd_comentario_linea(),
        afd_comentario_bloque(),
        afd_espacio(),
        afd_operadores(),
    ]


def afd_integrado() -> AFD:
    return unir(afds_por_categoria(), "INTEGRADO")
