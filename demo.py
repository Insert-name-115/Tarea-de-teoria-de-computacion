# -------------------------------------------------------------------
# Demostración de los puntos 1, 2 y 3 de la tarea
# -------------------------------------------------------------------
# Uso:
#   python demo.py                   -> usa ejemplos/ejemplo_enunciado.pl
#   python demo.py archivo.pl        -> usa otro archivo
#   python demo.py --interactivo     -> probar lexemas a mano
#
# Genera además:
#   docs/especificacion_tokens.md    (tabla del punto 1 con las ER del punto 2)
#   docs/automatas/*.dot (y .png)    (diagramas del punto 3)
# -------------------------------------------------------------------

import sys
from pathlib import Path

from prolog_lexer import automatas
from prolog_lexer.automatas import afd_integrado, reconocer_token
from prolog_lexer.especificacion import CATEGORIAS, TOKENS_IGNORADOS, tabla_markdown
from prolog_lexer.expresiones_regulares import clasificar, coincidencia_mas_larga
from prolog_lexer.visualizar import guardar_afd, tabla_pasos, tabla_transiciones

RAIZ = Path(__file__).parent
CARPETA_AUTOMATAS = RAIZ / "docs" / "automatas"


def titulo(texto: str):
    print("\n" + "=" * 70 + f"\n{texto}\n" + "=" * 70)


# -------------------------------------------------------------------
# Punto 1: mostrar la especificación y guardarla en Markdown
# -------------------------------------------------------------------
def punto_1():
    titulo("PUNTO 1 - Especificación de tokens")
    for c in CATEGORIAS[:12]:  # las 12 primeras; el resto son operadores
        print(f"  {c.token:<18} {c.descripcion}")
    print(f"  ... y {len(CATEGORIAS) - 12} operadores/delimitadores (lexemas fijos).")

    ruta = RAIZ / "docs" / "especificacion_tokens.md"
    ruta.parent.mkdir(exist_ok=True)
    encabezado = ("# Especificación de tokens\n\n"
                  "Generado por `python demo.py`. En los ejemplos, ⏎ es un salto de "
                  "línea real y ⇥ una tabulación real.\n\n")
    ruta.write_text(encabezado + tabla_markdown() + "\n", encoding="utf-8")
    print(f"\nTabla completa guardada en {ruta.relative_to(RAIZ)}")


# -------------------------------------------------------------------
# Punto 2: superposiciones entre ER y cómo se resuelven
# -------------------------------------------------------------------
def punto_2():
    titulo("PUNTO 2 - Expresiones regulares: prioridad y máxima coincidencia")
    print("Lexema completo -> token elegido   (todas las ER que calzan)")
    for lexema in ["is", "isa", "mod", "_", "_X", "padre", "Padre"]:
        elegido, todos = clasificar(lexema)
        print(f"  {lexema!r:<9} -> {elegido:<17} {todos}")

    print("\nTexto -> (token, lexema) por máxima coincidencia")
    for texto in ["\\== b", "\\= b", "=.. L", ":- p", "3.14.", "3.x", "/* c */ x", "//2", "-->"]:
        print(f"  {texto!r:<12} -> {coincidencia_mas_larga(texto)}")


# -------------------------------------------------------------------
# Punto 3: AFD de cada categoría, AFD integrado y una simulación
# -------------------------------------------------------------------
def punto_3():
    titulo("PUNTO 3 - Autómatas finitos deterministas")
    for afd in automatas.AFDS_POR_CATEGORIA:
        print("\n" + tabla_transiciones(afd))
        guardar_afd(afd, CARPETA_AUTOMATAS)
        print(f"AFD {afd.nombre} creado correctamente.")

    guardar_afd(afd_integrado, CARPETA_AUTOMATAS)
    print(f"\nAFD INTEGRADO: {len(afd_integrado.estados)} estados, "
          f"{len(afd_integrado.estados_aceptacion)} de aceptación, "
          f"{len(afd_integrado.transiciones)} transiciones.")
    print(f"Diagramas guardados en {CARPETA_AUTOMATAS.relative_to(RAIZ)}")

    # Ejemplo de simulación (como en el Laboratorio 1)
    cadena = "persona_1"
    final, log = automatas.afd_atomo.simular(cadena)
    print(f"\nSimulación del AFD ATOMO con {cadena!r}:")
    print(tabla_pasos(log))
    print(f"Estado final: {final} | ¿Acepta? {automatas.afd_atomo.acepta(cadena)}")
    guardar_afd(automatas.afd_atomo, CARPETA_AUTOMATAS / "simulaciones", log)


# -------------------------------------------------------------------
# Vista previa: recorrer un archivo con el AFD integrado
# (el lexer completo con tabla de lexemas y errores es de los puntos 5-7)
# -------------------------------------------------------------------
def vista_previa(ruta: Path):
    titulo(f"Vista previa: AFD integrado sobre {ruta.name}")
    texto = ruta.read_text(encoding="utf-8")
    pos, linea, columna = 0, 1, 1

    while pos < len(texto):
        token, lexema = reconocer_token(texto, pos)
        # Coherencia: la ER del punto 2 tiene que dar lo mismo que el AFD
        assert (token, lexema) == coincidencia_mas_larga(texto, pos), "ER y AFD no coinciden"

        if token is None:
            print(f"  [no reconocido] {texto[pos]!r} en línea {linea}, columna {columna}")
            lexema = texto[pos]
        elif token not in TOKENS_IGNORADOS:
            print(f"  <{token}, '{lexema}', {linea}, {columna}>")

        # Actualizar línea y columna
        for c in lexema:
            if c == "\n":
                linea, columna = linea + 1, 1
            else:
                columna += 1
        pos += len(lexema)


# -------------------------------------------------------------------
# Modo interactivo (parecido al widget del Laboratorio 1)
# -------------------------------------------------------------------
def modo_interactivo():
    titulo("Modo interactivo")
    print("Escribe un lexema para simularlo en el AFD integrado (enter vacío para salir).")
    print("Ejemplos: padre   _X   3.14   'Juan Pérez'   \\==   /* hola */")
    while True:
        cadena = input("\nLexema: ")
        if not cadena:
            break
        final, log = afd_integrado.simular(cadena)
        print(tabla_pasos(log))
        token, reconocido = reconocer_token(cadena)
        print(f"Estado final: {final} | Token: {token if reconocido == cadena else None}")
        if reconocido != cadena:
            print(f"(Por máxima coincidencia solo se reconoce el prefijo {reconocido!r} como {token})")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--interactivo" in sys.argv:
        modo_interactivo()
    else:
        archivo = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "ejemplos" / "ejemplo_enunciado.pl"
        punto_1()
        punto_2()
        punto_3()
        vista_previa(archivo)
