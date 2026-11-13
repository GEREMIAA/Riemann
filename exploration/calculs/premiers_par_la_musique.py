# Les nombres premiers retrouvés un par un avec les seuls zéros de ζ : aucun crible, aucun nombre premier en entrée.
# Pour chaque demi-entier x = n + ½, la formule explicite (même partie lisse que pi_par_les_zeros.py, marche lissée de
# largeur λ = 1/(9(2n + 1)) en ln x, un peu moins pour n = 2) donne Π(x) = Σ_{p^k ≤ x} 1/k, car aucune puissance de
# premier n'est à moins de 9λ de x : il n'y a rien à corriger. Seule erreur : les zéros au-dessus de la hauteur 100 000,
# qu'on n'a pas. Le saut Π(n + ½) − Π(n − ½) vaut 1 si n est premier, 1/k si n = p^k, 0 sinon. On compare ensuite avec
# la vérité (crible), seulement pour mesurer l'erreur.
# Usage : python3 premiers_par_la_musique.py zeros_precis.npy 30000        (environ une demi-heure sur deux cœurs)
import sys, math, json, time
from decimal import Decimal
from multiprocessing import Pool
import numpy as np
from scipy.special import erfc
import pi_par_les_zeros as P

GAM = None; FIX = None
def init(chemin):
    global GAM, FIX
    GAM = np.load(chemin); I1, J, D = P.morceaux_fixes(GAM); FIX = (I1, J, 2 * math.fsum(np.real(D)))

def formule(n):
    I1, J, SD = FIX
    x = n + 0.5; L = math.log(x); lam = min(1.0 / (9 * (2 * n + 1)), (L - P.UB) / 12.5); b = L - 12 * lam
    I2 = float(P.ei_dec(Decimal(b)) - P.ei_dec(Decimal(P.UB)))
    u, w = P.quad(lambda u: u, b, L + 12 * lam, 8)
    I3 = float(np.sum(w * 0.5 * erfc((u - L) / (math.sqrt(2) * lam)) * np.exp(u) / u))
    SU = 2 * math.fsum(np.real(P.somme_U(GAM, L, lam, 6)))
    return I1 + I2 + I3 - (SU - SD) - J

if __name__ == "__main__":
    chemin, NMAX = sys.argv[1], int(sys.argv[2]); t0 = time.time()
    with Pool(2, initializer=init, initargs=(chemin,)) as pool:
        vals = np.array([0.0] + pool.map(formule, range(2, NMAX + 1), chunksize=50))   # Π(1,5) = 0 : aucun entier ≥ 2 sous 1,5
    # la vérité, pour mesurer : Π(n + ½) = Σ_{p^k ≤ n} 1/k
    s = P.pi_petits(NMAX); vrai = np.zeros(NMAX + 1)
    for p in np.nonzero(s)[0]:
        k, q = 1, int(p)
        while q <= NMAX: vrai[q] += 1.0 / k; k += 1; q *= int(p)
    vrai = np.cumsum(vrai)[1:]
    err = vals - vrai
    sauts = np.diff(np.concatenate([[0.0], vals]))                  # Π(n + ½) − Π(n − ½)
    premiers_lus = [n for n in range(2, NMAX + 1) if abs(sauts[n - 1] - 1) < 0.25]
    vrais = [int(p) for p in np.nonzero(s)[0]]
    ko = next((n for n in range(1, NMAX + 1) if abs(err[n - 1]) > 0.25), None)
    jusqua = (ko - 1) if ko else NMAX
    bons = [p for p in premiers_lus if p <= jusqua] == [p for p in vrais if p <= jusqua]
    print(f"{NMAX} demi-entiers en {time.time() - t0:.0f} s ; erreur max {np.abs(err).max():.3f} ; "
          f"tous les Π(n + ½) justes (à ±0,25) jusqu'à n = {jusqua} ; nombres premiers lus jusque-là : {sum(1 for p in premiers_lus if p <= jusqua)} "
          f"(vrais : {sum(1 for p in vrais if p <= jusqua)}) ; liste identique : {bons}")
    for lo, hi in ((1, 1000), (1000, 5000), (5000, 10000), (10000, 20000), (20000, 30000), (30000, NMAX)):
        if lo < NMAX: print(f"   n ∈ [{lo}, {min(hi, NMAX)}] : erreur max {np.abs(err[lo - 1:min(hi, NMAX)]).max():.4f}")
    json.dump(dict(n=list(range(1, NMAX + 1)), formule=vals.tolist(), vrai=vrai.tolist(), jusqua=jusqua,
                   premiers_lus=premiers_lus), open("premiers_par_la_musique.json", "w"))
