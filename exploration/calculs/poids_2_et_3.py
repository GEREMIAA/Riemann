# Quand le nombre 3 entre à son tour (figure poids_2_et_3.png) : pour 3 < x ≤ 4, la fenêtre contient les nombres premiers 2 et 3.
# Pour chacun, on cherche l'intervalle des poids c (vrai poids : c = 1) qui gardent l'énergie de Weil positive, l'autre restant à son vrai poids.
# Les marges deviennent minuscules (10⁻¹¹ à x = 4) : le calcul se fait en haute précision avec weil_hp.py (module standard decimal).
# Usage : python3 poids_2_et_3.py 20      (nombre d'ondes de base ; une à deux minutes)
import sys
from decimal import Decimal as D
import weil_hp as W

def separer(X, N, chiffres=80):
    """A (sans nombres premiers) et P[n] (terme de chaque puissance de premier n), avec A + Σ P[n] = forme de Weil."""
    W.set_precision(chiffres)
    M, parts = W.weil_matrix(D(X), N, parts=True)
    a, K = parts["a"], parts["K"]
    A = [[parts["pole"][i][j] + parts["arch"][i][j] - (parts["const"] if i == j else 0) for j in range(N)] for i in range(N)]
    P = {}
    for n, p in W.prime_powers_below(D(X)):
        u = D(n).ln()
        if u < 2 * a:
            G = W.G_matrix(u, a, K); coef = 2 * D(p).ln() / D(n).sqrt()
            P[n] = [[-coef * G[i][j] for j in range(N)] for i in range(N)]
    return A, P

def positive(A, P, poids):
    N = len(A)
    M = [[A[i][j] + sum(poids.get(n, D(1)) * P[n][i][j] for n in P) for j in range(N)] for i in range(N)]
    piv = W.cholesky_pivots(M)
    return len(piv) == N and all(x > 0 for x in piv)

def intervalle(A, P, n, pas=48):
    def frontiere(dedans, dehors):
        dedans, dehors = D(dedans), D(dehors)
        for _ in range(pas):
            m = (dedans + dehors) / 2
            if positive(A, P, {n: m}): dedans = m
            else: dehors = m
        return (dedans + dehors) / 2
    bas = D(-1)
    while positive(A, P, {n: bas}) and bas > -10**6: bas *= 2
    haut = D(2)
    while positive(A, P, {n: haut}) and haut < 10**6: haut *= 2
    return frontiere(1, bas), frontiere(1, haut)

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    for x in ("3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "4"):
        A, P = separer(x, N)
        (b2, h2), (b3, h3) = intervalle(A, P, 2), intervalle(A, P, 3)
        print(f"x = {x:>3} : poids du 2 dans [1 − {float(1 - b2):.2e} ; 1 + {float(h2 - 1):.2e}]   poids du 3 dans [{float(b3):+.6f} ; 1 + {float(h3 - 1):.2e}]", flush=True)
