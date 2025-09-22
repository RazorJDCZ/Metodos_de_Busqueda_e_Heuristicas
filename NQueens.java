// NQueens.java
// Juan Diego Cadena
// 329220

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

public class NQueens {

    public static long contarYVolcar(int N, String archivo) throws IOException {
        long total;
        int[] colsPorFila = new int[N]; 
        BufferedWriter w = (archivo == null) ? null : new BufferedWriter(new FileWriter(archivo));

        // backtracking con bitmasks
        long all = (1L << N) - 1L;
        long[] kRef = new long[] {0L};  

        total = backtrack(0, 0L, 0L, 0L, all, N, colsPorFila, w, kRef);

        if (w != null) w.close();
        return total;
    }

    // Backtracking
    private static long backtrack(int fila, long cols, long diag1, long diag2, long all,
                                  int N, int[] colsPorFila, BufferedWriter w, long[] kRef) throws IOException {
        if (fila == N) {
            if (w != null) {
                kRef[0]++;
                volcarSolucion(colsPorFila, N, w, kRef[0]);
            }
            return 1L;
        }
        long total = 0L;
        long libres = all & ~(cols | diag1 | diag2);
        while (libres != 0) {
            long bit = libres & -libres;                
            int col = Long.numberOfTrailingZeros(bit);  
            colsPorFila[fila] = col;

            total += backtrack(
                fila + 1,
                cols | bit,
                (diag1 | bit) << 1,
                (diag2 | bit) >>> 1,
                all, N, colsPorFila, w, kRef
            );
            libres &= libres - 1;                       
        }
        return total;
    }

    private static void volcarSolucion(int[] colsPorFila, int N, BufferedWriter w, long k) throws IOException {
        w.write("#" + k);
        w.newLine();

        // ABS
        w.write("ABS: ");
        for (int i = 0; i < N; i++) {
            int posAbs = N * i + (colsPorFila[i] + 1); // 1..N*N
            if (i > 0) w.write(" ");
            w.write(Integer.toString(posAbs));
        }
        w.newLine();

        // COORDS
        w.write("COORDS: ");
        for (int i = 0; i < N; i++) {
            if (i > 0) w.write(" ");
            w.write("(" + (i + 1) + "," + (colsPorFila[i] + 1) + ")");
        }
        w.newLine();

        // BOARD
        w.write("BOARD:");
        w.newLine();
        for (int i = 0; i < N; i++) {
            StringBuilder row = new StringBuilder();
            for (int j = 0; j < N; j++) {
                row.append(j == colsPorFila[i] ? 'Q' : '.');
                if (j + 1 < N) row.append(' ');
            }
            w.write(row.toString());
            w.newLine();
        }
        w.newLine(); 
    }

    // MAIN

    public static void main(String[] args) throws Exception {
        long t;

        t = System.currentTimeMillis();
        long c5 = contarYVolcar(5, "soluciones_5x5.txt");
        System.out.printf(Locale.US, "N=5  -> %d soluciones (archivo: soluciones_5x5.txt)  [%.3f s]%n",
                c5, (System.currentTimeMillis() - t) / 1000.0);

        t = System.currentTimeMillis();
        long c8 = contarYVolcar(8, "soluciones_8x8.txt");
        System.out.printf(Locale.US, "N=8  -> %d soluciones (archivo: soluciones_8x8.txt)  [%.3f s]%n",
                c8, (System.currentTimeMillis() - t) / 1000.0);

        t = System.currentTimeMillis();
        long c11 = contarYVolcar(11, null); // solo cuenta; no genera archivo
        System.out.printf(Locale.US, "N=11 -> %d soluciones  [%.3f s]%n",
                c11, (System.currentTimeMillis() - t) / 1000.0);

        // t = System.currentTimeMillis();
        // long c27 = contarYVolcar(27, null);
        // System.out.printf(Locale.US, "N=27 -> %d soluciones  [%.3f s]%n",
        //         c27, (System.currentTimeMillis() - t) / 1000.0);
    }
}
