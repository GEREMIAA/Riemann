// sentinelle.c : le zéro de la dérivée ζ′ attaché à une paire de zéros de ζ très serrée, en quadruple précision.
//
// Entre deux zéros voisins de ζ sur la droite critique, la dérivée ζ′ a un zéro juste à droite de la droite : la
// « sentinelle ». Plus la paire est serrée, plus elle est près de la droite ; si la paire fusionnait puis quittait la
// droite, elle passerait à gauche (critère de Speiser, 1934). Pour une paire d'écart δ à la hauteur t, le modèle à deux
// zéros donne une distance L·δ²/16, avec L = ln(t/2π).
//
// Ici on la calcule directement : ζ, ζ′ et ζ″ par la formule d'Euler–Maclaurin, somme directe de N ≈ t/2 termes
// (aucune formule asymptotique en t), en quadruple précision (113 bits), puis la méthode de Newton
//   - sur ζ, dans le plan complexe, pour chacun des deux zéros : leur partie réelle doit retomber sur ½ ;
//   - sur ζ′, pour la sentinelle.
//
// Compilation : gcc -O2 -fopenmp -o sentinelle sentinelle.c -lquadmath -lm
// Usage       : ./sentinelle gamma1 gamma2        (deux valeurs approchées des zéros de la paire)
// Sortie      : calculs/sentinelle.txt
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <quadmath.h>
#include <omp.h>

typedef __float128 Q;
typedef __complex128 C;
#define MB 30                                    // nombre de termes de Bernoulli
static Q cb[MB + 1];                             // cb[k] = B_2k / (2k)!
static const char *fq(Q x, const char *fmt) { static char b[8][96]; static int i = 0; i = (i + 1) % 8; quadmath_snprintf(b[i], 96, fmt, x); return b[i]; }

static void bernoulli(void) {                    // B_2k/(2k)! = 2 (−1)^(k+1) ζ(2k) / (2π)^(2k)
    Q pi = M_PIq, p2 = 4 * pi * pi, pw = 1;
    for (int k = 1; k <= MB; k++) {
        Q z;
        if (k == 1) z = pi * pi / 6; else if (k == 2) z = powq(pi, 4) / 90; else if (k == 3) z = powq(pi, 6) / 945;
        else { int M = 20000; z = 0; for (int n = M; n >= 1; n--) z += powq((Q)n, -2 * k); z += powq((Q)M, 1 - 2 * k) / (2 * k - 1) - powq((Q)M, -2 * k) / 2; }
        pw *= p2; cb[k] = ((k & 1) ? 2 : -2) * z / pw;
    }
}

// ζ(s), ζ′(s), ζ″(s) ; N termes en somme directe, puis la correction d'Euler–Maclaurin
static void zeta3(C s, long N, C *z0, C *z1, C *z2) {
    Q sig = crealq(s), t = cimagq(s);
    int nt = omp_get_max_threads();
    Q *acc = calloc(6 * nt, sizeof(Q));
    #pragma omp parallel
    {
        Q a0r = 0, a0i = 0, a1r = 0, a1i = 0, a2r = 0, a2i = 0;
        #pragma omp for schedule(static)
        for (long n = 2; n < N; n++) {
            Q l = logq((Q)n), m = expq(-sig * l), si, co; sincosq(-t * l, &si, &co);
            Q re = m * co, im = m * si;
            a0r += re; a0i += im; a1r -= l * re; a1i -= l * im; a2r += l * l * re; a2i += l * l * im;
        }
        int id = omp_get_thread_num();
        acc[6 * id] = a0r; acc[6 * id + 1] = a0i; acc[6 * id + 2] = a1r; acc[6 * id + 3] = a1i; acc[6 * id + 4] = a2r; acc[6 * id + 5] = a2i;
    }
    C S0 = 1, S1 = 0, S2 = 0;
    for (int i = 0; i < nt; i++) { S0 += acc[6 * i] + acc[6 * i + 1] * 1.0Qi; S1 += acc[6 * i + 2] + acc[6 * i + 3] * 1.0Qi; S2 += acc[6 * i + 4] + acc[6 * i + 5] * 1.0Qi; }
    free(acc);
    Q lN = logq((Q)N);
    C Ns = cexpq(-s * lN);                                           // N^(−s)
    C A = N * Ns / (s - 1), dA = -lN - 1 / (s - 1);                  // N^(1−s)/(s−1) et sa dérivée logarithmique
    S0 += A; S1 += A * dA; S2 += A * (dA * dA + 1 / ((s - 1) * (s - 1)));
    S0 += Ns / 2; S1 -= lN * Ns / 2; S2 += lN * lN * Ns / 2;
    C P = s, D = 1 / s - lN, D1 = -1 / (s * s), pw = Ns / N;         // P_k(s) = s(s+1)…(s+2k−2) ; pw = N^(−s−2k+1)
    for (int k = 1; k <= MB; k++) {
        C T = cb[k] * P * pw;
        S0 += T; S1 += T * D; S2 += T * (D * D + D1);
        C u = s + (2 * k - 1), v = s + 2 * k;
        P *= u * v; D += 1 / u + 1 / v; D1 -= 1 / (u * u) + 1 / (v * v); pw /= (Q)N * N;
    }
    *z0 = S0; *z1 = S1; *z2 = S2;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage : %s gamma1 gamma2\n", argv[0]); return 1; }
    Q g1 = strtoflt128(argv[1], NULL), g2 = strtoflt128(argv[2], NULL), tm = (g1 + g2) / 2;
    long N = (long)(tm / 2) + 20;
    bernoulli();
    C z0, z1, z2, rho[2];
    double t0 = omp_get_wtime();
    for (int j = 0; j < 2; j++) {                                    // les deux zéros de la paire : Newton sur ζ
        C s = 0.5Q + (j ? g2 : g1) * 1.0Qi;
        for (int it = 0; it < 8; it++) { zeta3(s, N, &z0, &z1, &z2); C pas = z0 / z1; s -= pas; if (cabsq(pas) < 1e-27Q) break; }
        rho[j] = s;
    }
    Q d = cimagq(rho[1]) - cimagq(rho[0]), L = logq(tm / (2 * M_PIq)), loi = L * d * d / 16;
    Q u = L * L * d * d / 16, deux = 2 / L * (1 - sqrtq(1 - u));       // modèle à deux zéros, exact
    C s = 0.5Q + deux + (cimagq(rho[0]) + cimagq(rho[1])) / 2 * 1.0Qi;
    int it;
    for (it = 0; it < 12; it++) { zeta3(s, N, &z0, &z1, &z2); C pas = z1 / z2; s -= pas; if (cabsq(pas) < 1e-27Q) break; }   // la sentinelle : Newton sur ζ′
    zeta3(s, N, &z0, &z1, &z2);
    Q x = crealq(s) - 0.5Q;
    printf("paire à la hauteur %s (N = %ld termes, %.0f s)\n", fq(tm, "%.6Qf"), N, omp_get_wtime() - t0);
    printf("   zéro 1 : %s   partie réelle − ½ = %s\n", fq(cimagq(rho[0]), "%.18Qf"), fq(crealq(rho[0]) - 0.5Q, "%.1Qe"));
    printf("   zéro 2 : %s   partie réelle − ½ = %s\n", fq(cimagq(rho[1]), "%.18Qf"), fq(crealq(rho[1]) - 0.5Q, "%.1Qe"));
    printf("   écart δ = %s ; L = ln(t/2π) = %s ; écart rapporté à l'écart moyen = %s\n", fq(d, "%.12Qe"), fq(L, "%.6Qf"), fq(d * L / (2 * M_PIq), "%.6Qf"));
    printf("   sentinelle (zéro de ζ′) : partie réelle − ½ = %s ; hauteur = milieu de la paire %s ; |ζ′| = %s ; |ζ| = %s\n",
           fq(x, "%.10Qe"), fq(cimagq(s) - (cimagq(rho[0]) + cimagq(rho[1])) / 2, "%+.3Qe"), fq(cabsq(z1), "%.1Qe"), fq(cabsq(z0), "%.6Qe"));
    printf("   loi L·δ²/16 = %s (rapport %s) ; modèle à deux zéros = %s (rapport %s) ; marge du film δ²/2 = %s\n",
           fq(loi, "%.10Qe"), fq(x / loi, "%.6Qf"), fq(deux, "%.10Qe"), fq(x / deux, "%.6Qf"), fq(d * d / 2, "%.6Qe"));
    printf("@ %s %s %s %s %s %s\n", fq(tm, "%.9Qf"), fq(d, "%.12Qe"), fq(L, "%.9Qf"), fq(x, "%.12Qe"), fq(cabsq(z0), "%.6Qe"), fq(crealq(rho[0]) - 0.5Q, "%.1Qe"));
    return 0;
}
