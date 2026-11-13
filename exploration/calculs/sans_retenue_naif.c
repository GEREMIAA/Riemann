/* Contrôle de sans_retenue.c par une méthode lente et indépendante.
 *
 * Pour chaque nombre m < 2^K : primalité ordinaire par un crible simple ; primalité sans retenue par divisions
 * successives (reste de la division de polynômes, chiffre par chiffre) par tous les premiers sans retenue de degré
 * au plus moitié. Les statistiques sont comptées nombre par nombre, sans aucune astuce. La sortie a le même format
 * que celle de sans_retenue.c : les deux doivent coïncider (à 10⁻⁴ près pour la dernière colonne, la somme des ln p).
 * Usage : ./sans_retenue_naif 26 > naif.txt      (vingt secondes)
 * Compilation : gcc -O3 -march=native -o sans_retenue_naif sans_retenue_naif.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
typedef unsigned long long u64;
static int degre(u64 v) { return 63 - __builtin_clzll(v); }
static u64 reste(u64 a, u64 P) {                       /* reste de la division sans retenue de a par P */
    int d = degre(P);
    while (a >> d) a ^= P << (degre(a) - d);
    return a;
}
int main(int argc, char **argv) {
    int K = argc > 1 ? atoi(argv[1]) : 20; u64 N = 1ULL << K;
    uint8_t *comp = calloc(N, 1), *irr = calloc(N, 1); comp[0] = comp[1] = 1;
    for (u64 p = 2; p * p < N; p++) if (!comp[p]) for (u64 m = p * p; m < N; m += p) comp[m] = 1;
    u64 *liste = malloc(8 * (N / 4 + 16)); u64 nl = 0;
    for (u64 m = 2; m < N; m++) {
        int d = degre(m), ok = 1;
        for (u64 k = 0; k < nl && 2 * degre(liste[k]) <= d; k++) if (reste(m, liste[k]) == 0) { ok = 0; break; }
        if (ok) { irr[m] = 1; if (2 * d <= K) liste[nl++] = m; }
    }
    for (int n = 1; n < K; n++) {
        u64 A = 0, I = 0, B = 0, Ai = 0, A2 = 0, J = 0, i3[3] = {0, 0, 0}, i7[7] = {0, 0, 0, 0, 0, 0, 0}; long double th = 0;
        for (u64 m = 1ULL << n; m < (2ULL << n); m++) {
            int poids = __builtin_popcountll(m);
            if (!comp[m]) {
                A++; th += logl((long double)m);
                if (poids & 1) { Ai++; if (reste(m, 7) != 0) A2++; }
            }
            if (irr[m]) {
                I++; i3[m % 3]++; i7[m % 7]++; if (!comp[m]) B++;
                if ((m ^ 6) > m && (m ^ 6) < N && irr[m ^ 6]) J++;
            }
        }
        printf("%d %llu %llu %llu %llu %llu %llu", n, A, I, B, Ai, A2, J);
        for (int r = 0; r < 3; r++) printf(" %llu", i3[r]);
        for (int r = 0; r < 7; r++) printf(" %llu", i7[r]);
        printf(" %.6Lf\n", th);
    }
    return 0;
}
