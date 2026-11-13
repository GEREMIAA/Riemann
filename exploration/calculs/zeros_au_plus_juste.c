/* Les zéros de ζ au plus juste : chercher la pièce mauvaise.
 *
 * Pour démontrer que l'hypothèse de Riemann est fausse, il suffit d'un seul zéro hors de la droite critique, et cela
 * se voit sur la droite elle-même. La fonction Z(t) de Hardy est réelle, et ses changements de signe sont les zéros
 * de ζ(½ + it). Si l'hypothèse est vraie, |Z| n'a aucun creux entre deux zéros : tout creux descend jusqu'à zéro.
 * Un creux qui s'arrêterait avant (un minimum positif, ou un maximum négatif) signifierait que deux zéros ont quitté
 * la droite : ce serait un contre-exemple.
 *
 * Le programme balaye Z(t) de t = 10 à T (formule de Riemann–Siegel, avec quatre termes correctifs), localise tous
 * les changements de signe, et examine chaque creux de |Z| de plus en plus finement (pas divisé par 16, 256, 4096)
 * jusqu'à trouver les deux zéros qu'il cache. Un creux qui résisterait serait signalé comme candidat contre-exemple.
 * Les creux sont repérés sur la grille, et entre ses points par interpolation au quart de pas.
 * Il contrôle aussi « l'appel » : le nombre de zéros trouvés doit suivre la formule N(t) = θ(t)/π + 1 + S(t), où
 * S(t) reste petit et de moyenne nulle ; une paire oubliée, ou partie hors de la droite, décalerait S de −2.
 * Si la moyenne de S sur un bloc s'écarte de zéro, le bloc est repris avec une grille deux fois plus fine.
 *
 * Calcul rapide : sur une tranche, on avance d'un pas fixe h ; chaque terme n^(−½) e^(−it ln n) de la somme tourne
 * d'un angle fixe h·ln n, donc une multiplication complexe par terme, sans cosinus. Les phases de départ de chaque
 * tranche sont calculées en précision étendue.
 *
 * Sortie (sur la sortie standard) : le bilan, puis la liste des paires les plus serrées (écart inférieur à 5 % de
 * l'écart moyen) : rang du premier zéro, les deux hauteurs, l'écart rapporté à l'écart moyen.
 * Usage : ./zeros_au_plus_juste 100000000 > zeros_au_plus_juste.txt        (deux cœurs : trois quarts d'heure ; 10⁷ : une minute)
 *         ./zeros_au_plus_juste -f 7005.0816 0.1 400                         (une fenêtre : t et Z(t), pour les figures)
 *         ./zeros_au_plus_juste -z 100000 zeros.bin                          (enregistre aussi tous les zéros, en binaire)
 * Compilation : gcc -O3 -march=native -fopenmp -o zeros_au_plus_juste zeros_au_plus_juste.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>

#define NT 4300                                   /* nombre maximal de termes √(T/2π) : T ≤ 1,1·10⁸ */
#define LC 400.0                                  /* longueur d'une tranche */
#define ZMAX 4096                                 /* zéros par tranche, au plus */
#define SEUIL 0.05
static const long double PI2L = 6.283185307179586476925286766559L;
static double LN[NT + 2], ISQ[NT + 2], LAG[3][6]; static long double LNL[NT + 2];
/* termes correctifs C0..C3 de Riemann–Siegel : séries de Taylor en q = p − ½ (calculées par zeros_precis.py) */
static const double RS0[43] = {3.82683432365089782e-01, 0.00000000000000000e+00, 1.74896187231008171e+00, 0.00000000000000000e+00, 2.11802520768549618e+00, 0.00000000000000000e+00, -8.70721667051148063e-01, 0.00000000000000000e+00, -3.47331122434651673e+00, 0.00000000000000000e+00, -1.66269473089993247e+00, 0.00000000000000000e+00, 1.21673128891923210e+00, 0.00000000000000000e+00, 1.30143041610079768e+00, 0.00000000000000000e+00, 3.05110218273616715e-02, 0.00000000000000000e+00, -3.75580305154509519e-01, 0.00000000000000000e+00, -1.08578441656406594e-01, 0.00000000000000000e+00, 5.18329029995496238e-02, 0.00000000000000000e+00, 2.99994806199022773e-02, 0.00000000000000000e+00, -2.27593967061256444e-03, 0.00000000000000000e+00, -4.38264741658033873e-03, 0.00000000000000000e+00, -4.06423018372984715e-04, 0.00000000000000000e+00, 4.00609778542211398e-04, 0.00000000000000000e+00, 8.97105799138884146e-05, 0.00000000000000000e+00, -2.30256500272391078e-05, 0.00000000000000000e+00, -9.38000660190679249e-06, 0.00000000000000000e+00, 6.32351494760910754e-07, 0.00000000000000000e+00, 6.55102281923150186e-07};
static const double RS1[44] = {-0.00000000000000000e+00, -5.36502052567506896e-02, -0.00000000000000000e+00, 1.10278187410814826e-01, -0.00000000000000000e+00, 1.23172001543152265e+00, -0.00000000000000000e+00, 1.26349648627994604e+00, -0.00000000000000000e+00, -1.69510899755950306e+00, -0.00000000000000000e+00, -2.99987119676501024e+00, -0.00000000000000000e+00, -1.08199449598992081e-01, -0.00000000000000000e+00, 1.94076629462127137e+00, -0.00000000000000000e+00, 7.83842356150068587e-01, -0.00000000000000000e+00, -5.05482966790036681e-01, -0.00000000000000000e+00, -3.84507234960579758e-01, -0.00000000000000000e+00, 3.74726464653153263e-02, -0.00000000000000000e+00, 9.09202661097317649e-02, -0.00000000000000000e+00, 1.04492375500645097e-02, -0.00000000000000000e+00, -1.25829796515834168e-02, -0.00000000000000000e+00, -3.39950372115127445e-03, -0.00000000000000000e+00, 1.04109505377148934e-03, -0.00000000000000000e+00, 5.01094905111848748e-04, -0.00000000000000000e+00, -3.95635966900318169e-05, -0.00000000000000000e+00, -4.76245924535719024e-05, -0.00000000000000000e+00, -1.85393553380851326e-06, -0.00000000000000000e+00, 3.19369180800689734e-06};
static const double RS2[45] = {5.18854283029316840e-03, 0.00000000000000000e+00, 1.23786335522537566e-03, 0.00000000000000000e+00, -1.81375057251669997e-01, 0.00000000000000000e+00, 1.42914927485321364e-01, 0.00000000000000000e+00, 1.33033917666875690e+00, 0.00000000000000000e+00, 3.52247235340373388e-01, 0.00000000000000000e+00, -2.42100159589195174e+00, 0.00000000000000000e+00, -1.67607870225381128e+00, 0.00000000000000000e+00, 1.36894167233283781e+00, 0.00000000000000000e+00, 1.55390194302229889e+00, 0.00000000000000000e+00, -1.72216427347299889e-01, 0.00000000000000000e+00, -6.35906805504543371e-01, 0.00000000000000000e+00, -9.91164987304121031e-02, 0.00000000000000000e+00, 1.40334800673870136e-01, 0.00000000000000000e+00, 4.78235201982729410e-02, 0.00000000000000000e+00, -1.73560406414797856e-02, 0.00000000000000000e+00, -1.02250125340285943e-02, 0.00000000000000000e+00, 9.27414915979489192e-04, 0.00000000000000000e+00, 1.35721943723733900e-03, 0.00000000000000000e+00, 6.41369012029388233e-05, 0.00000000000000000e+00, -1.23008056981966345e-04, 0.00000000000000000e+00, -1.83135074047892080e-05, 0.00000000000000000e+00, 7.82162860432262871e-06};
static const double RS3[46] = {-0.00000000000000000e+00, -2.67943218143891363e-03, -0.00000000000000000e+00, 2.99537210910351612e-02, -0.00000000000000000e+00, -4.25701725418287102e-02, -0.00000000000000000e+00, -2.89979657798038915e-01, -0.00000000000000000e+00, 4.88883199923544676e-01, -0.00000000000000000e+00, 1.23085587639574601e+00, -0.00000000000000000e+00, -8.29756070852740946e-01, -0.00000000000000000e+00, -2.24976353666656692e+00, -0.00000000000000000e+00, 7.84513996100547062e-02, -0.00000000000000000e+00, 1.74674928008688957e+00, -0.00000000000000000e+00, 4.59680809797499423e-01, -0.00000000000000000e+00, -6.61935347103977612e-01, -0.00000000000000000e+00, -3.15904410361736443e-01, -0.00000000000000000e+00, 1.28447925452074979e-01, -0.00000000000000000e+00, 1.00733827166261544e-01, -0.00000000000000000e+00, -9.53018384882526985e-03, -0.00000000000000000e+00, -1.92644216875140911e-02, -0.00000000000000000e+00, -1.24646371587692931e-03, -0.00000000000000000e+00, 2.42439696411030905e-03, -0.00000000000000000e+00, 4.37647697741857069e-04, -0.00000000000000000e+00, -2.07140326870017922e-04, -0.00000000000000000e+00, -6.27434450418651551e-05, -0.00000000000000000e+00, 1.15753438145956715e-05};
static inline double horner(const double *c, int n, double q) { double s = 0; for (int k = n - 1; k >= 0; k--) s = s * q + c[k]; return s; }
static inline long double thetal(long double t) { return 0.5L * t * logl(t / PI2L) - 0.5L * t - PI2L / 16 + 1 / (48 * t) + 7 / (5760 * t * t * t); }
static inline int nterm(double t) { return (int)sqrt(t / 6.283185307179586); }
static inline double espacement(double t) { double e = 6.283185307179586 / log(t / 6.283185307179586); return e > 0.8 ? 0.8 : e; }
/* Z(t) à partir de la somme Σ n^(−½) e^(−it ln n) = sr + i·si (sur n ≤ N) */
static inline double Zde(double t, double sr, double si) {
    long double th = fmodl(thetal((long double)t), PI2L);
    double tau = t / 6.283185307179586, a = sqrt(tau); int n = (int)a; double q = a - n - 0.5, x = 1 / a;
    double r = horner(RS0, sizeof RS0 / 8, q) + x * (horner(RS1, sizeof RS1 / 8, q) + x * (horner(RS2, sizeof RS2 / 8, q) + x * horner(RS3, sizeof RS3 / 8, q)));
    return 2 * (cos((double)th) * sr - sin((double)th) * si) + ((n & 1) ? 1.0 : -1.0) * sqrt(x) * r;
}
typedef struct { double *ur, *ui, *vr, *vi, *xr, *xi, *wr[4], *wi[4], *zz; unsigned char *fin; int Nmax; double h; } travail;
static void somme(const double *restrict ur, const double *restrict ui, int N, double *sr, double *si) {
    double a = 0, b = 0;
    #pragma omp simd reduction(+:a,b)
    for (int n = 1; n <= N; n++) { a += ISQ[n] * ur[n]; b += ISQ[n] * ui[n]; }
    *sr = a; *si = b;
}
/* un pas : chaque terme tourne de l'angle de w (ou de son conjugué si sens = −1) */
static void tourne(double *restrict ur, double *restrict ui, const double *restrict wr, const double *restrict wi, int Nmax, double sens) {
    #pragma omp simd
    for (int n = 1; n <= Nmax; n++) {
        double x = ur[n] * wr[n] - sens * ui[n] * wi[n], y = sens * ur[n] * wi[n] + ui[n] * wr[n];
        ur[n] = x; ui[n] = y;
    }
}
static double pas(travail *W, double *ur, double *ui, int niv, double t) {       /* avance d'un pas de niveau niv, renvoie Z(t) */
    tourne(ur, ui, W->wr[niv], W->wi[niv], W->Nmax, 1.0);
    double sr, si; somme(ur, ui, nterm(t), &sr, &si); return Zde(t, sr, si);
}
/* racine dans [0,1] du polynôme de degré 3 qui passe par (−1,a), (0,b), (1,c), (2,d), sachant b·c < 0 */
static double racine_cubique(double a, double b, double c, double d) {
    double lo = 0, hi = 1, x = b / (b - c);
    for (int it = 0; it < 40; it++) {
        double p = -a * x * (x - 1) * (x - 2) / 6 + b * (x + 1) * (x - 1) * (x - 2) / 2 - c * (x + 1) * x * (x - 2) / 2 + d * (x + 1) * x * (x - 1) / 6;
        if ((p > 0) == (b > 0)) lo = x; else hi = x;
        double dp = -a * ((x - 1) * (x - 2) + x * (x - 2) + x * (x - 1)) / 6 + b * ((x - 1) * (x - 2) + (x + 1) * (x - 2) + (x + 1) * (x - 1)) / 2
                    - c * (x * (x - 2) + (x + 1) * (x - 2) + (x + 1) * x) / 2 + d * (x * (x - 1) + (x + 1) * (x - 1) + (x + 1) * x) / 6;
        double xn = dp != 0 ? x - p / dp : 0.5 * (lo + hi);
        if (!(xn > lo && xn < hi)) xn = 0.5 * (lo + hi);
        if (fabs(xn - x) < 1e-15) { x = xn; break; }
        x = xn;
    }
    return x;
}
typedef struct { long creux, resolus, fausses, candidats; double tcand, vcand, zmax; } bilan;
/* Examine finement [t0, t0 + 32·pas] : l'état (sr, si) est celui de t0. Ajoute les zéros trouvés ; renvoie leur nombre.
   Si aucun changement de signe : descend d'un niveau autour du creux ; au dernier niveau, signale un candidat. */
static int affine(travail *W, const double *sr0, const double *si0, double t0, int niv, double *zeros, int *nz, bilan *B, int creux) {
    double hf = W->h / pow(16.0, niv), fz[35]; int N = W->Nmax, trouve = 0;
    double *ur = niv == 1 ? W->vr : (niv == 2 ? W->xr : W->ur), *ui = niv == 1 ? W->vi : (niv == 2 ? W->xi : W->ui);
    double tr[NT + 2], ti[NT + 2];
    if (niv == 3) { memcpy(tr, sr0, 8 * (N + 1)); memcpy(ti, si0, 8 * (N + 1)); ur = tr; ui = ti; }
    else { memcpy(ur, sr0, 8 * (N + 1)); memcpy(ui, si0, 8 * (N + 1)); }
    double a, b; somme(ur, ui, nterm(t0), &a, &b); fz[1] = Zde(t0, a, b);
    for (int m = 1; m <= 32; m++) fz[m + 1] = pas(W, ur, ui, niv, t0 + m * hf);       /* fz[m + 1] = Z(t0 + m·hf) */
    fz[0] = fz[1]; fz[34] = fz[33];
    for (int m = 0; m < 32; m++) if (fz[m + 1] * fz[m + 2] < 0 || (fz[m + 1] == 0 && m > 0)) {
        double x = (m == 0 || m == 31) ? fz[m + 1] / (fz[m + 1] - fz[m + 2]) : racine_cubique(fz[m], fz[m + 1], fz[m + 2], fz[m + 3]);
        if (*nz < ZMAX) zeros[(*nz)++] = t0 + (m + x) * hf;
        trouve++;
    }
    if (trouve || !creux) return trouve;
    int ms = 0;                                                                        /* le fond du creux, s'il y en a un */
    for (int m = 1; m <= 31; m++) if (fabs(fz[m + 1]) < fabs(fz[m]) && fabs(fz[m + 1]) <= fabs(fz[m + 2]) && (!ms || fabs(fz[m + 1]) < fabs(fz[ms + 1]))) ms = m;
    if (!ms) { if (niv == 1) B->fausses++; else { B->candidats++; B->tcand = t0; B->vcand = fz[17]; } return 0; }   /* niveau 1 : l'interpolation s'était trompée */
    if (niv < 3) {
        double er[NT + 2], ei[NT + 2]; memcpy(er, sr0, 8 * (N + 1)); memcpy(ei, si0, 8 * (N + 1));
        for (int m = 0; m < ms - 1; m++) tourne(er, ei, W->wr[niv], W->wi[niv], N, 1.0);
        return affine(W, er, ei, t0 + (ms - 1) * hf, niv + 1, zeros, nz, B, 1);
    }
    double y0 = fz[ms], y1 = fz[ms + 1], y2 = fz[ms + 2], den = y0 - 2 * y1 + y2, xm = den != 0 ? 0.5 * (y0 - y2) / den : 0;
    double v = y1 - 0.25 * (y0 - y2) * xm;                                             /* sommet de la parabole */
    B->candidats++; B->tcand = t0 + (ms + xm) * hf; B->vcand = v;
    return 0;
}
/* Tous les zéros de [a, b[ */
static void tranche(double a, double b, travail *W, double *zeros, int *nzo, bilan *B, int div) {
    double h0 = espacement(a) / div; int M = (int)ceil((b - a) / h0); double h = (b - a) / M; W->h = h;
    int N = nterm(b + 4 * h) + 1; if (N > NT) N = NT; W->Nmax = N;
    long double ts = (long double)a - 3 * (long double)h;
    for (int n = 1; n <= N; n++) {
        long double ph = fmodl(ts * LNL[n], PI2L); W->ur[n] = cos((double)ph); W->ui[n] = -sin((double)ph);
        double st = h * LN[n];
        for (int l = 0; l < 4; l++) { W->wr[l][n] = cos(st); W->wi[l][n] = -sin(st); st /= 16; }
    }
    double *z = W->zz + 3, sr, si; int nz = 0; memset(W->fin, 0, M + 8); unsigned char *fin = W->fin + 4;
    somme(W->ur, W->ui, nterm(a - 3 * h), &sr, &si); z[-3] = Zde(a - 3 * h, sr, si);
    for (int j = -2; j <= M + 3; j++) {
        z[j] = pas(W, W->ur, W->ui, 0, a + j * h);
        int i = j - 3;                                                    /* motif centré sur t_i, i de 0 à M − 1 */
        if (i < 0 || i > M - 1) continue;
        double p = z[i - 1], c = z[i], q = z[i + 1];
        int creux = (p * c > 0 && c * q > 0 && fabs(c) < fabs(p) && fabs(c) <= fabs(q)), deux = (p * c < 0 && c * q < 0);
        if (!creux && !deux) {                                            /* la case [t_i, t_(i+1)] vue au quart de pas */
            double u[5] = {c, 0, 0, 0, q}; int chg = 0;
            for (int k = 1; k <= 3; k++) for (int m = 0; m < 6; m++) u[k] += LAG[k - 1][m] * z[i - 2 + m];
            for (int k = 0; k < 4; k++) if (u[k] * u[k + 1] < 0) chg++;
            if (chg >= 2) creux = 1;
            for (int k = 1; k <= 3 && !creux; k++) if (u[k - 1] * u[k] > 0 && u[k] * u[k + 1] > 0 && fabs(u[k]) < fabs(u[k - 1]) && fabs(u[k]) <= fabs(u[k + 1])) creux = 1;
        }
        if (!creux && !deux) continue;
        if (fin[i - 1] && fin[i]) continue;
        memcpy(W->vr, W->ur, 8 * (N + 1)); memcpy(W->vi, W->ui, 8 * (N + 1));       /* état en t_(i+3) : on recule de 4 pas */
        for (int k = 0; k < 4; k++) tourne(W->vr, W->vi, W->wr[0], W->wi[0], N, -1.0);
        double tmp[64]; int nt = 0; double er[NT + 2], ei[NT + 2]; memcpy(er, W->vr, 8 * (N + 1)); memcpy(ei, W->vi, 8 * (N + 1));
        if (creux) B->creux++;
        int k = affine(W, er, ei, a + (i - 1) * h, 1, tmp, &nt, B, creux);
        if (creux && k) B->resolus++;
        for (int m = 0; m < nt; m++) {                                    /* on ne garde que les cases pas encore affinées */
            int cs = (int)floor((tmp[m] - a) / h); if (cs < i - 1) cs = i - 1; if (cs > i) cs = i;
            if (!fin[cs] && nz < ZMAX) zeros[nz++] = tmp[m];
        }
        fin[i - 1] = fin[i] = 1;
    }
    for (int i = 0; i < M; i++) {
        if (fabs(z[i]) > B->zmax) B->zmax = fabs(z[i]);
        if (fin[i] || !(z[i] * z[i + 1] < 0 || z[i] == 0)) continue;
        if (nz < ZMAX) zeros[nz++] = a + (i + racine_cubique(z[i - 1], z[i], z[i + 1], z[i + 2])) * h;
    }
    for (int i = 1; i < nz; i++) { double v = zeros[i]; int k = i - 1; while (k >= 0 && zeros[k] > v) { zeros[k + 1] = zeros[k]; k--; } zeros[k + 1] = v; }
    int m = 0; for (int i = 0; i < nz; i++) if (zeros[i] >= a && zeros[i] < b) zeros[m++] = zeros[i];
    *nzo = m;
}
static travail *nouveau(void) {
    travail *W = calloc(1, sizeof(travail));
    double **p[] = {&W->ur, &W->ui, &W->vr, &W->vi, &W->xr, &W->xi, &W->wr[0], &W->wr[1], &W->wr[2], &W->wr[3], &W->wi[0], &W->wi[1], &W->wi[2], &W->wi[3]};
    for (int k = 0; k < 14; k++) *p[k] = aligned_alloc(64, 8 * (NT + 10));
    W->zz = malloc(8 * 300000); W->fin = malloc(300000); return W;
}
int main(int argc, char **argv) {
    for (int n = 1; n <= NT + 1; n++) { LNL[n] = logl((long double)n); LN[n] = (double)LNL[n]; ISQ[n] = 1 / sqrt((double)n); }
    for (int k = 0; k < 3; k++) for (int m = 0; m < 6; m++) {               /* interpolation de Lagrange à 6 points, aux quarts de pas */
        double x = 0.25 * (k + 1), w = 1; for (int r = 0; r < 6; r++) if (r != m) w *= (x - (r - 2)) / (double)(m - r);
        LAG[k][m] = w;
    }
    if (argc > 4 && !strcmp(argv[1], "-f")) {                                 /* une fenêtre de Z(t) */
        double t0 = atof(argv[2]), dm = atof(argv[3]); int np = atoi(argv[4]); travail *W = nouveau();
        double a = t0 - dm, h = 2 * dm / np; W->h = h; W->Nmax = nterm(t0 + dm) + 1;
        for (int n = 1; n <= W->Nmax; n++) {
            long double ph = fmodl((long double)a * LNL[n], PI2L); W->ur[n] = cos((double)ph); W->ui[n] = -sin((double)ph);
            W->wr[0][n] = cos(h * LN[n]); W->wi[0][n] = -sin(h * LN[n]);
        }
        double sr, si; somme(W->ur, W->ui, nterm(a), &sr, &si); printf("%.12f %.12e\n", a, Zde(a, sr, si));
        for (int j = 1; j <= np; j++) printf("%.12f %.12e\n", a + j * h, pas(W, W->ur, W->ui, 0, a + j * h));
        return 0;
    }
    FILE *fz = NULL; int ia = 1;
    if (argc > 3 && !strcmp(argv[1], "-z")) { fz = fopen(argv[3], "wb"); ia = 2; }
    double T = argc > ia ? atof(argv[ia]) : 1e5, T0 = 10.0;
    if (T > 1.1e8) { fprintf(stderr, "T trop grand (augmenter NT)\n"); return 1; }
    long ntr = (long)ceil((T - T0) / LC); const int BL = 512;
    double (*buf)[ZMAX] = malloc(sizeof(double[ZMAX]) * BL); int *nzb = malloc(sizeof(int) * BL); bilan *bb = calloc(BL, sizeof(bilan));
    long total = 0, hist[400] = {0}, npaires = 0, cap = 1 << 16; double (*paires)[4] = malloc(sizeof(double[4]) * cap);
    double prec = 0, smax = -9, smin = 9, tsmax = 0, tsmin = 0, ssum = 0, emin = 9, temin = 0, zmax = 0; bilan G = {0};
    double t0 = omp_get_wtime(); long reprises = 0, alertes = 0;
    for (long d = 0; d < ntr; d += BL) {
        int nb = (int)(ntr - d < BL ? ntr - d : BL), div = 8;
        for (;;) {
            #pragma omp parallel
            {
                static __thread travail *W = NULL; if (!W) W = nouveau();
                #pragma omp for schedule(dynamic, 4)
                for (int k = 0; k < nb; k++) {
                    double a = T0 + (d + k) * LC, b = a + LC; if (b > T) b = T;
                    memset(&bb[k], 0, sizeof(bilan)); tranche(a, b, W, buf[k], &nzb[k], &bb[k], div);
                }
            }
            double sm = 0; long nn = 0, r = total;                                /* l'appel : S doit être nul en moyenne */
            for (int k = 0; k < nb; k++) for (int i = 0; i < nzb[k]; i++) { r++; nn++; sm += (double)(r - thetal(buf[k][i]) / (PI2L / 2) - 1) - 0.5; }
            if (!nn || fabs(sm / nn) < 0.15 || div >= 64) { if (nn && fabs(sm / nn) >= 0.15) { alertes++; fprintf(stderr, "ALERTE : S moyen %+.3f sur le bloc finissant en t = %.0f\n", sm / nn, T0 + (d + nb) * LC); } break; }
            div *= 2; reprises++; fprintf(stderr, "bloc repris avec une grille %d fois plus fine (S moyen %+.3f)\n", div / 8, sm / nn);
        }
        double sbloc = 0; long nbloc = 0;
        for (int k = 0; k < nb; k++) {                                            /* le dépouillement, dans l'ordre */
            G.creux += bb[k].creux; G.resolus += bb[k].resolus; G.fausses += bb[k].fausses; if (bb[k].zmax > zmax) zmax = bb[k].zmax;
            if (bb[k].candidats) { G.candidats += bb[k].candidats; G.tcand = bb[k].tcand; G.vcand = bb[k].vcand;
                printf("CANDIDAT CONTRE-EXEMPLE : creux de |Z| sans changement de signe en t = %.9f, Z = %.3e\n", bb[k].tcand, bb[k].vcand); }
            if (nzb[k] >= ZMAX) { fprintf(stderr, "tranche saturée\n"); return 1; }
            if (fz) fwrite(buf[k], 8, nzb[k], fz);
            for (int i = 0; i < nzb[k]; i++) {
                double g = buf[k][i]; total++;
                double sp = (double)(total - (long double)thetal(g) / (PI2L / 2) - 1);   /* S juste après le zéro */
                if (sp > smax) { smax = sp; tsmax = g; } if (sp - 1 < smin) { smin = sp - 1; tsmin = g; }
                ssum += sp - 0.5; sbloc += sp - 0.5; nbloc++;
                if (total > 1) {
                    double e = (g - prec) * log(0.5 * (g + prec) / 6.283185307179586) / 6.283185307179586;
                    hist[e < 3.995 ? (int)(e * 100) : 399]++;
                    if (e < emin) { emin = e; temin = prec; }
                    if (e < SEUIL) { if (npaires == cap) { cap *= 2; paires = realloc(paires, sizeof(double[4]) * cap); }
                        paires[npaires][0] = (double)(total - 1); paires[npaires][1] = prec; paires[npaires][2] = g; paires[npaires][3] = e; npaires++; }
                }
                prec = g;
            }
        }
        double tb = T0 + (d + nb) * LC; if (tb > T) tb = T;
        fprintf(stderr, "t = %.0f : %ld zéros ; formule %.2f ; S moyen sur le bloc %+.4f ; %.0f s\n", tb, total, (double)(thetal(tb) / (PI2L / 2)) + 1, nbloc ? sbloc / nbloc : 0.0, omp_get_wtime() - t0);
    }
    printf("# hauteur T = %.0f\n# zéros trouvés sur la droite : %ld\n# attendu, θ(T)/π + 1 : %.3f\n", T, total, (double)(thetal(T) / (PI2L / 2)) + 1);
    printf("# S(t) : moyenne %.5f, minimum %.4f (t = %.3f), maximum %.4f (t = %.3f)\n", ssum / total, smin, tsmin, smax, tsmax);
    printf("# creux de |Z| examinés : %ld ; résolus en deux zéros : %ld ; fausses alertes de l'interpolation : %ld ; candidats contre-exemples : %ld\n", G.creux, G.resolus, G.fausses, G.candidats);
    printf("# blocs repris avec une grille plus fine après l'appel : %ld ; alertes restantes : %ld\n", reprises, alertes);
    printf("# plus grande valeur de |Z| sur la grille : %.3f\n# plus petit écart rapporté à l'écart moyen : %.6f (t = %.6f)\n", zmax, emin, temin);
    printf("# histogramme des écarts rapportés à l'écart moyen, par pas de 0,01 :\n#");
    for (int i = 0; i < 400; i++) printf(" %ld", hist[i]);
    printf("\n# paires serrées (écart < %.2f) : %ld\n# rang  gamma_1  gamma_2  écart rapporté à l'écart moyen\n", SEUIL, npaires);
    for (long i = 0; i < npaires; i++) printf("%.0f %.9f %.9f %.6f\n", paires[i][0], paires[i][1], paires[i][2], paires[i][3]);
    if (fz) fclose(fz);
    return 0;
}
