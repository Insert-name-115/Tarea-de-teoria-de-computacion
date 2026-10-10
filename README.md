# Analizador léxico de Prolog — INFO1148 Teoría de la Computación

Puntos 1, 2 y 3 de la tarea, en Python.

| Archivo | Contenido |
|---|---|
| `punto1_especificacion.py` | Tokens: patrón, ejemplos válidos/inválidos y atributo |
| `punto2_expresiones.py` | Una expresión regular por token, máxima coincidencia y prioridad |
| `punto3_automatas.py` | AFD de cada categoría, AFD integrado y dibujo con Graphviz |
| `main.py` | Ejecuta los tres puntos y guarda los diagramas en `automatas/` |

## Ejecución

```bash
pip install -r requirements.txt
python main.py
```

Los diagramas se guardan como `.dot` en `automatas/` (y como `.png` si está
instalado [Graphviz](https://graphviz.org/download/)). Los `.dot` se pueden ver en
https://dreampuf.github.io/GraphvizOnline
