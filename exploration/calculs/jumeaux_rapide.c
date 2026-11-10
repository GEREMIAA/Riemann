// Crible rapide des paires de nombres premiers (p, p + h), h = 2, 4, 6, jusqu'à N, sur les seuls nombres 6k ± 1.
// Pour chaque point x d'une grille donnée (fichier d'entiers int64 croissants), on écrit
//   C_h(x) = nombre de p ≤ x avec p et p + h premiers,   W_h(x) = Σ ln p · ln(p + h) sur ces p.
// Compilation : gcc -O3 -march=native -fopenmp jumeaux_rapide.c -o jumeaux_rapide -lm
// Usage : ./jumeaux_rapide 1e12 grille_1e+12.bin sortie_1e+12.bin      (une demi-heure sur deux cœurs ; 14 s jusqu'à 10¹⁰)
// La grille (la même que celle de crible_paires.py, prolongée) se fabrique ainsi :
//   python3 -c "import numpy as np, math; np.exp(np.arange(math.log(1e3), math.log(1e12), 0.0005)).astype(np.int64).tofile('grille_1e+12.bin')"
// puis : python3 musique_des_jumeaux.py crible_1e+10.npz zeros_100000.npy sortie_1e+12.bin grille_1e+12.bin
// Sortie : pour chaque point de la grille, 3 compteurs (int64) puis 3 sommes (double), h = 2, 4, 6.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <omp.h>

#define SEG (1u << 21)            // nombre de valeurs de k par segment
#define PER 5005u                 // 5 · 7 · 11 · 13 : motif périodique en k pour les petits premiers

static uint32_t *P, *R1, *R2; static size_t NP;

static void petits_premiers(uint64_t lim) {
    uint8_t *s = calloc(lim + 1, 1); NP = 0;
    P = malloc(sizeof(uint32_t) * (lim / 2 + 16)); R1 = malloc(sizeof(uint32_t) * (lim / 2 + 16)); R2 = malloc(sizeof(uint32_t) * (lim / 2 + 16));
    for (uint64_t i = 2; i <= lim; i++) {
        if (s[i]) continue;
        for (uint64_t j = i * i; j <= lim; j += i) s[j] = 1;
        if (i >= 17) {                                   // 5, 7, 11, 13 sont dans le motif
            uint64_t inv = (i % 6 == 1) ? i - (i - 1) / 6 : (i - 5) / 6 + 1;     // 6·inv ≡ 1 (mod i)
            P[NP] = (uint32_t)i; R1[NP] = (uint32_t)inv; R2[NP] = (uint32_t)((i - inv) % i); NP++;
        }
    }
    free(s);
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage : %s N grille.bin sortie.bin\n", argv[0]); return 1; }
    uint64_t N = (uint64_t)strtod(argv[1], NULL);
    FILE *fg = fopen(argv[2], "rb"); fseek(fg, 0, SEEK_END); size_t G = ftell(fg) / 8; fseek(fg, 0, SEEK_SET);
    int64_t *X = malloc(8 * G); if (fread(X, 8, G, fg) != G) return 2; fclose(fg);
    petits_premiers((uint64_t)sqrt((double)N + 64) + 2);
    uint64_t K = N / 6 + 2;                               // k ≤ K couvre 6k ± 1 ≤ N + quelques unités
    size_t nseg = (K + SEG - 1) / SEG;
    // motif des multiples de 5, 7, 11, 13 parmi les 6k − 1 (A) et 6k + 1 (B)
    uint8_t PA[PER], PB[PER];
    for (uint32_t k = 0; k < PER; k++) {
        uint64_t a = 6ull * k + 6 * PER - 1, b = 6ull * k + 1;
        PA[k] = (a % 5 && a % 7 && a % 11 && a % 13); PB[k] = (b % 5 && b % 7 && b % 11 && b % 13);
    }
    long double *totC = calloc(3 * nseg, sizeof(long double)), *totW = calloc(3 * nseg, sizeof(long double));
    int64_t *gC = calloc(3 * G, 8); double *gW = calloc(3 * G, 8); int64_t *gseg = malloc(8 * G);
    double t0 = omp_get_wtime(); volatile size_t fait = 0;
    #pragma omp parallel
    {
        uint8_t *A = malloc(SEG + 2), *B = malloc(SEG + 2);
        #pragma omp for schedule(dynamic, 8)
        for (size_t sg = 0; sg < nseg; sg++) {
            uint64_t k0 = 1 + (uint64_t)sg * SEG, k1 = k0 + SEG;          // k dans [k0, k1), plus k1 pour regarder devant
            if (k0 > K) continue;
            for (uint64_t k = k0; k <= k1; k++) { A[k - k0] = PA[k % PER]; B[k - k0] = PB[k % PER]; }
            if (k0 == 1) { A[0] = 1; B[0] = 1; A[1] = 1; B[1] = 1; }      // 5, 7, 11, 13 eux-mêmes sont premiers
            for (size_t i = 0; i < NP; i++) {
                uint64_t p = P[i], pp = p * p; if (pp > 6 * k1 + 1) break;
                uint64_t kmin = (pp + 1 + 5) / 6; if (kmin < k0) kmin = k0;          // 6k − 1 ≥ p²
                uint64_t s = kmin + (R1[i] + p - kmin % p) % p;
                for (uint64_t k = s; k <= k1; k += p) A[k - k0] = 0;
                kmin = (pp - 1 + 5) / 6; if (kmin < k0) kmin = k0;                   // 6k + 1 ≥ p²
                s = kmin + (R2[i] + p - kmin % p) % p;
                for (uint64_t k = s; k <= k1; k += p) B[k - k0] = 0;
            }
            // premier point de la grille concerné par ce segment
            int64_t xlo = 6 * (int64_t)k0 - 1, xhi = 6 * (int64_t)k1 - 1;
            size_t lo = 0, hi = G; while (lo < hi) { size_t m = (lo + hi) / 2; if (X[m] < xlo) lo = m + 1; else hi = m; }
            size_t j = lo; double c[3] = {0, 0, 0}, w[3] = {0, 0, 0};
            uint64_t kend = k1; if (kend > K) kend = K;
            for (uint64_t k = k0; k < kend; k++) {
                uint8_t a = A[k - k0], bq = B[k - k0], a1 = A[k - k0 + 1], b1 = B[k - k0 + 1];
                if (!(a | bq)) continue;
                int64_t pm = 6 * (int64_t)k - 1, pq = pm + 2;
                while (j < G && X[j] < pm && X[j] < xhi) { for (int h = 0; h < 3; h++) { gC[3 * j + h] = (int64_t)c[h]; gW[3 * j + h] = w[h]; } gseg[j] = sg; j++; }
                if (a && pm <= (int64_t)N) {
                    double lp = log((double)pm);
                    if (bq) { c[0] += 1; w[0] += lp * log((double)pm + 2); }               // (6k − 1, 6k + 1)
                    if (a1) { c[2] += 1; w[2] += lp * log((double)pm + 6); }               // (6k − 1, 6k + 5)
                }
                while (j < G && X[j] < pq && X[j] < xhi) { for (int h = 0; h < 3; h++) { gC[3 * j + h] = (int64_t)c[h]; gW[3 * j + h] = w[h]; } gseg[j] = sg; j++; }
                if (bq && pq <= (int64_t)N) {
                    double lq = log((double)pq);
                    if (a1) { c[1] += 1; w[1] += lq * log((double)pq + 4); }               // (6k + 1, 6k + 5)
                    if (b1) { c[2] += 1; w[2] += lq * log((double)pq + 6); }               // (6k + 1, 6k + 7)
                }
            }
            while (j < G && X[j] < xhi) { for (int h = 0; h < 3; h++) { gC[3 * j + h] = (int64_t)c[h]; gW[3 * j + h] = w[h]; } gseg[j] = sg; j++; }
            for (int h = 0; h < 3; h++) { totC[3 * sg + h] = c[h]; totW[3 * sg + h] = w[h]; }
            size_t f;
            #pragma omp atomic capture
            f = ++fait;
            if (f % 20000 == 0) { fprintf(stderr, "%zu / %zu segments, %.0f s\n", f, nseg, omp_get_wtime() - t0); }
        }
        free(A); free(B);
    }
    // sommes cumulées des segments, puis valeurs aux points de la grille ; plus les paires avec p = 3 : (3, 5) et (3, 7)
    long double *pre = calloc(3 * (nseg + 1), sizeof(long double)), *preW = calloc(3 * (nseg + 1), sizeof(long double));
    for (size_t s = 0; s < nseg; s++) for (int h = 0; h < 3; h++) { pre[3 * (s + 1) + h] = pre[3 * s + h] + totC[3 * s + h]; preW[3 * (s + 1) + h] = preW[3 * s + h] + totW[3 * s + h]; }
    double extraC[3] = {1, 1, 0}, extraW[3] = {log(3.0) * log(5.0), log(3.0) * log(7.0), 0};
    FILE *fo = fopen(argv[3], "wb");
    for (size_t j = 0; j < G; j++) {
        int64_t cc[3]; double ww[3];
        for (int h = 0; h < 3; h++) {
            if (X[j] > (int64_t)N) { cc[h] = -1; ww[h] = NAN; continue; }
            cc[h] = (int64_t)(pre[3 * gseg[j] + h] + gC[3 * j + h] + extraC[h]);
            ww[h] = (double)(preW[3 * gseg[j] + h] + (long double)gW[3 * j + h] + extraW[h]);
        }
        fwrite(cc, 8, 3, fo); fwrite(ww, 8, 3, fo);
    }
    fclose(fo);
    fprintf(stderr, "fini : %zu segments, %.0f s ; paires (h = 2, 4, 6) : %.0Lf %.0Lf %.0Lf\n", nseg, omp_get_wtime() - t0,
            pre[3 * nseg] + 1, pre[3 * nseg + 1] + 1, pre[3 * nseg + 2]);
    return 0;
}
