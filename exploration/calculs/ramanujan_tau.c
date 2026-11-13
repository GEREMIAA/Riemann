/* La fonction τ de Ramanujan : « vrai sur chaque premier ».
 *
 * Δ(q) = q·Π(1 − qⁿ)²⁴ = Σ τ(n) qⁿ : τ(1) = 1, τ(2) = −24, τ(3) = 252, τ(5) = 4 830…
 * Ramanujan (1916) a conjecturé |τ(p)| ≤ 2·p^(11/2) pour tout nombre premier p ; Deligne l'a démontré en 1974, comme
 * conséquence de l'hypothèse de Riemann pour les variétés sur les corps finis : c'est une hypothèse de Riemann « locale »,
 * nombre premier par nombre premier (les racines de 1 − τ(p)X + p¹¹X² ont le même module p^(−11/2)).
 * Pour les non-premiers, la même borne est fausse en général ; la bonne est |τ(n)| ≤ d(n)·n^(11/2), qui découle des
 * premiers par multiplicativité. Et l'hypothèse de Riemann « globale » pour la fonction L(s, Δ) reste ouverte.
 *
 * Calcul exact de τ(p) par la formule de Niebur (1975) :
 *      τ(n) = n⁴σ(n) − 24 Σ_{k=1}^{n−1} (35k⁴ − 52k³n + 18k²n²) σ(k) σ(n − k),
 * en entiers de 128 bits (sans débordement jusqu'à n = 100 000). On contrôle la formule sur des valeurs connues et sur
 * la multiplicativité (τ(6) = τ(2)τ(3), τ(4) = τ(2)² − 2¹¹).
 * Usage : ./ramanujan_tau 100000 > tau_premiers.txt        (lignes : p, τ(p), τ(p)/(2p^(11/2)))
 * Compilation : gcc -O2 -o ramanujan_tau ramanujan_tau.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
typedef __int128 I128;

static int64_t *sig;
static I128 tau(int64_t n) {
    I128 s = 0;
    for (int64_t k = 1; k < n; k++) {
        I128 c = (I128)k * k * (35 * (I128)k * k - 52 * (I128)k * n + 18 * (I128)n * n);
        s += c * ((I128)sig[k] * sig[n - k]);
    }
    return (I128)n * n * n * n * sig[n] - 24 * s;
}
static void ecrire(I128 v, char *buf) {
    char t[64]; int i = 0, neg = v < 0; unsigned __int128 u = neg ? -(unsigned __int128)v : (unsigned __int128)v;
    do { t[i++] = '0' + (int)(u % 10); u /= 10; } while (u);
    int j = 0; if (neg) buf[j++] = '-';
    while (i) buf[j++] = t[--i];
    buf[j] = 0;
}
int main(int argc, char **argv) {
    int64_t N = argc > 1 ? atoll(argv[1]) : 1000;
    sig = calloc(N + 1, sizeof(int64_t));
    for (int64_t d = 1; d <= N; d++) for (int64_t m = d; m <= N; m += d) sig[m] += d;
    /* contrôles */
    int64_t connus[][2] = {{1, 1}, {2, -24}, {3, 252}, {4, -1472}, {5, 4830}, {6, -6048}, {7, -16744}, {11, 534612}, {13, -577738}};
    for (int i = 0; i < 9; i++) if (N >= connus[i][0] && tau(connus[i][0]) != (I128)connus[i][1]) { fprintf(stderr, "ÉCHEC n = %lld\n", (long long)connus[i][0]); return 1; }
    if (N >= 12 && tau(12) != tau(3) * tau(4)) { fprintf(stderr, "ÉCHEC multiplicativité\n"); return 1; }
    fprintf(stderr, "contrôles : valeurs connues et multiplicativité, ok\n");
    char *crible = calloc(N + 1, 1); char buf[64];
    for (int64_t p = 2; p <= N; p++) {
        if (crible[p]) continue;
        for (int64_t m = p * p; m <= N; m += p) crible[m] = 1;
        I128 t = tau(p); ecrire(t, buf);
        double x = (double)t / (2.0 * pow((double)p, 5.5));
        printf("%lld %s %.15f\n", (long long)p, buf, x);
    }
    return 0;
}
