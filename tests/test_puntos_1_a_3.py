# -------------------------------------------------------------------
# Pruebas de coherencia entre los puntos 1, 2 y 3
#   especificación (ejemplos)  <->  expresiones regulares  <->  autómatas
#
# Ejecutar con:  python -m pytest
# -------------------------------------------------------------------

import pytest

from prolog_lexer import automatas
from prolog_lexer.automatas import afd_integrado, reconocer_token, token_de_lexema
from prolog_lexer.especificacion import CATEGORIAS
from prolog_lexer.expresiones_regulares import EXPRESIONES, calza_completo, coincidencia_mas_larga


def test_cada_categoria_tiene_expresion_regular():
    assert {c.token for c in CATEGORIAS} == set(EXPRESIONES)


@pytest.mark.parametrize("cat", CATEGORIAS, ids=lambda c: c.token)
def test_ejemplos_validos(cat):
    for lexema in cat.validos:
        assert calza_completo(cat.token, lexema), f"La ER rechaza {lexema!r}"
        assert token_de_lexema(lexema) == cat.token, f"El AFD no da {cat.token} para {lexema!r}"


@pytest.mark.parametrize("cat", CATEGORIAS, ids=lambda c: c.token)
def test_ejemplos_invalidos(cat):
    for lexema in cat.invalidos:
        assert not calza_completo(cat.token, lexema), f"La ER acepta {lexema!r}"
        assert token_de_lexema(lexema) != cat.token, f"El AFD acepta {lexema!r}"


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
        ("/*x*/", ("COMENTARIO_BLOQUE", "/*x*/")),
        ("/x", ("OP_DIV", "/")),
        ("-->", ("OP_DCG", "-->")),
        ("--", ("OP_RESTA", "-")),
        ("'Juan Pérez'", ("ATOMO_COMILLAS", "'Juan Pérez'")),
        ("@", (None, "")),
    ],
)
def test_maxima_coincidencia_y_prioridad(texto, esperado):
    assert reconocer_token(texto) == esperado
    assert coincidencia_mas_larga(texto) == esperado


def test_er_y_afd_coinciden_en_un_programa():
    """Desde cada posición del texto, la ER y el AFD deben elegir lo mismo."""
    texto = (
        "% comentario\nabuelo(X, Z) :- padre(X, Y), padre(Y, Z).\n"
        "suma(A, B, C) :- C is A + B * 2 ** 3 // 4 mod 5.\n"
        "x([H|T], _) :- \\+ H \\== T, !; T =.. L, L =< 3.5, @.\n"
        "/* bloque\n ** */ s(\"hola \\\"mundo\\\"\", 'it''s', 'Pérez'). ?- {a}. a --> b.\n"
    )
    for i in range(len(texto)):
        assert reconocer_token(texto, i) == coincidencia_mas_larga(texto, i), f"posición {i}"


def test_simular_registra_los_pasos():
    final, log = automatas.afd_atomo.simular("ab1")
    assert final == "Atomo"
    assert [paso[1] for paso in log] == ["Inicio", "Atomo", "Atomo"]
    assert automatas.afd_atomo.simular("1ab")[0] is None


def test_afd_integrado_bien_formado():
    for (origen, simbolo), destino in afd_integrado.transiciones.items():
        assert origen in afd_integrado.estados
        assert destino in afd_integrado.estados
        assert simbolo in afd_integrado.alfabeto
    assert set(afd_integrado.estados_aceptacion) <= afd_integrado.estados
