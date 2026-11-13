// Points d'une courbe hyperelliptique y² = f(x) sur le corps fini à q = p^n éléments (p premier impair).
//   S = Σ_{x ∈ F_q} χ(f(x)),  χ = caractère quadratique de F_q ;  si deg f est impair, N_n = q + 1 + S
//   (q + S points affines, plus un point à l'infini), et a_n = q + 1 − N_n = −S.
// Le corps F_q est construit comme F_p[X]/(m) avec m primitif ; on calcule dans le « domaine des logarithmes » :
// un élément non nul est g^k (g = classe de X), la multiplication additionne les k, l'addition passe par la table
// de Zech Z(k) = log(1 + g^k). Un élément est un carré si et seulement si son logarithme est pair.
// Compilation : gcc -O3 -march=native -fopenmp courbes_rapide.c -o courbes_rapide
// Usage : ./courbes_rapide p n c0 c1 ... cd        (f = c0 + c1 x + … + cd x^d ; coefficients entre 0 et p − 1)
// Sortie : « p n q S »                              (quelques secondes pour q ≈ 10⁷)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static int p, n;
static int64_t q;

// polynômes de degré < n à coefficients dans F_p : tableaux de n entiers
static void mulmod(const int *a, const int *b, const int *m, int *r) {      // r = a·b mod m (m unitaire de degré n)
    int t[64] = {0};
    for (int i = 0; i < n; i++) if (a[i]) for (int j = 0; j < n; j++) t[i + j] = (t[i + j] + a[i] * b[j]) % p;
    for (int k = 2 * n - 2; k >= n; k--) if (t[k]) {
        int c = t[k]; t[k] = 0;
        for (int i = 0; i < n; i++) t[k - n + i] = ((t[k - n + i] - c * m[i]) % p + p) % p;
    }
    memcpy(r, t, n * sizeof(int));
}
static void powmod(const int *a, int64_t e, const int *m, int *r) {
    int base[64], res[64] = {0}; memcpy(base, a, n * sizeof(int)); res[0] = 1;
    while (e > 0) { if (e & 1) mulmod(res, base, m, res); mulmod(base, base, m, base); e >>= 1; }
    memcpy(r, res, n * sizeof(int));
}
static int est_un(const int *a) { if (a[0] != 1) return 0; for (int i = 1; i < n; i++) if (a[i]) return 0; return 1; }

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage : %s p n c0 c1 ... cd\n", argv[0]); return 1; }
    p = atoi(argv[1]); n = atoi(argv[2]); int d = argc - 4; int c[64];
    for (int i = 0; i <= d; i++) c[i] = ((atoi(argv[3 + i]) % p) + p) % p;
    q = 1; for (int i = 0; i < n; i++) q *= p;
    int64_t Q1 = q - 1;
    // facteurs premiers de q − 1
    int64_t fac[64]; int nf = 0; int64_t t = Q1;
    for (int64_t r = 2; r * r <= t; r++) if (t % r == 0) { fac[nf++] = r; while (t % r == 0) t /= r; }
    if (t > 1) fac[nf++] = t;
    // recherche d'un polynôme primitif m (X d'ordre exactement q − 1), de façon déterministe
    int m[64], X[64], w[64]; uint64_t etat = 88172645463325252ULL;
    for (;;) {
        for (int i = 0; i < n; i++) { etat ^= etat << 13; etat ^= etat >> 7; etat ^= etat << 17; m[i] = etat % p; }
        if (m[0] == 0) continue;
        memset(X, 0, sizeof X); if (n == 1) { X[0] = ((-m[0]) % p + p) % p; } else X[1] = 1;   // classe de X
        powmod(X, Q1, m, w); if (!est_un(w)) continue;
        int ok = 1; for (int i = 0; i < nf && ok; i++) { powmod(X, Q1 / fac[i], m, w); if (est_un(w)) ok = 0; }
        if (ok) break;
    }
    // tables : antilog[k] = indice de g^k (indice = Σ chiffre_i p^i), log[indice]
    int32_t *lg = malloc(sizeof(int32_t) * q), *zech = malloc(sizeof(int32_t) * Q1);
    int64_t *al = malloc(sizeof(int64_t) * Q1);
    int cur[64] = {0}; cur[0] = 1;
    for (int64_t k = 0; k < Q1; k++) {
        int64_t idx = 0; for (int i = n - 1; i >= 0; i--) idx = idx * p + cur[i];
        al[k] = idx; lg[idx] = (int32_t)k;
        mulmod(cur, X, m, cur);
    }
    lg[0] = -1;
    for (int64_t k = 0; k < Q1; k++) {                                    // Zech : 1 + g^k
        int64_t idx = al[k]; int d0 = idx % p; int64_t j = idx - d0 + (d0 + 1) % p;
        zech[k] = (j == 0) ? -1 : lg[j];
    }
    free(al);
    int32_t lc[64]; for (int i = 0; i <= d; i++) lc[i] = (c[i] == 0) ? -1 : lg[c[i]];   // constantes de F_p dans F_q
    int64_t S = 0;
    #pragma omp parallel for reduction(+:S) schedule(static)
    for (int64_t e = -1; e < Q1; e++) {                                   // e = −1 : x = 0 ; sinon x = g^e
        int64_t acc = lc[d];
        for (int i = d - 1; i >= 0; i--) {
            if (acc >= 0) acc = (e < 0) ? -1 : (acc + e) % Q1;               // acc · x
            if (lc[i] >= 0) {                                                // acc + c_i
                if (acc < 0) acc = lc[i];
                else { int64_t df = ((int64_t)lc[i] - acc) % Q1; if (df < 0) df += Q1; int32_t z = zech[df]; acc = (z < 0) ? -1 : (acc + z) % Q1; }
            }
        }
        if (acc >= 0) S += (acc % 2 == 0) ? 1 : -1;
    }
    printf("%d %d %lld %lld\n", p, n, (long long)q, (long long)S);
    free(lg); free(zech);
    return 0;
}
