/* Le crible d'Ératosthène, avec et sans retenue.
 *
 * Un entier s'écrit en binaire : 13 = 1101. La même suite de 0 et de 1 est aussi un polynôme à coefficients 0 ou 1 :
 * 1101 = x³ + x² + 1. Ces polynômes s'additionnent et se multiplient comme les entiers écrits en binaire, mais SANS
 * RETENUE : 1 + 1 = 0, rien ne passe à la colonne suivante (l'addition est le « ou exclusif », noté ^ en C).
 * Exemple : 11 ⊗ 11 = 101, c'est-à-dire 3 ⊗ 3 = 5 ; avec retenue, 3 × 3 = 9.
 * Dans ce monde aussi, tout nombre se décompose d'une seule façon en « nombres premiers » (les polynômes irréductibles
 * sur le corps à deux éléments) : 2, 3, 7, 11, 13, 19, 25, 31, 37, 41, 47, 55, 59, 61… Et on les compte exactement :
 * il y en a (1/n) Σ_{d|n} μ(d) 2^(n/d) parmi les nombres de n+1 chiffres binaires (Gauss).
 *
 * Le programme crible les deux mondes à la fois, sur les mêmes tranches de 2^L nombres, jusqu'à 2^NMAX :
 *   - le crible ordinaire (multiples de p, avec retenue) ;
 *   - le crible sans retenue : les multiples d'un premier P, dans la tranche H·2^L + r, sont les r = r0 ^ (P ⊗ q),
 *     où r0 = (H·x^L) mod P ; on les parcourt par un code de Gray, un « ou exclusif » par multiple.
 *     La roue : tout premier sans retenue autre que 10 et 11 est impair et a un nombre impair de chiffres 1
 *     (sinon il serait divisible par x ou par x+1) ; on ne garde donc qu'un nombre sur quatre.
 * Pour chaque « bloc » n (les nombres de n+1 chiffres binaires, de 2^n à 2^(n+1) − 1), il écrit une ligne :
 *   n  A  I  B  Aimp  A2  J  I3[0..2]  I7[0..6]  theta
 *   A     nombres premiers ordinaires du bloc
 *   I     premiers sans retenue du bloc                      (doit valoir la formule de Gauss)
 *   B     nombres premiers dans les deux mondes à la fois
 *   Aimp  nombres premiers ordinaires ayant un nombre impair de chiffres 1 (non divisibles par 11 sans retenue)
 *   A2    parmi eux, ceux qui ne sont pas non plus divisibles par 111 sans retenue
 *   J     paires de premiers sans retenue « jumeaux » : P et P ^ 110
 *   I3[r] premiers sans retenue qui, lus comme entiers, valent r modulo 3 ; I7[r] : modulo 7
 *   theta somme des ln p sur les nombres premiers ordinaires du bloc
 * Usage : ./sans_retenue 40 > sans_retenue_2e40.txt      (deux cœurs : un quart d'heure ; 36 : une minute)
 * Compilation : gcc -O3 -march=native -fopenmp -o sans_retenue sans_retenue.c -lm
 * Vérification : gcc -O3 -march=native -fopenmp -DL=16 … puis comparer à sans_retenue_naif.c pour NMAX = 26.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>
#include <immintrin.h>

#ifndef L
#define L 24                     /* taille d'une tranche : 2^L nombres */
#endif
typedef unsigned long long u64;
typedef struct { u64 A, I, B, Aimp, A2, J, I3[3], I7[7]; long double th; } stat_t;

static inline int par(u64 v) { return __builtin_popcountll(v) & 1; }
/* valeur du polynôme en ω (ω² + ω + 1 = 0), dans le corps à 4 éléments : 0 si et seulement si 111 le divise */
#define M0 0x9249249249249249ULL
static inline int fomega(u64 m) {
    int p0 = par(m & M0), p1 = par(m & (M0 << 1)), p2 = par(m & (M0 << 2));
    return (p0 ^ p2) | ((p1 ^ p2) << 1);
}
static inline int degre(u64 v) { return 63 - __builtin_clzll(v); }
/* (a ⊗ b) mod P, avec deg b < d = deg P */
static inline uint32_t mulmod(u64 a, uint32_t b, uint32_t P, int d) {
    uint32_t res = 0;
    for (int i = degre(a); i >= 0; i--) { res <<= 1; if ((res >> d) & 1) res ^= P; if ((a >> i) & 1) res ^= b; }
    return res;
}

int main(int argc, char **argv) {
    int NMAX = argc > 1 ? atoi(argv[1]) : 30;
    if (NMAX <= L) NMAX = L + 1;
    int DM = (NMAX - 1) / 2;                                   /* degré maximal des premiers sans retenue utiles */
    if (DM > L - 2 || NMAX > 62) { fprintf(stderr, "NMAX trop grand pour L = %d\n", L); return 1; }
    const u64 T = 1ULL << L;
    stat_t *tot = calloc(64, sizeof(stat_t));

    /* ------------------------------------------------ 1. les nombres en dessous de 2^L, par deux cribles simples */
    uint8_t *comp = calloc(T, 1), *irr = calloc(T, 1);        /* comp : non premier ; irr : premier sans retenue */
    comp[0] = comp[1] = 1;
    for (u64 p = 2; p * p < T; p++) if (!comp[p]) for (u64 m = p * p; m < T; m += p) comp[m] = 1;
    uint8_t *red = calloc(T, 1); red[0] = red[1] = 1;
    for (u64 P = 2; P < T; P++) {
        if (red[P]) continue;
        irr[P] = 1; int d = degre(P);
        if (2 * d > L - 1) continue;
        u64 m = 0, nq = 1ULL << (L - d);                       /* tous les P ⊗ q de degré < L, par code de Gray */
        for (u64 i = 1; i < nq; i++) { m ^= P << __builtin_ctzll(i); if (m != P) red[m] = 1; }
    }
    free(red);
    for (u64 m = 2; m < T; m++) {
        stat_t *s = &tot[degre(m)];
        int pr = !comp[m], ir = irr[m];
        if (pr) { s->A++; s->th += logl((long double)m); if (par(m)) { s->Aimp++; if (fomega(m)) s->A2++; } }
        if (ir) { s->I++; s->I3[m % 3]++; s->I7[m % 7]++; if (pr) s->B++; if (!(m & 4) && (m ^ 6) > 1 && irr[m ^ 6]) s->J++; }
    }
    /* ------------------------------------------------ 2. les tables de base */
    u64 racine = 1; while (racine * racine < (1ULL << NMAX)) racine++;
    uint32_t *bp = malloc(sizeof(uint32_t) * (racine / 2 + 16)); int nbp = 0;
    for (u64 p = 3; p <= racine; p++) if (!comp[p]) bp[nbp++] = (uint32_t)p;
    int nq = 0; for (u64 P = 4; P < (2ULL << DM); P++) if (irr[P]) nq++;
    uint32_t *bq = malloc(sizeof(uint32_t) * nq), *bxl = malloc(sizeof(uint32_t) * nq); int qfin[64] = {0}; nq = 0;
    for (u64 P = 4; P < (2ULL << DM); P++) if (irr[P]) {
        int d = degre(P); uint32_t v = 1;
        for (int i = 0; i < L; i++) { v <<= 1; if ((v >> d) & 1) v ^= (uint32_t)P; }      /* x^L mod P */
        bq[nq] = (uint32_t)P; bxl[nq] = v; nq++; qfin[d] = nq;
    }
    for (int d = 1; d < 64; d++) if (!qfin[d]) qfin[d] = qfin[d - 1];
    free(comp); free(irr);
    /* masques sur les 64 positions t d'un mot : le nombre est r = 4j + 2e + 1, j = 64J + t, e = c ^ tm(t) */
    u64 MLO[2] = {0, 0}, MHI[2] = {0, 0}, ZV[2][4], R3[2][3], R7[2][7];
    memset(ZV, 0, sizeof ZV); memset(R3, 0, sizeof R3); memset(R7, 0, sizeof R7);
    for (int c = 0; c < 2; c++) for (int t = 0; t < 64; t++) {
        int e = c ^ par(t);
        if (t < 32) MLO[c] |= 1ULL << (2 * t + e); else MHI[c] |= 1ULL << (2 * t + e - 64);
        ZV[c][fomega(((u64)t << 2) | ((u64)e << 1))] |= 1ULL << t;
        R3[c][(4 * t + 2 * e) % 3] |= 1ULL << t; R7[c][(4 * t + 2 * e) % 7] |= 1ULL << t;
    }
    /* ------------------------------------------------ 3. les tranches H·2^L + r, H ≥ 1 */
    const u64 NH = 1ULL << (NMAX - L), NWP = T >> 7, NWC = T >> 8;
    u64 faits = 0; double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        u64 *pb = malloc(8 * NWP), *cb = malloc(8 * NWC);
        stat_t *loc = calloc(64, sizeof(stat_t));
        #pragma omp for schedule(dynamic, 8)
        for (u64 H = 1; H < NH; H++) {
            int n = L + degre(H); u64 lo = H << L, hi = lo + T - 1; stat_t *s = &loc[n];
            /* (a) crible ordinaire, sur les impairs : bit i ↔ lo + 2i + 1 */
            memset(pb, 0xff, 8 * NWP);
            for (int k = 0; k < nbp; k++) {
                u64 p = bp[k]; if (p * p > hi) break;
                u64 st = ((lo + p - 1) / p) * p; if (st < p * p) st = p * p; if (!(st & 1)) st += p;
                for (u64 i = (st - lo) >> 1; i < (T >> 1); i += p) pb[i >> 6] &= ~(1ULL << (i & 63));
            }
            /* (b) crible sans retenue, sur les r impairs à nombre impair de 1 : bit j ↔ r = 4j + 2e + 1 */
            memset(cb, 0, 8 * NWC);
            int wH = par(H), qf = qfin[n / 2];
            for (int k = 0; k < qf; k++) {
                uint32_t P = bq[k]; int d = degre(P);
                u64 rb = mulmod(H, bxl[k], P, d);                     /* r ≡ H·x^L (mod P) */
                if (!(rb & 1)) rb ^= P;                                /* r impair */
                if (!((wH + __builtin_popcountll(rb)) & 1)) rb ^= (u64)P << 1;   /* nombre total de 1 impair */
                u64 G = (u64)P ^ ((u64)P << 1), cnt = 1ULL << (L - d - 2);       /* pas : P ⊗ 11, décalé */
                cb[rb >> 8] |= 1ULL << ((rb >> 2) & 63);
                for (u64 i = 1; i < cnt; i++) { rb ^= G << (1 + __builtin_ctzll(i)); cb[rb >> 8] |= 1ULL << ((rb >> 2) & 63); }
            }
            /* (c) les comptes */
            u64 A = 0, I = 0, B = 0, Ai = 0, A2 = 0, Jm = 0, i3[3] = {0, 0, 0}, i7[7] = {0, 0, 0, 0, 0, 0, 0}; long double th = 0;
            for (u64 Jw = 0; Jw < NWC; Jw++) {
                u64 surv = ~cb[Jw], W0 = pb[2 * Jw], W1 = pb[2 * Jw + 1], base = lo + (Jw << 8);
                int c = (wH + __builtin_popcountll(Jw)) & 1;
                u64 pg = _pext_u64(W0, MLO[c]) | (_pext_u64(W1, MHI[c]) << 32);  /* premiers ordinaires sur la grille */
                int na = __builtin_popcountll(W0) + __builtin_popcountll(W1);
                A += na; I += __builtin_popcountll(surv); Ai += __builtin_popcountll(pg); B += __builtin_popcountll(pg & surv);
                Jm += __builtin_popcountll(surv & (surv >> 1) & 0x5555555555555555ULL);
                A2 += __builtin_popcountll(pg & ~ZV[c][fomega(base + 1)]);
                int b3 = (int)((base + 1) % 3), b7 = (int)((base + 1) % 7);
                for (int r = 0; r < 3; r++) i3[(r + b3) % 3] += __builtin_popcountll(surv & R3[c][r]);
                for (int r = 0; r < 7; r++) i7[(r + b7) % 7] += __builtin_popcountll(surv & R7[c][r]);
                if (na) th += na * (long double)log((double)(base + 128));
            }
            s->A += A; s->I += I; s->B += B; s->Aimp += Ai; s->A2 += A2; s->J += Jm; s->th += th;
            for (int r = 0; r < 3; r++) s->I3[r] += i3[r];
            for (int r = 0; r < 7; r++) s->I7[r] += i7[r];
            #pragma omp critical
            { faits++; if ((faits & 1023) == 0) fprintf(stderr, "%llu / %llu tranches, %.0f s\n", faits, NH - 1, omp_get_wtime() - t0); }
        }
        #pragma omp critical
        for (int n = 0; n < 64; n++) {
            stat_t *a = &tot[n], *b = &loc[n];
            a->A += b->A; a->I += b->I; a->B += b->B; a->Aimp += b->Aimp; a->A2 += b->A2; a->J += b->J; a->th += b->th;
            for (int r = 0; r < 3; r++) a->I3[r] += b->I3[r];
            for (int r = 0; r < 7; r++) a->I7[r] += b->I7[r];
        }
        free(pb); free(cb); free(loc);
    }
    for (int n = 1; n < NMAX; n++) {
        stat_t *s = &tot[n];
        printf("%d %llu %llu %llu %llu %llu %llu", n, s->A, s->I, s->B, s->Aimp, s->A2, s->J);
        for (int r = 0; r < 3; r++) printf(" %llu", s->I3[r]);
        for (int r = 0; r < 7; r++) printf(" %llu", s->I7[r]);
        printf(" %.6Lf\n", s->th);
    }
    return 0;
}
