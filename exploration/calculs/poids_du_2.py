# La première marche (figure poids_du_2.png) : entre x = 2 et x = 3, seul le nombre premier 2 est dans la fenêtre.
# On multiplie son terme par un poids c (le vrai poids est c = 1, soit 2 ln 2 / √2 ≈ 0,980258) et on cherche
# l'intervalle des c pour lesquels l'énergie de Weil reste positive.
# Usage : python3 poids_du_2.py 20      (nombre d'ondes de base ; environ une minute)
import sys, numpy as np
from weil_entree_2 import weil_parts

def lmin(A, P, c): return np.linalg.eigvalsh(A + c * P)[0]

def poids_permis(A, P):
    """Intervalle [c_min, c_max] des poids c pour lesquels A + c·P reste définie positive (c'est un intervalle : convexité)."""
    def frontiere(dedans, dehors):
        for _ in range(80):
            m = (dedans + dehors) / 2
            if lmin(A, P, m) > 0: dedans = m
            else: dehors = m
        return (dedans + dehors) / 2
    bas = -1.0
    while lmin(A, P, bas) > 0 and bas > -1e6: bas *= 2
    haut = 2.0
    while lmin(A, P, haut) > 0 and haut < 1e6: haut *= 2
    return frontiere(1.0, bas), frontiere(1.0, haut)

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    for x in (2.05, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0):
        A, P = weil_parts(N, x)
        assert lmin(A, P, 1.0) > 0
        cmin, cmax = poids_permis(A, P)
        print(f"x = {x:.2f} : poids permis de {cmin:+.6f} à {cmax:+.7f}   (marge vers le haut : {cmax - 1:.2e})")
