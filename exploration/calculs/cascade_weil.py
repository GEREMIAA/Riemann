# La cascade de Weil (figure cascade_weil.png) : chaque puissance de premier n entre dans la fenêtre à x = n,
# d'abord « libre » (on pourrait l'enlever), puis « nécessaire » (sans elle, l'énergie de Weil devient négative),
# puis « verrouillée » (son poids ne peut plus bouger que d'une quantité minuscule).
#   W(x) = A + Σ_n c_n P_n, avec les vrais poids c_n = 1 ; ondes paires vivant entre 1/√x et √x, N ondes de base.
# Deux mesures :
#   - le point de nécessité x_n* : premier x > n où W(x) sans le terme de n cesse d'être définie positive ;
#   - le verrou à x donné : de combien le poids c_n peut monter ou descendre (les autres restant à 1) sans casser la positivité.
# La loi qu'on observe : la marge la plus fine ≈ λ₁ / |⟨v₁, P_n v₁⟩|, où λ₁ est la plus petite valeur propre de W(x)
# et v₁ l'onde correspondante (l'onde « la plus fragile »).
# Usage : python3 cascade_weil.py necessite 20 32       (points de nécessité jusqu'à x = 32, une dizaine de minutes)
#         python3 cascade_weil.py verrous 20 4,8,16,32  (verrous à ces x, quelques secondes par point)
# Avec plus d'ondes (N plus grand), les fenêtres de liberté et les verrous ne peuvent que rétrécir : les ondes de N
# sont parmi celles de N + 1. Les nombres donnés avec N = 20 sont donc des bornes larges.
import sys, math
from decimal import Decimal as D
import weil_hp as W

def matrices(X, N):
    """W(x) complète, et le terme P[n] de chaque puissance de premier présente (matrices en haute précision)."""
    M, parts = W.weil_matrix(D(X), N, parts=True)
    a, K = parts["a"], parts["K"]
    P = {}
    for n, p in W.prime_powers_below(D(X)):
        u = D(n).ln()
        if u < 2 * a:
            G = W.G_matrix(u, a, K); coef = 2 * D(p).ln() / D(n).sqrt()
            P[n] = [[-coef * G[i][j] for j in range(N)] for i in range(N)]
    return M, P

def positive(M):
    piv = W.cholesky_pivots(M)
    return len(piv) == len(M) and all(v > 0 for v in piv)

def plus(M, Pn, t):
    return [[M[i][j] + t * Pn[i][j] for j in range(len(M))] for i in range(len(M))]

def sans_n_positive(n, log10_eps, N):
    """À x = n·e^ε : (W(x) positive ?, W(x) sans le terme de n positive ?)"""
    X = D(n) * (D(10) ** D(repr(log10_eps))).exp()
    M, P = matrices(X, N)
    return positive(M), positive(plus(M, P[n], D(-1)))

def point_de_necessite(n, N, depart=-34.0, plafond=1.0, pas=14):
    """Recherche sur log10 ε (x = n·e^ε) : balayage par deux décades, puis dichotomie."""
    k = depart
    tout, sans = sans_n_positive(n, k, N)
    assert tout and sans, "au départ, n devrait être libre"
    while True:
        if k + 2 > plafond: return None                     # n reste libre dans toute la plage
        tout, sans = sans_n_positive(n, k + 2, N)
        assert tout, "W(x) complète non positive : augmenter la précision"
        if not sans: break
        k += 2
    bas, haut = k, k + 2
    for _ in range(pas):
        m = (bas + haut) / 2
        if sans_n_positive(n, m, N)[1]: bas = m
        else: haut = m
    e = (bas + haut) / 2
    return e, n * math.exp(10 ** e)

def marge(M, Pn, signe, bas=-110.0, haut=3.0, pas=22):
    """Plus grand t > 0 (renvoyé en log10) tel que W + signe·t·P_n reste positive ; None si jamais cassé."""
    if positive(plus(M, Pn, signe * D(10) ** D(repr(haut)))): return None
    for _ in range(pas):
        m = (bas + haut) / 2
        if positive(plus(M, Pn, signe * D(10) ** D(repr(m)))): bas = m
        else: haut = m
    return (bas + haut) / 2

def plus_fragile(M):
    """λ₁ et v₁ par itération inverse (départ grossier, puis raffinement en haute précision)."""
    N = len(M); v0 = [1.0 if i == 0 else 0.0 for i in range(N)]
    lam, v, res = W.smallest_eigenpair(M, v0, iterations=40)
    return lam, v

def verrous(X, N):
    M, P = matrices(X, N)
    assert positive(M)
    lam, v = plus_fragile(M)
    print(f"x = {X} : plus petite valeur propre λ₁ = {float(lam):.2e}")
    for n in sorted(P):
        s = sum(v[i] * sum(P[n][i][j] * v[j] for j in range(N)) for i in range(N))
        h, b = marge(M, P[n], +1), marge(M, P[n], -1)
        hs = "jamais" if h is None else f"10^{h:.2f}"
        bs = "jamais" if b is None else f"10^{b:.2f}"
        print(f"   n = {n:>2} : le poids peut monter de {hs}, descendre de {bs} ; loi λ₁/|⟨v₁,P v₁⟩| = 10^{float((lam / abs(s)).log10()):.2f}")

if __name__ == "__main__":
    mode, N = sys.argv[1], int(sys.argv[2])
    W.set_precision(200)
    if mode == "necessite":
        xmax = float(sys.argv[3])
        for n, p in W.prime_powers_below(D(repr(xmax)) + D("1e-9")):      # toutes les puissances n ≤ xmax
            r = point_de_necessite(n, N)
            print(f"n = {n:>2} : libre jusqu'à " + ("la fin de la plage" if r is None else f"x* = {r[1]:.10g}  (ε* = ln(x*/n) = 10^{r[0]:.3f})"), flush=True)
    else:
        for X in sys.argv[3].split(","):
            verrous(X, N)
