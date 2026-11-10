// Crible des k-uplets de nombres premiers (p, p + a₁, …, p + a_{k−1}) jusqu'à N, pour une liste de motifs.
// Pour chaque point x d'une grille (fichier d'entiers int64 croissants) et chaque motif H, on écrit
//   C_H(x) = nombre de p ≤ x tels que tous les p + a_i sont premiers,   W_H(x) = Σ Π_i ln(p + a_i) sur ces p.
// (Hardy–Littlewood : W_H(x) ≈ S(H)·x.)
// Compilation : gcc -O3 -march=native -fopenmp triplets_rapide.c -o triplets_rapide -lm
// Usage : ./triplets_rapide 1e10 grille_1e+10.bin motifs_triplets.txt sortie_triplets_1e+10.bin        (quelques minutes)
// motifs_triplets.txt : un motif par ligne, par exemple « 0 2 6 » (ici les 50 triplets (0, a, b), b ≤ 24, que les petits
// premiers 2, 3, 5, 7 n'interdisent pas, et le quadruplet (0, 2, 6, 8)). La grille, la même que celle de crible_paires.py :
//   python3 -c "import numpy as np, math; np.exp(np.arange(math.log(1e3), math.log(1e10), 0.0005)).astype(np.int64).tofile('grille_1e+10.bin')"
// puis : python3 musique_des_triplets.py crible_1e+10.npz sortie_triplets_1e+10.bin motifs_triplets.txt
// Sortie : pour chaque point de la grille, pour chaque motif : le compte (int64) puis la somme (double).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <omp.h>

#define SEG (1u << 23)
#define KMAX 6
#define MMAX 128

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage : %s N grille.bin motifs.txt sortie.bin\n", argv[0]); return 1; }
    uint64_t N = (uint64_t)strtod(argv[1], NULL);
    FILE *fg = fopen(argv[2], "rb"); fseek(fg, 0, SEEK_END); size_t G = ftell(fg) / 8; fseek(fg, 0, SEEK_SET);
    int64_t *X = malloc(8 * G); if (fread(X, 8, G, fg) != G) return 2; fclose(fg);
    int nm = 0, km[MMAX], am[MMAX][KMAX], amax = 0; char ligne[256];
    FILE *fm = fopen(argv[3], "r");
    while (fgets(ligne, sizeof ligne, fm) && nm < MMAX) {
        int k = 0; char *s = ligne, *e;
        while (k < KMAX) { long v = strtol(s, &e, 10); if (e == s) break; am[nm][k++] = (int)v; if (v > amax) amax = (int)v; s = e; }
        if (k >= 2) km[nm++] = k;
    }
    fclose(fm);
    uint64_t lim = (uint64_t)sqrt((double)N + amax + 64) + 2;           // petits premiers jusqu'à √(N + amax)
    uint8_t *s0 = calloc(lim + 1, 1); uint32_t *P = malloc(sizeof(uint32_t) * (lim / 2 + 16)); size_t NP = 0;
    for (uint64_t i = 2; i <= lim; i++) { if (s0[i]) continue; P[NP++] = (uint32_t)i; for (uint64_t j = i * i; j <= lim; j += i) s0[j] = 1; }
    size_t nseg = (N + SEG) / SEG;
    long double *totC = calloc((size_t)nm * nseg, sizeof(long double)), *totW = calloc((size_t)nm * nseg, sizeof(long double));
    double *gC = calloc((size_t)nm * G, 8), *gW = calloc((size_t)nm * G, 8); int64_t *gseg = malloc(8 * G);
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        uint8_t *isp = malloc(SEG + amax + 8);
        double *c = malloc(8 * nm), *w = malloc(8 * nm);
        #pragma omp for schedule(dynamic, 4)
        for (size_t sg = 0; sg < nseg; sg++) {
            uint64_t lo = (uint64_t)sg * SEG, hi = lo + SEG; if (hi > N + 1) hi = N + 1;
            uint64_t len = hi - lo + amax + 1;
            memset(isp, 1, len);
            if (lo == 0) { isp[0] = 0; isp[1] = 0; }
            for (size_t i = 0; i < NP; i++) {
                uint64_t p = P[i], st = p * p; if (st >= lo + len) break;
                if (st < lo) st = ((lo + p - 1) / p) * p;
                for (uint64_t m = st; m < lo + len; m += p) isp[m - lo] = 0;
            }
            size_t a = 0, b = G; while (a < b) { size_t m = (a + b) / 2; if ((uint64_t)X[m] < lo) a = m + 1; else b = m; }
            size_t j = a; for (int h = 0; h < nm; h++) { c[h] = 0; w[h] = 0; }
            for (uint64_t n = lo; n < hi; n++) {
                if (!isp[n - lo]) continue;
                while (j < G && (uint64_t)X[j] < n) { for (int h = 0; h < nm; h++) { gC[(size_t)nm * j + h] = c[h]; gW[(size_t)nm * j + h] = w[h]; } gseg[j] = sg; j++; }
                double ln0 = log((double)n);
                for (int h = 0; h < nm; h++) {
                    int ok = 1; for (int i = 1; i < km[h]; i++) if (!isp[n - lo + am[h][i]]) { ok = 0; break; }
                    if (!ok) continue;
                    double pr = ln0; for (int i = 1; i < km[h]; i++) pr *= log((double)n + am[h][i]);
                    c[h] += 1; w[h] += pr;
                }
            }
            while (j < G && (uint64_t)X[j] < hi) { for (int h = 0; h < nm; h++) { gC[(size_t)nm * j + h] = c[h]; gW[(size_t)nm * j + h] = w[h]; } gseg[j] = sg; j++; }
            for (int h = 0; h < nm; h++) { totC[(size_t)nm * sg + h] = c[h]; totW[(size_t)nm * sg + h] = w[h]; }
        }
        free(isp); free(c); free(w);
    }
    long double *pc = calloc(nm, sizeof(long double)), *pw = calloc(nm, sizeof(long double));
    long double *preC = malloc(sizeof(long double) * nm * (nseg + 1)), *preW = malloc(sizeof(long double) * nm * (nseg + 1));
    for (int h = 0; h < nm; h++) { preC[h] = 0; preW[h] = 0; }
    for (size_t s = 0; s < nseg; s++) for (int h = 0; h < nm; h++) {
        preC[(size_t)nm * (s + 1) + h] = preC[(size_t)nm * s + h] + totC[(size_t)nm * s + h];
        preW[(size_t)nm * (s + 1) + h] = preW[(size_t)nm * s + h] + totW[(size_t)nm * s + h];
    }
    FILE *fo = fopen(argv[4], "wb");
    for (size_t j = 0; j < G; j++) for (int h = 0; h < nm; h++) {
        int64_t cc = (X[j] > (int64_t)N) ? -1 : (int64_t)(preC[(size_t)nm * gseg[j] + h] + gC[(size_t)nm * j + h]);
        double ww = (X[j] > (int64_t)N) ? NAN : (double)(preW[(size_t)nm * gseg[j] + h] + (long double)gW[(size_t)nm * j + h]);
        fwrite(&cc, 8, 1, fo); fwrite(&ww, 8, 1, fo);
    }
    fclose(fo);
    fprintf(stderr, "fini : %d motifs, %zu segments, %.0f s ; totaux :", nm, nseg, omp_get_wtime() - t0);
    for (int h = 0; h < nm && h < 6; h++) fprintf(stderr, " %.0Lf", preC[(size_t)nm * nseg + h]);
    fprintf(stderr, " …\n");
    free(pc); free(pw);
    return 0;
}
