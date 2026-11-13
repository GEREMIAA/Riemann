/* Nicolas, premier après premier.
 *
 * Nicolas (1983) : l'hypothèse de Riemann équivaut à
 *      N_k / φ(N_k) > e^γ · ln ln N_k   pour tout k,
 * où N_k = 2·3·5·…·p_k est le produit des k premiers nombres premiers (une « primorielle ») et φ l'indicatrice d'Euler.
 * En logarithmes, avec θ(x) = Σ_{p ≤ x} ln p (donc ln N_k = θ(p_k)), c'est F(p_k) > 0, où
 *      F(p_k) = Σ_{p ≤ p_k} −ln(1 − 1/p) − γ − ln ln θ(p_k).
 * C'est exactement la forme « vrai au rang k, donc vrai au rang k + 1 ? » : chaque nouveau nombre premier est une marche.
 * Le programme crible tous les nombres premiers jusqu'à X (crible d'Ératosthène par segments), et suit F premier après
 * premier, en long double avec sommation compensée (Kahan). À chaque marche, il teste le signe de ΔF : une condition
 * suffisante simple (p − θ > 3 + 1,5 ln p, pour p ≥ 10⁶) garantit ΔF < 0 ; sinon, ΔF est calculé exactement.
 * Il écrit, à des points de contrôle répartis en échelle logarithmique : x, le dernier premier p ≤ x, π(x), θ(x),
 * A(x) = Σ −ln(1 − 1/p), B(x) = Σ ln(1 + 1/p) (pour le critère de Robin), F, G = F·√p·ln p, le min et le max de G
 * depuis le point précédent, le nombre de marches où F a augmenté, et le nombre de marches vérifiées exactement.
 * Usage : ./nicolas_premier_apres_premier 100000000000 > nicolas.txt      (environ dix minutes pour X = 10¹¹)
 * Compilation : gcc -O3 -march=native -o nicolas_premier_apres_premier nicolas_premier_apres_premier.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef long double LD;
static const LD GAMMA = 0.577215664901532860606512090082402431L;

static LD th, thc, A, Ac, B, Bc, Gmin = 1e30L, Gmax = -1e30L;
static uint64_t npi, nup, nexact, lastp;
static double *cps; static int ncp, icp;

static inline void kadd(LD *s, LD *c, LD v) { LD y = v - *c; LD t = *s + y; *c = (t - *s) - y; *s = t; }

static void sortie(double x) {
    LD F = (th > 1.0L) ? A - GAMMA - logl(logl(th)) : 0.0L;
    LD G = (lastp > 2) ? F * sqrtl((LD)lastp) * logl((LD)lastp) : 0.0L;
    printf("%.17g %llu %llu %.21Lg %.21Lg %.21Lg %.21Lg %.15Lg %.15Lg %.15Lg %llu %llu\n", x, (unsigned long long)lastp,
           (unsigned long long)npi, th, A, B, F, G, Gmin, Gmax, (unsigned long long)nup, (unsigned long long)nexact);
    Gmin = 1e30L; Gmax = -1e30L;
}

static inline void premier(uint64_t p) {
    while (icp < ncp && (double)p > cps[icp]) { sortie(cps[icp]); icp++; }
    LD lp = logl((LD)p), u = 1.0L / (LD)p;
    if (npi >= 2) {                                          /* la marche de p_k à p : signe de ΔF */
        if (p < 1000000 || !((LD)p - th > 3.0L + 1.5L * lp)) {
            nexact++;
            LD dF = -log1pl(-u) - log1pl(log1pl(lp / th) / logl(th));
            if (dF > 0) nup++;
        }
    }
    kadd(&th, &thc, lp);
    LD a, b;
    if (p < 1000000) { a = -log1pl(-u); b = log1pl(u); }
    else { LD u2 = u * u; a = u + u2 * (0.5L + u * (1.0L / 3.0L + u * 0.25L)); b = u - u2 * (0.5L - u * (1.0L / 3.0L - u * 0.25L)); }
    kadd(&A, &Ac, a); kadd(&B, &Bc, b);
    npi++; lastp = p;
    if (npi >= 2 && (p < 100000 || (npi & 7) == 0)) {
        LD F = A - GAMMA - logl(logl(th)), G = F * sqrtl((LD)p) * lp;
        if (G < Gmin) Gmin = G;
        if (G > Gmax) Gmax = G;
    }
}

int main(int argc, char **argv) {
    uint64_t X = strtoull(argv[1], 0, 10); int par_decade = argc > 2 ? atoi(argv[2]) : 400;
    cps = malloc(sizeof(double) * 100000);
    for (int j = 0;; j++) {
        double x = pow(10.0, 2.0 + (double)j / par_decade);
        if (x > (double)X * (1 + 1e-12)) break;
        cps[ncp++] = x;
    }
    if (cps[ncp - 1] < (double)X) cps[ncp++] = (double)X;
    uint64_t R = (uint64_t)sqrtl((LD)X) + 2;
    char *bs = calloc(R + 1, 1); uint64_t *bp = malloc(sizeof(uint64_t) * (R / 2 + 10)); int nbp = 0;
    for (uint64_t i = 2; i <= R; i++) if (!bs[i]) { if (i > 2) bp[nbp++] = i; for (uint64_t j = i * i; j <= R; j += i) bs[j] = 1; }
    premier(2);
    const uint64_t S = 1u << 22;                             /* nombres impairs par segment : n = 2i + 1 */
    unsigned char *seg = malloc(S); uint64_t *nxt = malloc(sizeof(uint64_t) * nbp);
    for (int k = 0; k < nbp; k++) nxt[k] = (bp[k] * bp[k] - 1) / 2;
    for (uint64_t lo = 1;; lo += S) {
        if (2 * lo + 1 > X) break;
        uint64_t hi = lo + S, nmax = 2 * (hi - 1) + 1;
        memset(seg, 0, S);
        for (int k = 0; k < nbp; k++) {
            uint64_t q = bp[k];
            if (q * q > nmax) break;
            uint64_t j = nxt[k];
            for (; j < hi; j += q) seg[j - lo] = 1;
            nxt[k] = j;
        }
        for (uint64_t i = lo; i < hi; i++)
            if (!seg[i - lo]) { uint64_t n = 2 * i + 1; if (n > X) break; premier(n); }
    }
    while (icp < ncp) { sortie(cps[icp]); icp++; }
    fprintf(stderr, "X = %llu : %llu nombres premiers ; marches où F augmente : %llu ; marches vérifiées exactement : %llu\n",
            (unsigned long long)X, (unsigned long long)npi, (unsigned long long)nup, (unsigned long long)nexact);
    return 0;
}
