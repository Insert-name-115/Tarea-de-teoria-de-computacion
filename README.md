# Analizador léxico de Prolog — INFO1148 Teoría de la Computación

Analizador léxico para un subconjunto de Prolog, implementado en Python 3.

## Avance

| Punto | Contenido | Estado | Archivo |
|---|---|---|---|
| 1 | Especificación del subconjunto (tokens, ejemplos, atributos) | ✅ | `prolog_lexer/especificacion.py` |
| 2 | Expresiones regulares, máxima coincidencia y prioridad | ✅ | `prolog_lexer/expresiones_regulares.py` |
| 3 | AFD por categoría y AFD integrado | ✅ | `prolog_lexer/automatas.py` |
| 4 | Determinización (AFN→AFD) y minimización | ⏳ | |
| 5–7 | Lexer completo, tabla de lexemas, errores léxicos | ⏳ | |
| 8 | Corpus de pruebas | ⏳ (pruebas de coherencia de los puntos 1–3 listas) | `tests/` |

## Estructura

```
prolog_lexer/
  especificacion.py         Punto 1: catálogo de tokens y convenciones
  expresiones_regulares.py  Punto 2: una ER por token + máxima coincidencia y prioridad
  automatas.py              Punto 3: clase AFD, AFD de cada categoría y AFD integrado
  visualizar.py             Diagramas Graphviz (.dot/.png) y tablas de transición
demo.py                     Ejecuta y muestra los puntos 1–3
ejemplos/                   Programas Prolog de entrada
docs/                       Tabla de tokens y diagramas generados
tests/                      Pruebas automáticas (pytest)
```

## Requisitos

- Python 3.10 o superior
- `pytest` (solo para las pruebas): `pip install -r requirements.txt`
- Opcional: [Graphviz](https://graphviz.org/download/) para generar los PNG de los
  autómatas (en Windows: `winget install graphviz`). Sin Graphviz se generan los
  `.dot`, que se pueden ver en https://dreampuf.github.io/GraphvizOnline

## Ejecución

```bash
python demo.py                        # usa ejemplos/ejemplo_enunciado.pl
python demo.py ruta/a/programa.pl     # otro archivo
python -m pytest                      # pruebas
```

`demo.py` muestra la especificación, los casos de prioridad, las tablas de
transición de cada AFD y una vista previa de los tokens que reconoce el AFD
integrado. También regenera `docs/especificacion_tokens.md` y `docs/automatas/`.

## Decisiones de diseño (resumen)

- **Números sin signo:** `-5` → `OP_RESTA` + `ENTERO`.
- **Reales:** requieren parte decimal (`3.14`, `1.5e10`); `3.` se lee `ENTERO` + `PUNTO`.
- **Máxima coincidencia:** `\==` antes que `\=`, `=..` antes que `=`, `:-` antes que `:`,
  `_X` (VARIABLE) antes que `_` (VARIABLE_ANONIMA).
- **Prioridad:** ante empate de largo, `is`/`mod` son `OP_IS`/`OP_MOD` y no `ATOMO`.
- **AFD integrado:** construcción del producto (unión) de los AFD de cada categoría;
  si varios aceptan en el mismo estado gana el de mayor prioridad.
- Las pruebas verifican que las ER y los AFD reconocen exactamente lo mismo.
