/* Un monde sans retenue qui n'a qu'une note.
 *
 * Les nombres écrits avec des 0 et des 1, additionnés sans retenue, forment un monde dont la fonction zêta n'a aucun
 * zéro (voir sans_retenue.c). Pour avoir des zéros, on ajoute une deuxième lettre y, liée à x par une équation.
 * Ici : la courbe E : y² + xy = x³ + 1 (une courbe de Koblitz, de celles qu'on utilise en cryptographie).
 * Sa fonction zêta a deux zéros, conjugués : 2^(−s) = 1/α, avec α = (−1 + i√7)/2. Comme |α| = √2, ils sont sur la
 * droite Re s = ½ : c'est l'hypothèse de Riemann de ce monde, et c'est un théorème (Hasse, 1933).
 * Conséquence qu'on peut compter : le nombre N_n de points de la courbe dans le corps à 2^n éléments vaut
 *       N_n = 2^n + 1 − a_n,   a_n = α^n + conj(α)^n = 2·2^(n/2)·cos(nθ),   θ = arg α = 110,7°.
 * Une seule onde, d'amplitude exactement 2·√(2^n) : une note pure.
 *
 * Le programme compte vraiment les points, un par un. Le corps à 2^n éléments est fait des nombres de n chiffres
 * binaires, multipliés sans retenue modulo un polynôme primitif M : alors x, x², x³… parcourent tous les éléments
 * non nuls, et 1/x, 1/x²… se calculent aussi par un simple décalage. Pour x ≠ 0, on pose y = xz : l'équation devient
 * z² + z = x + 1/x², qui a deux solutions si la « trace » de x + 1/x est nulle, aucune sinon. S'y ajoutent le point
 * (0, 1) et le point à l'infini.
 * Sortie, une ligne par n : n, le polynôme M, N_n compté, a_n = 2^n + 1 − N_n, a_n prédit par la récurrence
 * a_n = −a_(n−1) − 2·a_(n−2), et a_n/√(2^n).
 * Usage : ./monde_a_une_note 38 > monde_a_une_note.txt        (deux cœurs : dix minutes ; 32 : dix secondes)
 * Compilation : gcc -O3 -march=native -fopenmp -o monde_a_une_note monde_a_une_note.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>
typedef unsigned long long u64;
static int n; static u64 M;
static u64 mul(u64 a, u64 b) {                       /* produit sans retenue modulo M */
    u64 r = 0;
    while (b) { if (b & 1) r ^= a; b >>= 1; a <<= 1; if ((a >> n) & 1) a ^= M; }
    return r;
}
static u64 puiss(u64 a, u64 e) { u64 r = 1; while (e) { if (e & 1) r = mul(r, a); a = mul(a, a); e >>= 1; } return r; }

int main(int argc, char **argv) {
    int nmax = argc > 1 ? atoi(argv[1]) : 24;
    long long a2 = 2, a1 = -1;                         /* a_0 = 2, a_1 = −1 */
    for (n = 1; n <= nmax; n++) {
        u64 e = (1ULL << n) - 1, f[64]; int nf = 0;    /* facteurs premiers de 2^n − 1 */
        { u64 m = e; for (u64 q = 3; q * q <= m; q += 2) if (m % q == 0) { f[nf++] = q; while (m % q == 0) m /= q; } if (m > 1) f[nf++] = m; }
        u64 X = n == 1 ? 1 : 2;                        /* l'élément x */
        for (M = (1ULL << n) | 1; ; M += 2) {          /* le premier polynôme primitif de degré n */
            if (puiss(X, e) != 1) continue;
            int ok = 1; for (int i = 0; i < nf && ok; i++) if (puiss(X, e / f[i]) == 1) ok = 0;
            if (ok) break;
        }
        u64 tau = 0;                                   /* trace(z) = parité de (z & tau) */
        for (int j = 0; j < n; j++) {
            u64 z = puiss(X, j), t = 0;
            for (int k = 0; k < n; k++) { t ^= z; z = mul(z, z); }
            if (t & 1) tau |= 1ULL << j;
        }
        u64 impairs = 0; int nt = n < 12 ? 1 : omp_get_max_threads();
        #pragma omp parallel for reduction(+:impairs) num_threads(nt)
        for (int t = 0; t < nt; t++) {
            u64 k0 = e / nt * t, k1 = t == nt - 1 ? e : e / nt * (t + 1), c = 0;
            u64 u = puiss(X, k0), v = puiss(X, e - k0), Mh = M >> 1;
            for (u64 k = k0; k < k1; k++) {
                c += __builtin_parityll((u ^ v) & tau);
                u <<= 1; if ((u >> n) & 1) u ^= M;     /* u = x^k */
                v = (v >> 1) ^ ((v & 1) ? Mh : 0);     /* v = x^(−k) */
            }
            impairs += c;
        }
        long long N = 2 + 2 * (long long)(e - impairs), a = (1LL << n) + 1 - N;
        long long pred = n == 1 ? -1 : -a1 - 2 * a2;
        printf("%d %llu %lld %lld %lld %.6f\n", n, M, N, a, pred, a / sqrt((double)(1ULL << n)));
        fflush(stdout);
        if (n > 1) { a2 = a1; a1 = pred; }
    }
    return 0;
}
