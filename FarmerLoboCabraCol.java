// Juan Diego Cadena
// 329220

import java.util.*;

public class FarmerLoboCabraCol {

    static final int GRANJERO = 1; // 0001
    static final int LOBO     = 2; // 0010
    static final int CABRA    = 4; // 0100
    static final int COL      = 8; // 1000

    static final int INICIAL = 0;                 // 0000 todos a la izquierda
    static final int OBJETIVO = GRANJERO|LOBO|CABRA|COL; // 1111 todos a la derecha

    public static void main(String[] args) {
        List<Integer> solucion = new ArrayList<>();
        Set<Integer> visitados = new HashSet<>();

        boolean encontrado = backtrack(INICIAL, visitados, solucion);

        if (encontrado) {
            imprimirSolucion(solucion);
        } else {
            System.out.println("No se encontró una solución.");
        }

    }

    // Backtracking
    private static boolean backtrack(int estado, Set<Integer> visitados, List<Integer> camino) {
        camino.add(estado);
        visitados.add(estado);

        if (estado == OBJETIVO) return true;

        for (int siguiente : generarMovimientosValidos(estado)) {
            if (!visitados.contains(siguiente)) {
                if (backtrack(siguiente, visitados, camino)) return true;
            }
        }

        // retroceder
        camino.remove(camino.size() - 1);
        return false;
    }

    
    private static List<Integer> generarMovimientosValidos(int estado) {
        List<Integer> siguientes = new ArrayList<>();

        boolean granjeroDerecha = lado(estado, GRANJERO);

        int[] posiblesCompaneros = {0, LOBO, CABRA, COL};

        for (int comp : posiblesCompaneros) {
            if (comp != 0 && lado(estado, comp) != granjeroDerecha) continue;

            int nuevo = mover(estado, GRANJERO); 
            if (comp != 0) nuevo = mover(nuevo, comp); 

            if (esValido(nuevo)) siguientes.add(nuevo);
        }
        return siguientes;
    }

    
    private static boolean lado(int estado, int actorMask) {
        return (estado & actorMask) != 0;
    }

    
    private static int mover(int estado, int actorMask) {
        return estado ^ actorMask;
    }

    private static boolean esValido(int estado) {
        boolean granjeroDer = lado(estado, GRANJERO);
        boolean loboDer     = lado(estado, LOBO);
        boolean cabraDer    = lado(estado, CABRA);
        boolean colDer      = lado(estado, COL);

        boolean loboConCabraIzq = (!loboDer && !cabraDer && granjeroDer);
        boolean loboConCabraDer = ( loboDer &&  cabraDer && !granjeroDer);


        boolean cabraConColIzq = (!cabraDer && !colDer && granjeroDer);
        boolean cabraConColDer = ( cabraDer &&  colDer && !granjeroDer);

        return !(loboConCabraIzq || loboConCabraDer || cabraConColIzq || cabraConColDer);
    }

    private static void imprimirSolucion(List<Integer> camino) {
        System.out.println("Solución encontrada (" + (camino.size()-1) + " cruces):\n");

        for (int i = 0; i < camino.size()-1; i++) {
            int desde = camino.get(i);
            int hacia = camino.get(i+1);

            String dir = lado(desde, GRANJERO) ? "DERECHA -> IZQUIERDA" : "IZQUIERDA -> DERECHA";
            String companero = companeroMovido(desde, hacia);

            System.out.printf("Paso %d: Granjero lleva %s (%s)\n",
                    i+1, companero, dir);

            System.out.println("   Estado: " + describir(hacia));
        }

        System.out.println("\n¡Todos llegaron a la DERECHA!");
    }

    
    private static String companeroMovido(int desde, int hacia) {
        int diff = desde ^ hacia;        
        diff &= ~GRANJERO;               
        if (diff == 0) return "a nadie";
        if (diff == LOBO) return "al LOBO";
        if (diff == CABRA) return "a la CABRA";
        if (diff == COL)  return "la COL";
        return "(desconocido)";
    }

    
    private static String describir(int estado) {
        List<String> izq = new ArrayList<>();
        List<String> der = new ArrayList<>();

        poner(estado, GRANJERO, "Granjero", izq, der);
        poner(estado, LOBO,     "Lobo",     izq, der);
        poner(estado, CABRA,    "Cabra",    izq, der);
        poner(estado, COL,      "Col",      izq, der);

        return String.format("[Izq: %s | Der: %s]",
                String.join(", ", izq), String.join(", ", der));
    }

    private static void poner(int estado, int mask, String nombre, List<String> izq, List<String> der) {
        if ((estado & mask) == 0) izq.add(nombre); else der.add(nombre);
    }

    

    private static List<List<Integer>> todasLasSoluciones() {
        List<List<Integer>> todas = new ArrayList<>();
        Set<Integer> visitados = new HashSet<>();
        dfsTodas(INICIAL, visitados, new ArrayList<>(), todas);
        return todas;
    }

    private static void dfsTodas(int estado, Set<Integer> visitados, List<Integer> camino, List<List<Integer>> todas) {
        camino.add(estado);
        visitados.add(estado);
        if (estado == OBJETIVO) {
            todas.add(new ArrayList<>(camino));
        } else {
            for (int sig : generarMovimientosValidos(estado)) {
                if (!visitados.contains(sig)) {
                    dfsTodas(sig, visitados, camino, todas);
                }
            }
        }
        camino.remove(camino.size()-1);
        visitados.remove(estado);
    }

    private static void imprimirTodas(List<List<Integer>> todas) {
        System.out.println("Total de soluciones: " + todas.size());
        for (int k = 0; k < todas.size(); k++) {
            System.out.println("\n--- Solución " + (k+1) + " ---");
            imprimirSolucion(todas.get(k));
        }
    }
}
