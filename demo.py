"""
Demostración de los puntos 1, 2 y 3 de la tarea.

Uso:
    python demo.py                      # usa ejemplos/ejemplo_enunciado.pl
    python demo.py ruta/archivo.pl      # usa otro archivo

Genera además:
    docs/especificacion_tokens.md       tabla del punto 1 + ER del punto 2
    docs/automatas/*.dot (y .png)       diagramas del punto 3
"""

import sys
from pathlib import Path

from prolog_lexer import automatas as A
from prolog_lexer.especificacion import CATEGORIAS, TOKENS_IGNORADOS, tabla_markdown
from prolog_lexer.expresiones_regulares import clasificar, coincidencia_mas_larga
from prolog_lexer.visualizar import guardar, tabla_transiciones

RAIZ = Path(__file__).parent


def titulo(texto: str):
    print("\n" + "=" * 70 + f"\n{texto}\n" + "=" * 70)


def punto_1():
    titulo("PUNTO 1 - Especificación de tokens")
    for c in CATEGORIAS[:12]:  # categorías principales (el resto son operadores)
        print(f"{c.token:<18} {c.descripcion}")
    print(f"... y {len(CATEGORIAS) - 12} operadores/delimitadores literales.")
    ruta = RAIZ / "docs" / "especificacion_tokens.md"
    encabezado = (
        "# Especificación de tokens\n\n"
        "Generado por `python demo.py`. En los ejemplos, ⏎ es un salto de línea real "
        "y ⇥ una tabulación real.\n\n"
    )
    ruta.write_text(encabezado + tabla_markdown() + "\n", encoding="utf-8")
    print(f"\nTabla completa escrita en {ruta.relative_to(RAIZ)}")


def punto_2():
    titulo("PUNTO 2 - Expresiones regulares: superposiciones y prioridad")
    print("Lexema completo -> token elegido (todos los que calzan)")
    for lexema in ["is", "isa", "mod", "_", "_X", "padre", "Padre"]:
        elegido, todos = clasificar(lexema)
        print(f"  {lexema!r:<10} -> {elegido:<16} {todos}")

    print("\nMáxima coincidencia al inicio del texto -> (token, lexema)")
    for texto in ["\\== b", "\\= b", "=.. L", ":- p", "3.14.", "3.x", "/* c */ x", "//2", "-->"]:
        print(f"  {texto!r:<12} -> {coincidencia_mas_larga(texto)}")


def punto_3():
    titulo("PUNTO 3 - Autómatas finitos deterministas")
    carpeta = RAIZ / "docs" / "automatas"
    principales = [
        A.afd_atomo(), A.afd_variable(), A.afd_numero(), A.afd_atomo_comillas(),
        A.afd_cadena(), A.afd_comentario_linea(), A.afd_comentario_bloque(), A.afd_espacio(),
    ]
    for afd in principales:
        print("\n" + tabla_transiciones(afd))
        guardar(afd, carpeta)

    operadores = A.afd_operadores()
    integrado = A.afd_integrado()
    guardar(operadores, carpeta)
    guardar(integrado, carpeta)
    print(f"\nAFD OPERADORES: {len(operadores.estados)} estados (ver {carpeta.relative_to(RAIZ)}/operadores.dot)")
    print(f"AFD INTEGRADO: {len(integrado.estados)} estados, "
          f"{len(integrado.aceptacion)} de aceptación, {len(integrado.transiciones)} transiciones")

    print("\nTraza del AFD ATOMO con 'persona_1':")
    afd = A.afd_atomo()
    for estado, c, sig in afd.traza("persona_1"):
        print(f"  δ({estado}, {c!r}) = {sig}")
    print(f"  Resultado: {afd.acepta('persona_1')}")


def vista_previa(ruta: Path):
    titulo(f"Vista previa: AFD integrado sobre {ruta.name} (máxima coincidencia)")
    print("(El lexer completo con tabla de lexemas y errores corresponde a los puntos 5-7.)\n")
    texto = ruta.read_text(encoding="utf-8")
    integrado = A.afd_integrado()
    pos, linea, col = 0, 1, 1
    while pos < len(texto):
        token, lexema = integrado.reconocer(texto, pos)
        # Coherencia: las ER del punto 2 deben dar exactamente lo mismo
        assert (token, lexema) == coincidencia_mas_larga(texto, pos), "ER y AFD no coinciden"
        if token is None:
            print(f"  [no reconocido] {texto[pos]!r} en línea {linea}, columna {col}")
            lexema = texto[pos]
        elif token not in TOKENS_IGNORADOS:
            print(f"  <{token}, '{lexema}', {linea}, {col}>")
        for c in lexema:  # actualizar línea y columna
            linea, col = (linea + 1, 1) if c == "\n" else (linea, col + 1)
        pos += len(lexema)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    archivo = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "ejemplos" / "ejemplo_enunciado.pl"
    punto_1()
    punto_2()
    punto_3()
    vista_previa(archivo)
