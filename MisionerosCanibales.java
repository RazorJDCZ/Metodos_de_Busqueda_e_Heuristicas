// Juan Diego Cadena
// 329220

import java.util.*;

public class MisionerosCanibales {

    // Estado: misioneros y caníbales en la orilla izquierda y posición del bote
    static final class Estado {
        final int mLeft, cLeft;
        final boolean boatLeft;

        Estado(int mLeft, int cLeft, boolean boatLeft) {
            this.mLeft = mLeft;
            this.cLeft = cLeft;
            this.boatLeft = boatLeft;
        }

        // Misioneros/Caníbales en la derecha se deducen del total (3)
        int mRight() { return 3 - mLeft; }
        int cRight() { return 3 - cLeft; }

        boolean esMeta() { return mLeft == 0 && cLeft == 0 && !boatLeft; }

        // Validez “interna” del estado 
        boolean esValido() {
            // Rango
            if (mLeft < 0 || mLeft > 3 || cLeft < 0 || cLeft > 3) return false;
            // Seguridad en la izquierda: si hay misioneros, no pueden ser mas
            if (mLeft > 0 && cLeft > mLeft) return false;
            // Seguridad en la derecha
            int mR = mRight(), cR = cRight();
            if (mR > 0 && cR > mR) return false;
            return true;
        }

        @Override
        public boolean equals(Object o) {
            if (!(o instanceof Estado)) return false;
            Estado e = (Estado) o;
            return mLeft == e.mLeft && cLeft == e.cLeft && boatLeft == e.boatLeft;
        }

        @Override
        public int hashCode() {
            return Objects.hash(mLeft, cLeft, boatLeft);
        }

        @Override
        public String toString() {
            return String.format("(M_izq=%d, C_izq=%d, bote=%s)", mLeft, cLeft, boatLeft ? "izq" : "der");
        }
    }

    // Movimiento posible del bote
    static final int[][] MOVS = {
        {2, 0}, // 2 M
        {0, 2}, // 2 C
        {1, 1}, // 1 M y 1 C
        {1, 0}, // 1 M
        {0, 1}  // 1 C
    };

    public static void main(String[] args) {
        Estado inicio = new Estado(3, 3, true);
        List<String> pasoActual = new ArrayList<>();
        List<List<String>> soluciones = new ArrayList<>();
        Set<Estado> visitados = new HashSet<>();

        backtrack(inicio, pasoActual, soluciones, visitados);

        if (soluciones.isEmpty()) {
            System.out.println("No se encontraron soluciones.");
        } else {
            System.out.println("Total de soluciones: " + soluciones.size());
            int k = 1;
            for (List<String> ruta : soluciones) {
                System.out.println("\n--- Solución " + (k++) + " (" + ruta.size() + " pasos) ---");
                int i = 1;
                for (String s : ruta) {
                    System.out.printf("%2d) %s%n", i++, s);
                }
            }
        }
    }

    // Backtracking DFS
    static void backtrack(Estado estado, List<String> ruta, List<List<String>> soluciones, Set<Estado> visitados) {
        if (!estado.esValido()) return;           
        if (estado.esMeta()) {                    
            soluciones.add(new ArrayList<>(ruta));
            return;
        }
        if (!visitados.add(estado)) return;       

        for (int[] mv : MOVS) {
            int m = mv[0], c = mv[1];
            Estado sig = mover(estado, m, c);
            if (sig == null || !sig.esValido()) continue;

            String descripcion = describeMovimiento(estado, sig, m, c);
            ruta.add(descripcion);
            backtrack(sig, ruta, soluciones, visitados);
            ruta.remove(ruta.size() - 1); 
        }

        visitados.remove(estado); 
    }

    // Aplica el movimiento elegido según dónde esté el bote
    static Estado mover(Estado e, int m, int c) {
        
        if (m + c < 1 || m + c > 2) return null;

        if (e.boatLeft) {
            
            if (m > e.mLeft || c > e.cLeft) return null;
            return new Estado(e.mLeft - m, e.cLeft - c, false);
        } else {
            
            if (m > e.mRight() || c > e.cRight()) return null;
            return new Estado(e.mLeft + m, e.cLeft + c, true);
        }
    }

    
    static String describeMovimiento(Estado desde, Estado hacia, int m, int c) {
        String dir = desde.boatLeft ? "izq -> der" : "der -> izq";
        return String.format(
            "Bote %s | Viajan: %d M, %d C | Estado antes %s | Estado después %s",
            dir, m, c, desde, hacia
        );
    }
}
