
# Juan Diego Cadena 
# 329220

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable, Set
import heapq

# Representación 
# Valores: 'X', 'O', '_'  (vacío)
Tablero = Tuple[str, ...]  
Accion = Tuple[int, str]   

def rc_a_i(r:int, c:int) -> int: return r*4 + c
def i_a_rc(i:int) -> Tuple[int,int]: return divmod(i,4)

def mostrar(board: Tablero) -> str:
    out = []
    for r in range(4):
        fila = board[r*4:(r+1)*4]
        out.append(" ".join(f"{x:>1}" for x in fila))
    return "\n".join(out)

def turno(board: Tablero) -> str:
    x = sum(1 for v in board if v=='X')
    o = sum(1 for v in board if v=='O')
    return 'X' if x==o else 'O'


def es_subtablero(inicial: Tablero, final: Tablero) -> bool:
    """
    Inicial sólo puede tener marcas que también estén en el final (no se puede borrar ni sobreescribir).
    """
    for i, v in enumerate(inicial):
        if v == '_': 
            continue
        if v != final[i]: 
            return False
    
    if sum(1 for v in final if v=='X') < sum(1 for v in inicial if v=='X'):
        return False
    if sum(1 for v in final if v=='O') < sum(1 for v in inicial if v=='O'):
        return False
    return True

def cuentas_coherentes_con_turnos(inicial: Tablero, final: Tablero) -> bool:
    """
    X empieza. A lo largo del camino siempre se alterna X,O,X,O...
    Eso implica que en cualquier prefijo válido: 0 <= (#X - #O) <= 1.
    Para el estado final, debe cumplirse:
       #X == #O  ó  #X == #O + 1
    y nunca #O > #X.
    """
    x0 = sum(1 for v in inicial if v=='X')
    o0 = sum(1 for v in inicial if v=='O')
    xf = sum(1 for v in final if v=='X')
    of = sum(1 for v in final if v=='O')
    
    if not (o0 <= x0 <= o0+1): 
        return False
    
    if of > xf: 
        return False
    if not (xf == of or xf == of+1):
        return False
    return True

# Sucesores 

def sucesores(board: Tablero, final: Tablero, forzar_hacia_meta: bool=True) -> List[Tuple[Tablero, Accion]]:
    """
    Genera nuevos tableros colocando el símbolo del turno en una celda vacía.
    Si forzar_hacia_meta=True, sólo permite colocar donde el final requiere ese símbolo.
    Esto reduce fuertemente el branching y respeta que no se “deshacen” jugadas.
    """
    t = turno(board)
    vecinos = []
    for i, v in enumerate(board):
        if v != '_': 
            continue
        if forzar_hacia_meta and final[i] != t:
            
            continue
        b = list(board)
        b[i] = t
        vecinos.append((tuple(b), (i, t)))
    return vecinos

# Heurísticas 

def faltantes(board: Tablero, final: Tablero) -> int:
    """Celdas que faltan por poner correctamente (final[i] != '_' y board[i] == '_')."""
    cnt = 0
    for i in range(16):
        if final[i] != '_' and board[i] == '_':
            cnt += 1
    return cnt

def h_manhattan(board: Tablero, final: Tablero) -> float:
    return float(faltantes(board, final))

def h_euclidea(board: Tablero, final: Tablero) -> float:
    return float(faltantes(board, final))

#  Estructuras de búsqueda 

@dataclass(order=True)
class PQElem:
    prioridad: float
    ord: int
    nodo: "Nodo" = field(compare=False)

@dataclass
class Nodo:
    estado: Tablero
    padre: Optional["Nodo"]
    accion: Optional[Accion]  
    profundidad: int

@dataclass
class Resultado:
    exito: bool
    nodo_obj: Optional[Nodo]
    visitados: int
    generados: int

    def camino(self) -> List[Tablero]:
        if not self.exito or not self.nodo_obj:
            return []
        seq = []
        n = self.nodo_obj
        while n:
            seq.append(n.estado)
            n = n.padre
        return list(reversed(seq))

    def jugadas(self) -> List[str]:
        if not self.exito or not self.nodo_obj:
            return []
        ops = []
        n = self.nodo_obj
        while n and n.padre:
            i, s = n.accion
            r, c = i_a_rc(i)
            ops.append(f"Colocar {s} en ({r},{c})")
            n = n.padre
        return list(reversed(ops))

#  Best-First (Greedy) 

def best_first(inicial: Tablero, final: Tablero,
               heuristica: Callable[[Tablero, Tablero], float]=h_manhattan,
               forzar_hacia_meta: bool=True) -> Resultado:
    
    if not es_subtablero(inicial, final):
        return Resultado(False, None, 0, 0)
    if not cuentas_coherentes_con_turnos(inicial, final):
        return Resultado(False, None, 0, 0)

    visitados: Set[Tablero] = set([inicial])
    generados = 0
    visit_count = 0
    pq: List[PQElem] = []
    ordc = 0
    raiz = Nodo(inicial, None, None, 0)
    heapq.heappush(pq, PQElem(heuristica(inicial, final), ordc, raiz)); ordc += 1

    while pq:
        elem = heapq.heappop(pq)
        nodo = elem.nodo
        visit_count += 1
        if nodo.estado == final:
            return Resultado(True, nodo, visit_count, generados)

        for est, acc in sucesores(nodo.estado, final, forzar_hacia_meta=forzar_hacia_meta):
            if est in visitados: 
                continue
            hijo = Nodo(est, nodo, acc, nodo.profundidad+1)
            heapq.heappush(pq, PQElem(heuristica(est, final), ordc, hijo)); ordc += 1
            visitados.add(est); generados += 1

    return Resultado(False, None, visit_count, generados)

#  Helpers para construir tableros desde strings 

def board_from_rows(rows: List[str]) -> Tablero:
    """
    rows: 4 strings de longitud 4 usando 'X','O','_' (o ' ' como vacío).
    """
    cells = []
    for r in rows:
        for ch in r:
            cells.append('_' if ch in (' ','_') else ch)
    assert len(cells)==16
    return tuple(cells)



def ejemplo():
    
    inicial_a = board_from_rows([
        "_X__",
        "O___",
        "_O__",
        "__X_",
    ])
    final_a = board_from_rows([
        "O_O_",
        "XXO_",
        "_OO_",
        "X_XX",
    ])

    print("Caso (a):")
    print("Inicial:\n", mostrar(inicial_a))
    print("Final:\n", mostrar(final_a))
    res_a_m = best_first(inicial_a, final_a, heuristica=h_manhattan, forzar_hacia_meta=True)
    if res_a_m.exito:
        print(f"Éxito en {len(res_a_m.jugadas())} jugadas.")
        print("Jugadas:", " | ".join(res_a_m.jugadas()))
        print(f"Visitados={res_a_m.visitados}  Generados={res_a_m.generados}")
    else:
        print("No hay solución (contradicción o alternancia inválida).")
        print(f"Visitados={res_a_m.visitados}  Generados={res_a_m.generados}")

    
    inicial_b = board_from_rows([
        "____",
        "____",
        "____",
        "____",
    ])
    final_b = board_from_rows([
        "XXXO",
        "OOOX",
        "__X_",
        "O___",
    ])
    print("\nCaso (b):")
    print("Inicial:\n", mostrar(inicial_b))
    print("Final:\n", mostrar(final_b))
    res_b = best_first(inicial_b, final_b, heuristica=h_euclidea, forzar_hacia_meta=True)
    if res_b.exito:
        print(f"Éxito en {len(res_b.jugadas())} jugadas.")
        print("Jugadas:", " | ".join(res_b.jugadas()))
        print(f"Visitados={res_b.visitados}  Generados={res_b.generados}")
    else:
        print("No hay solución o no hay ganador posible (ver comentario abajo).")
        print(f"Visitados={res_b.visitados}  Generados={res_b.generados}")

    inicial_c = board_from_rows([
        "X__O",
        "_XOO",
        "_XXX",
        "___O",
    ])
    final_c = board_from_rows([
        "XXXO",
        "XXOO",
        "OXXX",
        "OOOO",
    ])
    print("\nCaso (c):")
    print("Inicial:\n", mostrar(inicial_c))
    print("Final:\n", mostrar(final_c))
    res_c = best_first(inicial_c, final_c, heuristica=h_euclidea, forzar_hacia_meta=True)
    if res_c.exito:
        print(f"Éxito en {len(res_c.jugadas())} jugadas.")
        print("Jugadas:", " | ".join(res_c.jugadas()))
        print(f"Visitados={res_c.visitados}  Generados={res_c.generados}")
    else:
        print("No hay solución o no hay ganador posible (ver comentario abajo).")
        print(f"Visitados={res_c.visitados}  Generados={res_c.generados}")

if __name__ == "__main__":
    ejemplo()
