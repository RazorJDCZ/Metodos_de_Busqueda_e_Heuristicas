# puzzle8_es.py
# Juan Diego Cadena
# 329220

from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple
import math
import heapq

Tablero = Tuple[int, ...]  
Accion = str               # 'Arriba','Abajo','Izquierda','Derecha'

OBJETIVO: Tablero = (1,2,3,4,5,6,7,8,0)

# Utilidades de tablero

def indice_a_rc(i: int) -> Tuple[int, int]:
    return divmod(i, 3)  

def rc_a_indice(fila: int, col: int) -> int:
    return fila*3 + col

def mostrar(tablero: Tablero) -> str:
    filas = []
    for f in range(3):
        fila = []
        for c in range(3):
            v = tablero[rc_a_indice(f, c)]
            fila.append(" " if v == 0 else str(v))
        filas.append(" ".join(f"{x:>2}" for x in fila))
    return "\n".join(filas)

def intercambiar(tablero: Tablero, i: int, j: int) -> Tablero:
    b = list(tablero)
    b[i], b[j] = b[j], b[i]
    return tuple(b)

def vecinos(tablero: Tablero) -> List[Tuple[Tablero, Accion, int]]:
    i0 = tablero.index(0)  
    f, c = indice_a_rc(i0)
    movimientos: List[Tuple[Tablero, Accion, int]] = []
    
    if f > 0:
        idx = rc_a_indice(f-1, c)
        ficha = tablero[idx]
        movimientos.append((intercambiar(tablero, i0, idx), 'Abajo', ficha))
    
    if f < 2:
        idx = rc_a_indice(f+1, c)
        ficha = tablero[idx]
        movimientos.append((intercambiar(tablero, i0, idx), 'Arriba', ficha))
    
    if c > 0:
        idx = rc_a_indice(f, c-1)
        ficha = tablero[idx]
        movimientos.append((intercambiar(tablero, i0, idx), 'Derecha', ficha))
    
    if c < 2:
        idx = rc_a_indice(f, c+1)
        ficha = tablero[idx]
        movimientos.append((intercambiar(tablero, i0, idx), 'Izquierda', ficha))
    return movimientos

def es_resoluble(tablero: Tablero) -> bool:
    arr = [x for x in tablero if x != 0]
    inversiones = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            inversiones += arr[i] > arr[j]
    return inversiones % 2 == 0

# Heurísticas

def h_mal_colocadas(tablero: Tablero, objetivo: Tablero) -> int:
    return sum(1 for i, v in enumerate(tablero) if v != 0 and v != objetivo[i])

def h_manhattan(tablero: Tablero, objetivo: Tablero) -> int:
    pos_obj: Dict[int, Tuple[int, int]] = {v: indice_a_rc(i) for i, v in enumerate(objetivo) if v != 0}
    s = 0
    for i, v in enumerate(tablero):
        if v == 0: 
            continue
        f, c = indice_a_rc(i)
        fo, co = pos_obj[v]
        s += abs(f - fo) + abs(c - co)
    return s

def h_euclidea(tablero: Tablero, objetivo: Tablero) -> float:
    pos_obj: Dict[int, Tuple[int, int]] = {v: indice_a_rc(i) for i, v in enumerate(objetivo) if v != 0}
    s = 0.0
    for i, v in enumerate(tablero):
        if v == 0:
            continue
        f, c = indice_a_rc(i)
        fo, co = pos_obj[v]
        s += math.hypot(f - fo, c - co)
    return s

# Estructuras de nodo y resultado

@dataclass(order=True)
class ElementoPQ:
    prioridad: float
    contador: int
    nodo: "Nodo" = field(compare=False)

@dataclass
class Nodo:
    estado: Tablero
    padre: Optional["Nodo"]
    accion: Optional[Accion]         
    ficha_movida: Optional[int]      
    profundidad: int

@dataclass
class ResultadoBusqueda:
    exito: bool
    nodo_objetivo: Optional[Nodo]
    visitados: int
    generados: int
    profundidad_max: int
    ancho_max: int
    explorados: int
    frontera_max: int

    def camino(self) -> List[Tablero]:
        if not self.exito or not self.nodo_objetivo:
            return []
        out: List[Tablero] = []
        n = self.nodo_objetivo
        while n:
            out.append(n.estado)
            n = n.padre
        return out[::-1]

    def acciones(self) -> List[str]:
        """Devuelve acciones legibles: 'Mover <ficha> hacia <dirección>'."""
        if not self.exito or not self.nodo_objetivo:
            return []
        out: List[str] = []
        n = self.nodo_objetivo
        while n and n.padre:
            out.append(f"Mover {n.ficha_movida} hacia {n.accion}")
            n = n.padre
        return out[::-1]

# BFS

def bfs(inicio: Tablero, objetivo: Tablero = OBJETIVO) -> ResultadoBusqueda:
    frontera: deque[Nodo] = deque([Nodo(inicio, None, None, None, 0)])
    visitados: Set[Tablero] = {inicio}
    cont_visitados, cont_generados = 0, 0
    profundidad_max, ancho_max, frontera_max = 0, 1, 1
    niveles = defaultdict(int)

    while frontera:
        frontera_max = max(frontera_max, len(frontera))
        nodo = frontera.popleft()
        cont_visitados += 1
        profundidad_max = max(profundidad_max, nodo.profundidad)

        if nodo.estado == objetivo:
            return ResultadoBusqueda(True, nodo, cont_visitados, cont_generados,
                                     nodo.profundidad, ancho_max, len(visitados), frontera_max)

        for est, acc, ficha in vecinos(nodo.estado):
            if est in visitados:
                continue
            hijo = Nodo(est, nodo, acc, ficha, nodo.profundidad + 1)
            frontera.append(hijo)
            visitados.add(est)
            cont_generados += 1
            niveles[hijo.profundidad] += 1
            ancho_max = max(ancho_max, niveles[hijo.profundidad])

    return ResultadoBusqueda(False, None, cont_visitados, cont_generados,
                             profundidad_max, ancho_max, len(visitados), frontera_max)

# DFS (con límite)

def dfs(inicio: Tablero, objetivo: Tablero = OBJETIVO, limite: int = 30) -> ResultadoBusqueda:
    pila: List[Nodo] = [Nodo(inicio, None, None, None, 0)]
    visitados: Set[Tablero] = {inicio}
    cont_visitados, cont_generados = 0, 0
    profundidad_max, ancho_max, frontera_max = 0, 1, 1
    niveles = defaultdict(int)

    while pila:
        frontera_max = max(frontera_max, len(pila))
        nodo = pila.pop()
        cont_visitados += 1
        profundidad_max = max(profundidad_max, nodo.profundidad)

        if nodo.estado == objetivo:
            return ResultadoBusqueda(True, nodo, cont_visitados, cont_generados,
                                     nodo.profundidad, ancho_max, len(visitados), frontera_max)

        if nodo.profundidad >= limite:
            continue

        for est, acc, ficha in vecinos(nodo.estado):
            if est in visitados:
                continue
            hijo = Nodo(est, nodo, acc, ficha, nodo.profundidad + 1)
            pila.append(hijo)
            visitados.add(est)
            cont_generados += 1
            niveles[hijo.profundidad] += 1
            ancho_max = max(ancho_max, niveles[hijo.profundidad])

    return ResultadoBusqueda(False, None, cont_visitados, cont_generados,
                             profundidad_max, ancho_max, len(visitados), frontera_max)

# Greedy Best-First Search

def best_first(inicio: Tablero,
               objetivo: Tablero = OBJETIVO,
               heuristica: Callable[[Tablero, Tablero], float] = lambda s, g: 0.0) -> ResultadoBusqueda:
    contador = 0
    cola: List[ElementoPQ] = []
    inicial = Nodo(inicio, None, None, None, 0)
    heapq.heappush(cola, ElementoPQ(heuristica(inicio, objetivo), contador, inicial))
    contador += 1

    visitados: Set[Tablero] = {inicio}
    cont_visitados, cont_generados = 0, 0
    profundidad_max, ancho_max, frontera_max = 0, 1, 1
    niveles = defaultdict(int)

    while cola:
        frontera_max = max(frontera_max, len(cola))
        elem = heapq.heappop(cola)
        nodo = elem.nodo
        cont_visitados += 1
        profundidad_max = max(profundidad_max, nodo.profundidad)

        if nodo.estado == objetivo:
            return ResultadoBusqueda(True, nodo, cont_visitados, cont_generados,
                                     nodo.profundidad, ancho_max, len(visitados), frontera_max)

        for est, acc, ficha in vecinos(nodo.estado):
            if est in visitados:
                continue
            hijo = Nodo(est, nodo, acc, ficha, nodo.profundidad + 1)
            heapq.heappush(cola, ElementoPQ(heuristica(est, objetivo), contador, hijo))
            contador += 1
            visitados.add(est)
            cont_generados += 1
            niveles[hijo.profundidad] += 1
            ancho_max = max(ancho_max, niveles[hijo.profundidad])

    return ResultadoBusqueda(False, None, cont_visitados, cont_generados,
                             profundidad_max, ancho_max, len(visitados), frontera_max)

# Mostrar resultados

def imprimir_resultado(res: ResultadoBusqueda) -> None:
    if not res.exito:
        print("No se encontró solución.")
        print(f"Visitados={res.visitados} Generados={res.generados} Prof_max={res.profundidad_max} Ancho_max={res.ancho_max}")
        return
    print(f"Solución en {res.nodo_objetivo.profundidad} movimientos")
    print(f"Visitados={res.visitados} Generados={res.generados} Prof_max={res.profundidad_max} Ancho_max={res.ancho_max}")
    print("Acciones:", " | ".join(res.acciones()))
    print("\nCamino:")
    for paso, tablero in enumerate(res.camino()):
        print(f"Paso {paso}:\n{mostrar(tablero)}\n")

# MAIN

if __name__ == "__main__":
    inicio: Tablero = (1, 2, 3,
                       4, 0, 6,
                       7, 5, 8)
    objetivo: Tablero = OBJETIVO

    print("Estado inicial:\n", mostrar(inicio))
    print("Estado objetivo:\n", mostrar(objetivo))
    print("¿Resoluble?:", es_resoluble(inicio))

    print("\n=== BFS ===")
    r_bfs = bfs(inicio, objetivo)
    imprimir_resultado(r_bfs)

    print("\n=== DFS ===")
    r_dfs = dfs(inicio, objetivo, limite=30)
    imprimir_resultado(r_dfs)

    print("\n=== Greedy Best-First: Baldosas mal colocadas ===")
    r_g1 = best_first(inicio, objetivo, heuristica=h_mal_colocadas)
    imprimir_resultado(r_g1)

    print("\n=== Greedy Best-First: Manhattan ===")
    r_g2 = best_first(inicio, objetivo, heuristica=h_manhattan)
    imprimir_resultado(r_g2)

    print("\n=== Greedy Best-First: Euclídea ===")
    r_g3 = best_first(inicio, objetivo, heuristica=h_euclidea)
    imprimir_resultado(r_g3)
