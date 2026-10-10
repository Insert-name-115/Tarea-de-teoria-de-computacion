# Especificación de tokens

Generado por `python demo.py`. En los ejemplos, ⏎ es un salto de línea real y ⇥ una tabulación real.

| Token | Descripción | Expresión regular | Ejemplos válidos | Ejemplos inválidos | Atributo |
|---|---|---|---|---|---|
| ATOMO | Letra minúscula seguida de letras, dígitos o guion bajo. | `[a-z][a-zA-Z0-9_]*` | `padre`, `persona_1`, `x`, `juanPerez` | `Padre`, `1abc`, `_x`, `per-sona` | Índice en la tabla de lexemas |
| ATOMO_COMILLAS | Texto entre comillas simples; admite espacios, símbolos, escapes y ''. | `'(?:[^'\\\n]\|\\[^\n]\|'')*'` | `'Juan Pérez'`, `':-'`, `'it''s'`, `'a\nb'`, `''` | `'sin cierre`, `'a⏎b'`, `'x'y'` | Índice en la tabla de lexemas |
| VARIABLE | Letra mayúscula, o guion bajo seguido de al menos un carácter; luego letras, dígitos o guion bajo. | `_[a-zA-Z0-9_]+\|[A-Z][a-zA-Z0-9_]*` | `X`, `Persona`, `_Temporal`, `_x1`, `Lista_2` | `persona`, `1X`, `_` | Índice en la tabla de lexemas |
| VARIABLE_ANONIMA | El guion bajo solo. | `_` | `_` | `__`, `_X` | - |
| ENTERO | Uno o más dígitos, sin signo. | `[0-9]+` | `0`, `25`, `007` | `-5`, `2a`, `3.14` | Valor numérico (int) |
| REAL | Dígitos, un punto y dígitos. | `[0-9]+\.[0-9]+` | `3.14`, `0.5`, `10.0` | `3.`, `.5`, `1.5e10`, `1.2.3` | Valor numérico (float) |
| CADENA | Texto entre comillas dobles; admite escapes y "". | `"(?:[^"\\\n]\|\\[^\n]\|"")*"` | `"hola"`, `"Hola mundo"`, `"dice \"si\""`, `""` | `"sin cierre`, `"a⏎b"` | Índice en la tabla de lexemas |
| COMENTARIO_LINEA | Desde % hasta el final de la línea (se ignora). | `%[^\n]*` | `% Hechos`, `%`, `%% doble` | `Hechos %` | - |
| COMENTARIO_BLOQUE | Desde /* hasta el primer */ (no anidado; se ignora). | `/\*[^*]*\*+(?:[^*/][^*]*\*+)*/` | `/* hola */`, `/**/`, `/* a⏎b */`, `/* ** */` | `/* sin cierre`, `/* a */ b */` | - |
| ESPACIO | Uno o más espacios, tabulaciones o saltos de línea (se ignora). | `[ \t\r\n]+` | ` `, `⇥`, `⏎`, `  ⏎⇥ ` | `x ` | - |
| OP_IS | Átomo operador 'is' (palabra reservada). | `is` | `is` | `IS`, `isx` | - |
| OP_MOD | Átomo operador 'mod' (palabra reservada). | `mod` | `mod` | `MOD`, `modx` | - |
| OP_REGLA | Literal :- | `:\-` | `:-` | `:` | - |
| OP_CONSULTA | Literal ?- | `\?\-` | `?-` | `?` | - |
| OP_DCG | Literal --> | `\-\->` | `-->` | `--` | - |
| OP_UNIFICA | Literal = | `=` | `=` | - | - |
| OP_NO_UNIFICA | Literal \= | `\\=` | `\=` | `\` | - |
| OP_IDENTICO | Literal == | `==` | `==` | - | - |
| OP_NO_IDENTICO | Literal \== | `\\==` | `\==` | - | - |
| OP_UNIV | Literal =.. | `=\.\.` | `=..` | `=.` | - |
| OP_MENOR | Literal < | `<` | `<` | - | - |
| OP_MENOR_IGUAL | Literal =< | `=<` | `=<` | - | - |
| OP_MAYOR | Literal > | `>` | `>` | - | - |
| OP_MAYOR_IGUAL | Literal >= | `>=` | `>=` | - | - |
| OP_SUMA | Literal + | `\+` | `+` | - | - |
| OP_RESTA | Literal - | `\-` | `-` | - | - |
| OP_MULT | Literal * | `\*` | `*` | - | - |
| OP_DIV | Literal / | `/` | `/` | - | - |
| OP_DIV_ENTERA | Literal // | `//` | `//` | - | - |
| OP_POTENCIA | Literal ** | `\*\*` | `**` | - | - |
| OP_NEGACION | Literal \+ | `\\\+` | `\+` | - | - |
| CORTE | Literal ! | `!` | `!` | - | - |
| PUNTO_Y_COMA | Literal ; | `;` | `;` | - | - |
| COMA | Literal , | `,` | `,` | - | - |
| PARENTESIS_IZQ | Literal ( | `\(` | `(` | - | - |
| PARENTESIS_DER | Literal ) | `\)` | `)` | - | - |
| CORCHETE_IZQ | Literal [ | `\[` | `[` | - | - |
| CORCHETE_DER | Literal ] | `\]` | `]` | - | - |
| LLAVE_IZQ | Literal { | `\{` | `{` | - | - |
| LLAVE_DER | Literal } | `\}` | `}` | - | - |
| BARRA | Literal \| | `\\|` | `\|` | - | - |
| PUNTO | Literal . | `\.` | `.` | - | - |
