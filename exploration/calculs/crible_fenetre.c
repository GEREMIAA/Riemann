// La petite correction locale de la méthode analytique : crible de la fenêtre [lo, hi] autour de x, et somme, sur les
// nombres premiers p de la fenêtre, de  1[p ≤ x] − K(ln p − ln x),  avec K(v) = ½ erfc(v / (√2 λ)) (la marche lissée).
// Le reste du compte des nombres premiers vient des zéros de ζ (pi_par_les_zeros.py).
// Compilation : gcc -O3 -march=native -fopenmp crible_fenetre.c -o crible_fenetre -lm
// Usage : ./crible_fenetre x lambda dL lo hi        (dL = ln x − L, la différence entre ln x exact et le L utilisé ailleurs)
// Sortie : « somme  nombre_de_premiers_≤_x  nombre_de_premiers_>_x » dans la fenêtre.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>

#define SEG (1u << 24)          // nombres impairs par segment

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage : %s x lambda dL lo hi\n", argv[0]); return 1; }
    uint64_t x = strtoull(argv[1], NULL, 10); long double lam = strtold(argv[2], NULL), dL = strtold(argv[3], NULL);
    uint64_t lo = strtoull(argv[4], NULL, 10), hi = strtoull(argv[5], NULL, 10);
    if (lo % 2 == 0) lo++;                                   // on ne regarde que les impairs (la fenêtre est loin de 2)
    uint64_t r = (uint64_t)sqrtl((long double)hi) + 2;
    uint8_t *pe = calloc(r + 1, 1); uint32_t *P = malloc(sizeof(uint32_t) * (r / 2 + 16)); size_t NP = 0;
    for (uint64_t i = 3; i <= r; i += 2) { if (pe[i]) continue; P[NP++] = (uint32_t)i; for (uint64_t j = i * i; j <= r; j += 2 * i) pe[j] = 1; }
    uint64_t nimp = (hi - lo) / 2 + 1, nseg = (nimp + SEG - 1) / SEG;
    long double total = 0; long long avant = 0, apres = 0;
    const long double s2l = sqrtl(2.0L) * lam; const long double xx = (long double)x;
    double t0 = omp_get_wtime();
    #pragma omp parallel reduction(+:total, avant, apres)
    {
        uint8_t *comp = malloc(SEG);
        #pragma omp for schedule(dynamic, 1)
        for (uint64_t sg = 0; sg < nseg; sg++) {
            uint64_t a = lo + 2 * (uint64_t)sg * SEG;                  // a impair ; le segment couvre a, a + 2, …
            uint64_t cnt = SEG; if (sg == nseg - 1) cnt = nimp - (uint64_t)sg * SEG;
            uint64_t b = a + 2 * (cnt - 1);
            memset(comp, 0, cnt);
            for (size_t i = 0; i < NP; i++) {
                uint64_t p = P[i], st = p * p; if (st > b) break;
                if (st < a) { st = ((a + p - 1) / p) * p; if (st % 2 == 0) st += p; }
                for (uint64_t m = st; m <= b; m += 2 * p) comp[(m - a) / 2] = 1;
            }
            long double s = 0, c = 0;                                  // somme compensée (Kahan)
            for (uint64_t k = 0; k < cnt; k++) {
                if (comp[k]) continue;
                uint64_t n = a + 2 * k;
                long double v = log1pl(((long double)n - xx) / xx) + dL;   // ln n − L
                long double term = (n <= x) ? 0.5L * erfcl(-v / s2l) : -0.5L * erfcl(v / s2l);
                if (n <= x) avant++; else apres++;
                long double y = term - c, t = s + y; c = (t - s) - y; s = t;
            }
            total += s;
        }
        free(comp);
    }
    printf("%.12Lf %lld %lld\n", total, avant, apres);
    fprintf(stderr, "fenêtre de %llu nombres, %zu petits premiers, %.1f s\n", (unsigned long long)(hi - lo + 1), NP, omp_get_wtime() - t0);
    return 0;
}
