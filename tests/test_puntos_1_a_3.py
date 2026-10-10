"""
Pruebas de coherencia entre los puntos 1, 2 y 3:
especificación (ejemplos)  <->  expresiones regulares  <->  autómatas.

Ejecutar con:  python -m pytest
"""

import pytest

from prolog_lexer import automatas as A
from prolog_lexer.especificacion import CATEGORIAS
from prolog_lexer.expresiones_regulares import EXPRESIONES, calza_completo, coincidencia_mas_larga

INTEGRADO = A.afd_integrado()


def test_cada_categoria_tiene_expresion_regular():
    assert {c.token for c in CATEGORIAS} == set(EXPRESIONES)


@pytest.mark.parametrize("cat", CATEGORIAS, ids=lambda c: c.token)
def test_ejemplos_validos(cat):
    for lexema in cat.validos:
        assert calza_completo(cat.token, lexema), f"ER rechaza {lexema!r}"
        assert INTEGRADO.acepta(lexema) == cat.token, f"AFD no da {cat.token} para {lexema!r}"


@pytest.mark.parametrize("cat", CATEGORIAS, ids=lambda c: c.token)
def test_ejemplos_invalidos(cat):
    for lexema in cat.invalidos:
        assert not calza_completo(cat.token, lexema), f"ER acepta {lexema!r}"
        assert INTEGRADO.acepta(lexema) != cat.token, f"AFD acepta {lexema!r}"


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("\\==", ("OP_NO_IDENTICO", "\\==")),
        ("\\=x", ("OP_NO_UNIFICA", "\\=")),
        ("==", ("OP_IDENTICO", "==")),
        ("=..", ("OP_UNIV", "=..")),
        ("=.a", ("OP_UNIFICA", "=")),
        (":-", ("OP_REGLA", ":-")),
        ("_", ("VARIABLE_ANONIMA", "_")),
        ("_Var", ("VARIABLE", "_Var")),
        ("is", ("OP_IS", "is")),
        ("is_", ("ATOMO", "is_")),
        ("modulo", ("ATOMO", "modulo")),
        ("3.14.", ("REAL", "3.14")),
        ("3.", ("ENTERO", "3")),
        ("1.5e", ("REAL", "1.5")),
        ("/*x*/", ("COMENTARIO_BLOQUE", "/*x*/")),
        ("/x", ("OP_DIV", "/")),
        ("-->", ("OP_DCG", "-->")),
        ("--", ("OP_RESTA", "-")),
        ("'Juan Pérez'", ("ATOMO_COMILLAS", "'Juan Pérez'")),
        ("@", (None, "")),
    ],
)
def test_maxima_coincidencia_y_prioridad(texto, esperado):
    assert INTEGRADO.reconocer(texto) == esperado
    assert coincidencia_mas_larga(texto) == esperado


def test_er_y_afd_coinciden_en_un_programa():
    """Desde cada posición del texto, ER y AFD deben elegir el mismo token."""
    texto = (
        "% comentario\nabuelo(X, Z) :- padre(X, Y), padre(Y, Z).\n"
        "suma(A, B, C) :- C is A + B * 2 ** 3 // 4 mod 5.\n"
        "x([H|T], _) :- \\+ H \\== T, !; T =.. L, L =< 3.5e-2.\n"
        "/* bloque\n ** */ s(\"hola \\\"mundo\\\"\", 'it''s'). ?- {a}. a --> b.\n"
    )
    for i in range(len(texto)):
        assert INTEGRADO.reconocer(texto, i) == coincidencia_mas_larga(texto, i), i


def test_afd_integrado_es_determinista_y_completo_en_estados():
    for (origen, _), destino in INTEGRADO.transiciones.items():
        assert origen in INTEGRADO.estados and destino in INTEGRADO.estados
    assert INTEGRADO.inicial == "q0"
    assert set(INTEGRADO.aceptacion) <= INTEGRADO.estados
