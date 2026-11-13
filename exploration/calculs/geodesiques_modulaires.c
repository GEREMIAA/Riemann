/* Les géodésiques fermées de la surface modulaire, comptées par leur trace.
 *
 * Une géodésique fermée primitive de la surface modulaire PSL(2,Z)\H correspond à une classe de conjugaison
 * hyperbolique primitive de PSL(2,Z), et chacune s'écrit, de façon unique à rotation près, comme un mot en
 *      L = (1 1 / 0 1)  et  R = (1 0 / 1 1)
 * contenant les deux lettres : les classes primitives sont exactement les mots de Lyndon en L et R — les mêmes mots
 * que les orbites périodiques du papillon de Lorenz (Ghys, 2007 : ce sont aussi les mêmes nœuds).
 * La longueur de la géodésique vaut 2 argch(t/2), où t est la trace de la matrice ; sa « norme » est
 * N = ((t + √(t² − 4))/2)².  Exemple : LR = (2 1 / 1 1), t = 3, N = ((3 + √5)/2)² = 6,854…
 *
 * Le programme parcourt l'arbre des pré-colliers (algorithme de Fredricksen–Kessler–Maiorana) en élaguant dès que
 * la trace dépasse X : la trace ne peut que croître quand on allonge un mot positif. Il écrit, pour chaque trace
 * t ≤ X, le nombre m(t) de mots de Lyndon (géodésiques primitives) de trace t.
 * Usage : ./geodesiques_modulaires 22000 > traces.txt          (quelques dizaines de secondes)
 * Compilation : gcc -O2 -o geodesiques_modulaires geodesiques_modulaires.c
 */
#include <stdio.h>
#include <stdlib.h>

static long X;
static long *m;
static unsigned char *mot;
static long long noeuds = 0;

static void parcours(long t, long p, long a, long b, long c, long d) {
    noeuds++;
    if (p == t && c > 0) m[a + d]++;                         /* mot de Lyndon contenant R : une géodésique primitive */
    long debut = mot[t + 1 - p];                             /* lettres permises : de mot[t+1−p] à 1 */
    for (long l = debut; l <= 1; l++) {
        long na, nb, nc, nd;
        if (l == 0) { na = a; nb = a + b; nc = c; nd = c + d; }       /* on ajoute L */
        else        { na = a + b; nb = b; nc = c + d; nd = d; }       /* on ajoute R */
        if (na + nd > X) continue;
        if (l == 0 && c == 0 && t + 3 > X) continue;         /* L^(t+1) : toute suite aurait une trace > X */
        mot[t + 1] = (unsigned char)l;
        parcours(t + 1, l == debut ? p : t + 1, na, nb, nc, nd);
    }
}

int main(int argc, char **argv) {
    X = argc > 1 ? atol(argv[1]) : 1000;
    m = calloc(X + 2, sizeof(long)); mot = calloc(X + 5, 1);
    mot[0] = 0; mot[1] = 0;                                  /* les mots commencent par L */
    parcours(1, 1, 1, 1, 0, 1);                              /* le mot « L » */
    long long total = 0;
    for (long t = 3; t <= X; t++) { printf("%ld %ld\n", t, m[t]); total += m[t]; }
    fprintf(stderr, "traces <= %ld : %lld géodésiques primitives ; %lld noeuds parcourus\n", X, total, noeuds);
    return 0;
}
