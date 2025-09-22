# Juan Diego Cadena
# 329220

import os
from openai import OpenAI
from httpx import HTTPError

MODEL = os.getenv("OPENAI_TASK_MODEL", "gpt-5")

SYSTEM_BASE = (
    "Eres un asistente experto en Búsqueda, Heurísticas y Juegos, y Razonamiento Lógico.\n"
    "Responde SIEMPRE en español, con pasos claros, verificables y concisos.\n"
    "PROHIBIDO generar CUALQUIER código (incluye PROLOG, Python, Java, C/C++ y pseudocódigo).\n"
    "Siempre entrega: conteos (estados generados/visitados), profundidad y camino completo cuando aplique.\n"
    "Ante empates de heurística/operadores, usa el orden fijo: Arriba, Abajo, Izquierda, Derecha.\n"
)

# ESTADOS FIJOS (8-Puzzle) 

EJ1_INITIAL = (1, 2, 3,
               4, 0, 6,
               7, 5, 8)
EJ1_GOAL    = (1, 2, 3,
               4, 5, 6,
               7, 8, 0)

def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Define la variable de entorno OPENAI_API_KEY en tu sistema.")
    return OpenAI(api_key=api_key)

def ask(client: OpenAI, prompt: str) -> str:
    try:
        resp = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": SYSTEM_BASE},
                {"role": "user", "content": prompt.strip()}
            ]
        )
        return resp.output_text
    except HTTPError as e:
        return f"[Error de red] {e}"
    except Exception as e:
        return f"[Error] {e}"

# PROMPTS
def prompt_ej1() -> str:
    ini = EJ1_INITIAL
    goal = EJ1_GOAL
    ini_mat  = f"{ini[0:3]}\n{ini[3:6]}\n{ini[6:9]}"
    goal_mat = f"{goal[0:3]}\n{goal[3:6]}\n{goal[6:9]}"

    return f"""
***Ejercicio 1 – 8-Puzzle (3×3)***
Datos del problema:
- Estado INICIAL (tupla 9, 0 = blanco): {ini}
  Como 3×3:
  {ini_mat}
- Estado OBJETIVO: {goal}
  Como 3×3:
  {goal_mat}
- Orden de operadores y desempate: Arriba, Abajo, Izquierda, Derecha.
- Convención de conteo:
  • Generados = estados distintos añadidos a la frontera (incluye el inicial; sin duplicados).
  • Visitados (expandidos) = estados a los que efectivamente se les generaron sucesores.
  • Se evita reinsertar estados ya vistos (en frontera o cerrados).
  • Se detiene al generar el objetivo (sin expandirlo).

Resuelve desde el estado inicial al objetivo con:
1) BFS (costo 1; orden de operadores indicado).
2) DFS con búsqueda en profundidad iterativa (IDDFS) con el mismo orden.
3) Best-First Greedy (f=h) con TRES heurísticas:
   • H1 = 8 − (# de baldosas bien ubicadas)  [minimizar]
   • H2 = suma de distancias Euclidianas de cada baldosa a su posición objetivo
   • H3 = suma de distancias Manhattan de cada baldosa a su posición objetivo

Para CADA método/heurística reporta EXACTAMENTE:
- Total de estados GENERADOS
- Total de estados VISITADOS (expandidos)
- Profundidad de la solución (número de movimientos)
- Camino (secuencia: Arriba/Abajo/Izquierda/Derecha) y una traza compacta de tableros

Compara:
- ¿Las soluciones (camino/profundidad) son iguales? ¿por qué?
- Entre H1/H2/H3, ¿cuál funciona mejor y por qué? Comenta admisibilidad/consistencia y efectos prácticos.

MUY IMPORTANTE: Al final, imprime una TABLA Markdown con estas filas y columnas EXACTAS:
| Método / h | Generados | Visitados | Profundidad | Camino |
Incluye una fila para: BFS, IDDFS, Greedy-H1, Greedy-H2, Greedy-H3, con los valores que obtuviste.
No generes nada de código.
""".strip()

def prompt_ej2() -> str:
    return """
***Ejercicio 2 – N-Queens (sin código)***
1) Explica brevemente el backtracking.
2) Reporta el número total de soluciones para 5×5 y 8×8 (indica si son todas o únicas por simetría).
3) Lista TODAS las soluciones de 5×5 y 8×8 en dos formatos:
   (a) Coordenadas (fila→columna) 1-based: (1,c1),(2,c2),…,(N,cN).
   (b) Índices lineales 1..N^2 por filas: i_r = N*(r−1) + c_r.
4) Discute para 11×11 y 27×27: complejidad temporal/espacial, explosión combinatoria, simetrías y pruning.
No generes código. Presenta listas legibles (por bloques si es necesario).
""".strip()

def prompt_ej3() -> str:
    return """
***Ejercicio 3 – 4-en-raya (4×4, X empieza, SIN gravedad)***
Convención: '.' = casilla vacía. Se puede colocar en cualquier casilla vacía (no hay gravedad).

CASO (a)
INICIAL:
. . . O
X . X O
. O . O
. . X X
FINAL:
. . . O
X . X O
. O O .
X O X X

CASO (b)
INICIAL:
. . . .
. . . .
. . X .
. . . O
FINAL:
. X X O
. O O X
. . X .
. . . .

CASO (c)
INICIAL:
X . . O
. X O O
. X X X
. . . O
FINAL:
X X X O
X X O O
O X X X
O O O O

Tarea (para cada caso a, b, c):
Usa Best-First (Greedy, f=h) con DOS heurísticas y reporta POR CADA UNA:
- H_Manhattan: define con precisión cómo mides “cuántas colocaciones faltan” para completar una de las 10 líneas ganadoras del 4×4 (4 horizontales, 4 verticales, 2 diagonales).
- H_Euclidiana: análogo, usando la norma L2 sobre los “esfuerzos” de las casillas vacías.
Salida requerida en cada caso y para cada heurística:
- Total de estados GENERADOS
- Total de estados VISITADOS (expandidos)
- Profundidad del estado final alcanzado (número de jugadas desde el estado inicial)
- Camino completo: secuencia de jugadas (Jugador, (fila,columna)) hasta alcanzar el estado FINAL indicado o demostrar imposibilidad (en b).
- Comparación breve entre H_Manhattan y H_Euclidiana en ese caso.

Reglas:
- No pidas datos adicionales; usa exactamente los tres casos arriba.
- No generes código. Responde con definiciones y secuencias en lenguaje natural muy claro.
""".strip()

def prompt_ej4() -> str:
    return """
***Ejercicio 4 – “PROLOG” en lenguaje natural (sin código)***
(a) Farmer–Wolf–Goat–Cabbage:
- Representación de estado (tupla de orillas), estado inicial y objetivo, movimientos válidos, restricciones.
- Estrategia de búsqueda (backtracking) descrita verbalmente.
- Secuencia válida de pasos (numerada) sin violar restricciones, justificando cada paso.

(b) Misioneros y Caníbales (3 y 3):
- Igual estructura: representación, restricciones de seguridad, ruta completa válida, y breve justificación.

No generes NINGÚN código ni pseudocódigo; usa especificación clara en texto.
""".strip()

# MAIN 
if __name__ == "__main__":
    client = get_client()

    print("\n=== EJERCICIO 1 ===\n")
    print(ask(client, prompt_ej1()))

    print("\n=== EJERCICIO 2 ===\n")
    print(ask(client, prompt_ej2()))

    print("\n=== EJERCICIO 3 ===\n")
    print(ask(client, prompt_ej3()))

    print("\n=== EJERCICIO 4 ===\n")
    print(ask(client, prompt_ej4()))
