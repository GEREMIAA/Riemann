# Ce qui se passe dans la forme de Weil quand le nombre premier 2 entre dans la fenêtre (figure weil_entree_2.png).
# Ondes paires vivant entre 1/√x et √x, base e_m(t) = cos(k_m t) sur [−a, a], a = ½ ln x, k_m = (m − ½)π/a.
# Formule explicite (Guinand–Weil) : énergie = pôles − g(0) ln π + archimédien − 2 Σ Λ(n) n^(−1/2) g(ln n).
# Usage : python3 weil_entree_2.py     (double précision : fiable tant que l'énergie la plus basse dépasse 10⁻¹² environ, soit x ≲ 4)
import math, numpy as np
from scipy.special import digamma

def mangoldt_upto(X):
    out = []
    for n in range(2, int(X) + 1):
        m, p = n, None
        for q in range(2, int(n ** 0.5) + 1):
            if m % q == 0: p = q; break
        p = p or n
        while m % p == 0: m //= p
        if m == 1: out.append((n, math.log(p)))
    return out

GX, GW = np.polynomial.legendre.leggauss(24)
def gl_nodes(R, W=0.5):
    e = np.arange(0.0, R + 1e-12, W); a0, b0 = e[:-1, None], e[1:, None]
    return ((a0 + b0) / 2 + (b0 - a0) / 2 * GX[None, :]).ravel(), ((b0 - a0) / 2 * GW[None, :] * np.ones((len(a0), 1))).ravel()

def weil_parts(N, x, R=6000.0):
    """(partie sans nombres premiers, partie des nombres premiers) de la forme de Weil, en matrices N × N."""
    a = 0.5 * math.log(x)
    k = (np.arange(1, N + 1) - 0.5) * np.pi / a; sgn = np.where(np.arange(1, N + 1) % 2 == 1, 1.0, -1.0)
    A = sgn * 2 * k * math.cosh(a / 2) / (k * k + 0.25)
    M = 2 * np.outer(A, A) - a * math.log(math.pi) * np.eye(N)                  # pôles et − g(0) ln π
    r, w = gl_nodes(R)
    with np.errstate(divide="ignore", invalid="ignore"):
        E = sgn[:, None] * 2 * k[:, None] * np.cos(r[None, :] * a) / (k[:, None] ** 2 - r[None, :] ** 2)
    E = np.where(np.abs(r[None, :] - k[:, None]) < 1e-7, a, E)
    M += (E * (w * digamma(0.25 + 0.5j * r).real)[None, :]) @ E.T / math.pi   # archimédien
    t4 = math.log(R / 2) / (3 * R ** 3) + 1 / (9 * R ** 3); t6 = math.log(R / 2) / (5 * R ** 5) + 1 / (25 * R ** 5)
    M += np.outer(sgn * k, sgn * k) * 2 * (t4 + (k[:, None] ** 2 + k[None, :] ** 2) * t6) / math.pi
    P = np.zeros((N, N)); gx, gw = np.polynomial.legendre.leggauss(800)
    for n, L in mangoldt_upto(x + 1e-9):
        u = math.log(n)
        if u >= 2 * a: continue
        lo, hi = -a, a - u; t = (lo + hi) / 2 + (hi - lo) / 2 * gx; wt = (hi - lo) / 2 * gw
        G = (np.cos(np.outer(k, t)) * wt[None, :]) @ np.cos(np.outer(k, t + u)).T
        P -= L / math.sqrt(n) * (G + G.T)
    return (M + M.T) / 2, P

if __name__ == "__main__":
    # 1) où la partie sans nombres premiers cesse d'être positive
    for N in (12, 20, 30):
        lo, hi = 2.0, 3.0
        for _ in range(30):
            mid = (lo + hi) / 2
            if np.linalg.eigvalsh(weil_parts(N, mid)[0])[0] > 0: lo = mid
            else: hi = mid
        print(f"{N} ondes : sans les nombres premiers, la positivité casse en x ≈ {lo:.4f}")
    # 2) avant et après : énergie la plus basse, avec et sans les nombres premiers ; décomposition dans la direction la plus basse
    print("\n   x     sans premiers    avec premiers    (direction la plus basse : partie sans premiers | partie des premiers)")
    for x in (1.8, 2.0, 2.1, 2.2, 2.3, 2.5, 2.75, 3.0, 3.5, 4.0):
        Winf, P = weil_parts(20, x); ev, V = np.linalg.eigh(Winf + P); v = V[:, 0]
        print(f"  {x:4.2f}   {np.linalg.eigvalsh(Winf)[0]:+.3e}      {ev[0]:+.3e}      {v @ Winf @ v:+.3e} | {v @ P @ v:+.3e}")
