# -------------------------------------------------------------------
# PUNTO 3: Modelado con autómatas (AFD)
# Comentarios:
# - 'transiciones' mapea (estado, símbolo) -> nuevo_estado.
# - 'aceptacion' mapea estado de aceptación -> token que reconoce.
# - El estado inicial de todos los AFD es "Inicio".
# - El alfabeto son clases de caracteres (minuscula, digito, ...).
# - Si no hay transición, el AFD se detiene (estado de error).
# -------------------------------------------------------------------

from dataclasses import dataclass

import graphviz

from punto1_especificacion import PALABRAS_RESERVADAS

ESPECIALES = {"_": "guion_bajo", " ": "espacio", "\t": "espacio", "\r": "espacio", "\n": "salto",
              "'": "comilla_simple", '"': "comilla_doble", "\\": "barra_inv", "%": "porcentaje"}
SIMBOLOS = set(":?->=.<+*/!;,()[]{}|")
ALFABETO = {"minuscula", "mayuscula", "digito", "otro"} | set(ESPECIALES.values()) | SIMBOLOS
LETRA_DIGITO = ["minuscula", "mayuscula", "digito", "guion_bajo"]


def clase_de(c):
    """Traduce un carácter a su símbolo del alfabeto."""
    if "a" <= c <= "z":
        return "minuscula"
    if "A" <= c <= "Z":
        return "mayuscula"
    if "0" <= c <= "9":
        return "digito"
    if c in ESPECIALES:
        return ESPECIALES[c]
    return c if c in SIMBOLOS else "otro"  # otro = @, #, é, ñ, ...


def todos_menos(*simbolos):
    return ALFABETO - set(simbolos)


@dataclass
class AFD:
    nombre: str
    transiciones: dict
    aceptacion: dict
    inicial: str = "Inicio"

    def simular(self, cadena):
        """Recorre la cadena. Devuelve (estado_final, log)."""
        actual, log = self.inicial, []
        for i, c in enumerate(cadena):
            nuevo = self.transiciones.get((actual, clase_de(c)))
            log.append((i, actual, c, nuevo))
            if nuevo is None:
                return None, log
            actual = nuevo
        return actual, log

    def reconocer(self, texto, inicio=0):
        """Máxima coincidencia: guarda el último estado de aceptación visto."""
        actual, token, fin = self.inicial, None, inicio
        for i in range(inicio, len(texto)):
            actual = self.transiciones.get((actual, clase_de(texto[i])))
            if actual is None:
                break
            if actual in self.aceptacion:
                token, fin = self.aceptacion[actual], i + 1
        lexema = texto[inicio:fin]
        # Palabras reservadas: se reconocen como ATOMO y luego se buscan en la tabla
        if token == "ATOMO" and lexema in PALABRAS_RESERVADAS:
            token = PALABRAS_RESERVADAS[lexema]
        return token, lexema


# AFD ATOMO:  Inicio --minuscula--> Atomo --letra|digito|_--> Atomo
afd_atomo = AFD("ATOMO", {
    ("Inicio", "minuscula"): "Atomo",
    **{("Atomo", s): "Atomo" for s in LETRA_DIGITO},
}, {"Atomo": "ATOMO"})

# AFD VARIABLE:  Inicio --_--> Anonima --letra|digito|_--> Variable;  Inicio --mayuscula--> Variable
afd_variable = AFD("VARIABLE", {
    ("Inicio", "guion_bajo"): "Anonima",
    ("Inicio", "mayuscula"): "Variable",
    **{("Anonima", s): "Variable" for s in LETRA_DIGITO},
    **{("Variable", s): "Variable" for s in LETRA_DIGITO},
}, {"Anonima": "VARIABLE_ANONIMA", "Variable": "VARIABLE"})

# AFD NUMERO:  Inicio --digito--> Entero --.--> EnteroPunto --digito--> Real
afd_numero = AFD("NUMERO", {
    ("Inicio", "digito"): "Entero",
    ("Entero", "digito"): "Entero",
    ("Entero", "."): "EnteroPunto",
    ("EnteroPunto", "digito"): "Real",
    ("Real", "digito"): "Real",
}, {"Entero": "ENTERO", "Real": "REAL"})


# AFD con comillas (sirve para ATOMO_COMILLAS y CADENA):
#   Inicio --C--> Abierto --C--> Cerrado (acepta) --C--> Abierto ('' dentro del texto)
#   Abierto --\--> Escape --cualquiera--> Abierto
def afd_comillas(nombre, comilla, p):
    return AFD(nombre, {
        ("Inicio", comilla): p + "Abierto",
        **{(p + "Abierto", s): p + "Abierto" for s in todos_menos(comilla, "barra_inv", "salto")},
        (p + "Abierto", "barra_inv"): p + "Escape",
        **{(p + "Escape", s): p + "Abierto" for s in todos_menos("salto")},
        (p + "Abierto", comilla): p + "Cerrado",
        (p + "Cerrado", comilla): p + "Abierto",
    }, {p + "Cerrado": nombre})


afd_atomo_comillas = afd_comillas("ATOMO_COMILLAS", "comilla_simple", "AC_")
afd_cadena = afd_comillas("CADENA", "comilla_doble", "CAD_")

# AFD COMENTARIO_LINEA:  Inicio --%--> ComLinea --todo menos salto--> ComLinea
afd_comentario_linea = AFD("COMENTARIO_LINEA", {
    ("Inicio", "porcentaje"): "ComLinea",
    **{("ComLinea", s): "ComLinea" for s in todos_menos("salto")},
}, {"ComLinea": "COMENTARIO_LINEA"})

# AFD COMENTARIO_BLOQUE:  Inicio --/--> Barra --*--> Dentro --*--> Asterisco --/--> Cerrado
# (el estado "Barra" lo comparte con el AFD de operadores, donde acepta OP_DIV)
afd_comentario_bloque = AFD("COMENTARIO_BLOQUE", {
    ("Inicio", "/"): "Barra",
    ("Barra", "*"): "CB_Dentro",
    **{("CB_Dentro", s): "CB_Dentro" for s in todos_menos("*")},
    ("CB_Dentro", "*"): "CB_Asterisco",
    ("CB_Asterisco", "*"): "CB_Asterisco",
    **{("CB_Asterisco", s): "CB_Dentro" for s in todos_menos("*", "/")},
    ("CB_Asterisco", "/"): "CB_Cerrado",
}, {"CB_Cerrado": "COMENTARIO_BLOQUE"})

# AFD ESPACIO:  Inicio --espacio|salto--> Espacio --espacio|salto--> Espacio
afd_espacio = AFD("ESPACIO", {
    ("Inicio", "espacio"): "Espacio", ("Inicio", "salto"): "Espacio",
    ("Espacio", "espacio"): "Espacio", ("Espacio", "salto"): "Espacio",
}, {"Espacio": "ESPACIO"})

# AFD OPERADORES: árbol de prefijos. Cada estado es lo leído hasta ahora.
# No aceptan: DosPuntos (:), Interrogacion (?), MenosMenos (--), IgualPunto (=.), BarraInv (\)
# Los demás estados aceptan el token con su mismo nombre ("Barra" acepta OP_DIV).
transiciones_operadores = {
    ("Inicio", ":"): "DosPuntos", ("DosPuntos", "-"): "OP_REGLA",
    ("Inicio", "?"): "Interrogacion", ("Interrogacion", "-"): "OP_CONSULTA",
    ("Inicio", "-"): "OP_RESTA", ("OP_RESTA", "-"): "MenosMenos", ("MenosMenos", ">"): "OP_DCG",
    ("Inicio", "="): "OP_UNIFICA", ("OP_UNIFICA", "="): "OP_IDENTICO", ("OP_UNIFICA", "<"): "OP_MENOR_IGUAL",
    ("OP_UNIFICA", "."): "IgualPunto", ("IgualPunto", "."): "OP_UNIV",
    ("Inicio", "barra_inv"): "BarraInv", ("BarraInv", "="): "OP_NO_UNIFICA",
    ("OP_NO_UNIFICA", "="): "OP_NO_IDENTICO", ("BarraInv", "+"): "OP_NEGACION",
    ("Inicio", "<"): "OP_MENOR", ("Inicio", ">"): "OP_MAYOR", ("OP_MAYOR", "="): "OP_MAYOR_IGUAL",
    ("Inicio", "+"): "OP_SUMA", ("Inicio", "*"): "OP_MULT", ("OP_MULT", "*"): "OP_POTENCIA",
    ("Inicio", "/"): "Barra", ("Barra", "/"): "OP_DIV_ENTERA",
    ("Inicio", "!"): "CORTE", ("Inicio", ";"): "PUNTO_Y_COMA", ("Inicio", ","): "COMA",
    ("Inicio", "("): "PARENTESIS_IZQ", ("Inicio", ")"): "PARENTESIS_DER",
    ("Inicio", "["): "CORCHETE_IZQ", ("Inicio", "]"): "CORCHETE_DER",
    ("Inicio", "{"): "LLAVE_IZQ", ("Inicio", "}"): "LLAVE_DER",
    ("Inicio", "|"): "BARRA", ("Inicio", "."): "PUNTO",
}
NO_ACEPTAN = {"DosPuntos", "Interrogacion", "MenosMenos", "IgualPunto", "BarraInv"}
afd_operadores = AFD("OPERADORES", transiciones_operadores, {
    **{e: e for e in transiciones_operadores.values() if e not in NO_ACEPTAN},
    "Barra": "OP_DIV",
})

AFDS = [afd_atomo, afd_variable, afd_numero, afd_atomo_comillas, afd_cadena,
        afd_comentario_linea, afd_comentario_bloque, afd_espacio, afd_operadores]

# AFD INTEGRADO: todos comparten el estado "Inicio" y salen de él con símbolos
# distintos (salvo '/', que lleva al estado compartido "Barra"), así que basta
# con juntar sus tablas para obtener un solo AFD.
afd_integrado = AFD("INTEGRADO", {}, {})
for afd in AFDS:
    for clave, destino in afd.transiciones.items():
        assert afd_integrado.transiciones.get(clave, destino) == destino, f"Conflicto en {clave}"
        afd_integrado.transiciones[clave] = destino
    afd_integrado.aceptacion.update(afd.aceptacion)


# -------------------------------------------------------------------
# Funciones para visualizar y mostrar pasos
# - 'dibujar_afd' dibuja el grafo del AFD con Graphviz.
# - 'tabla_pasos' muestra las transiciones tomadas en una simulación.
# -------------------------------------------------------------------
def dibujar_afd(afd, log=None):
    dot = graphviz.Digraph(afd.nombre, format="png")
    dot.attr(rankdir="LR")
    dot.node("", shape="point")  # nodo invisible para flecha inicial

    # Dibujar estados (doble círculo si es de aceptación)
    estados = {afd.inicial} | {e for e, _ in afd.transiciones} | set(afd.transiciones.values())
    for s in estados:
        if s in afd.aceptacion:
            dot.node(s, f"{s}\\n[{afd.aceptacion[s]}]", shape="doublecircle")
        else:
            dot.node(s, shape="circle")

    # Flecha al estado inicial
    dot.edge("", afd.inicial)

    # Agrupar símbolos por (origen, destino)
    etiquetas = {}
    for (src, sym), dst in afd.transiciones.items():
        etiquetas.setdefault((src, dst), []).append(sym)

    recorridos = {(src, dst) for (_, src, _, dst) in (log or [])}

    for (src, dst), syms in etiquetas.items():
        # Si son casi todos los símbolos, se escribe "todo menos ..." para acortar
        if len(syms) > 8:
            label = "todo menos " + ", ".join(sorted(ALFABETO - set(syms)))
        else:
            label = ", ".join(sorted(syms))
        if (src, dst) in recorridos:
            dot.edge(src, dst, label=label, color="blue", penwidth="2")
        else:
            dot.edge(src, dst, label=label)

    return dot


def tabla_pasos(log):
    if not log:
        print("No hubo transiciones.")
        return
    print(f"{'#':<3} {'Estado actual':<15} {'Entrada':<9} Nuevo estado")
    for i, s, c, nuevo in log:
        print(f"{i:<3} {s:<15} {c!r:<9} {nuevo or 'ERROR'}")
