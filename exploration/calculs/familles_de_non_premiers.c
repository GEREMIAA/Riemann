/* Les non-premiers, rangés par nombre de facteurs premiers.
 *
 * Un nombre premier n'a qu'un facteur premier : lui-même. On range tous les entiers par leur nombre Ω(n) de facteurs
 * premiers, comptés avec répétition : Ω(1) = 0 ; Ω = 1 : les nombres premiers ; Ω = 2 : les produits de deux premiers
 * (4, 6, 9, 10, 14, 15…) ; Ω = 3 : 8, 12, 18, 20, 27… ; etc. Les non-premiers sont les familles Ω ≥ 2.
 * Le programme crible Ω(n) pour tous les n ≤ N (crible par segments : pour chaque puissance p^j d'un premier p ≤ √N,
 * on ajoute 1 à ses multiples ; le cofacteur restant, s'il dépasse 1, est un grand nombre premier). Il écrit, à chaque
 * puissance de 10 :
 *   - le nombre d'entiers de chaque famille ;
 *   - la somme de Liouville L(x) = Σ (−1)^Ω(n) (familles paires moins familles impaires), dont l'hypothèse de Riemann
 *     dit qu'elle reste de l'ordre de √x ;
 *   - le « poids » Σ 1/n² de chaque famille, à comparer aux fonctions zêta des familles calculées par
 *     zeta_des_non_premiers.py (P_1(2) = P(2) = 0,4522474…, P_2(2) = (P(2)² + P(4))/2, …).
 * Usage : ./familles_de_non_premiers 1000000000 > familles.txt        (une demi-minute pour 10⁹)
 * Compilation : gcc -O3 -march=native -o familles_de_non_premiers familles_de_non_premiers.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define KMAX 40
int main(int argc, char **argv) {
    uint64_t N = argc > 1 ? strtoull(argv[1], 0, 10) : 1000000;
    uint64_t R = (uint64_t)sqrtl((long double)N) + 2;
    char *bs = calloc(R + 1, 1); uint32_t *pr = malloc(sizeof(uint32_t) * (R / 2 + 10)); int np = 0;
    for (uint64_t i = 2; i <= R; i++) if (!bs[i]) { pr[np++] = (uint32_t)i; for (uint64_t j = i * i; j <= R; j += i) bs[j] = 1; }
    const uint64_t S = 1u << 18;
    uint8_t *om = malloc(S); uint64_t *reste = malloc(sizeof(uint64_t) * S);
    uint64_t compte[KMAX + 1] = {0}; long double poids[KMAX + 1] = {0}; int64_t L = 0;
    uint64_t prochain = 10;
    for (uint64_t lo = 1; lo <= N; lo += S) {
        uint64_t hi = lo + S - 1; if (hi > N) hi = N;
        uint64_t len = hi - lo + 1;
        memset(om, 0, len);
        for (uint64_t i = 0; i < len; i++) reste[i] = lo + i;
        for (int k = 0; k < np; k++) {
            uint64_t p = pr[k];
            if (p * p > hi) break;
            for (uint64_t q = p; q <= hi; q *= p) {
                uint64_t m = ((lo + q - 1) / q) * q;
                for (; m <= hi; m += q) { om[m - lo]++; reste[m - lo] /= p; }
                if (q > hi / p) break;
            }
        }
        for (uint64_t i = 0; i < len; i++) {
            uint64_t n = lo + i; int o = om[i] + (reste[i] > 1);
            compte[o]++; L += (o & 1) ? -1 : 1;
            poids[o] += 1.0L / ((long double)n * (long double)n);
            if (n == prochain || n == N) {
                printf("x %llu L %lld", (unsigned long long)n, (long long)L);
                for (int j = 0; j <= KMAX; j++) if (compte[j]) printf(" %d:%llu:%.15Lf", j, (unsigned long long)compte[j], poids[j]);
                printf("\n");
                if (n == prochain) prochain *= 10;
            }
        }
    }
    return 0;
}
