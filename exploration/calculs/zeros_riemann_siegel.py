# Zéros de ζ sur la droite critique jusqu'à T, par la formule de Riemann–Siegel (premier terme correctif C₀).
# On cherche les changements de signe de la fonction Z(t) de Hardy, réelle sur la droite, puis on affine (méthode de l'Illinois).
# Précision : environ 3·10⁻³ près du premier zéro (14,1347…), bien meilleure plus haut (l'erreur décroît comme t^(−3/4)).
# Contrôle : S(T) = rang − ½ − θ(γ)/π − 1 doit rester autour de 0 ; une dérive signale des zéros manqués (pas trop grand).
# Usage : python3 zeros_riemann_siegel.py 100000 0.004     (138 069 zéros en une minute ; le n° 100 000 est 74 920,8275)
import numpy as np, math, time, sys
T = float(sys.argv[1]); STEP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.02
def theta(t):
    t = np.asarray(t, float)
    return t / 2 * np.log(t / (2 * np.pi)) - t / 2 - np.pi / 8 + 1 / (48 * t) + 7 / (5760 * t ** 3)
def C0(p):
    den = np.cos(2 * np.pi * p); num = np.cos(2 * np.pi * (p * p - p - 1 / 16))
    near = np.abs(den) < 1e-6
    alt = np.sin(2 * np.pi * (p * p - p - 1 / 16)) * (2 * p - 1) / np.where(near, np.sin(2 * np.pi * p), 1.0)
    return np.where(near, alt, num / np.where(near, 1.0, den))
def Z(t):
    t = np.atleast_1d(np.asarray(t, float)); tau = t / (2 * np.pi); sq = np.sqrt(tau); N = np.floor(sq).astype(int); p = sq - N
    th = theta(t); out = np.zeros_like(t)
    for Nv in np.unique(N):
        m = N == Nv; tt = t[m]; n = np.arange(1, Nv + 1)
        s = (np.cos(th[m][:, None] - np.outer(tt, np.log(n))) / np.sqrt(n)).sum(1)
        out[m] = 2 * s + (-1) ** (Nv - 1) * tau[m] ** -0.25 * C0(p[m])
    return out
if __name__ == "__main__":
    t0 = time.time(); roots = []
    edges = np.arange(10.0, T + 1000, 1000.0)
    prev_t, prev_z = None, None
    for a in edges:
        tg = np.arange(a, min(a + 1000, T), STEP)
        if len(tg) == 0: break
        zg = Z(tg)
        if prev_z is not None: tg = np.concatenate([[prev_t], tg]); zg = np.concatenate([[prev_z], zg])
        idx = np.nonzero(np.sign(zg[1:]) != np.sign(zg[:-1]))[0]
        lo, hi = tg[idx], tg[idx + 1]; flo, fhi = zg[idx], zg[idx + 1]
        for _ in range(6):                     # méthode de l'Illinois, vectorisée
            mid = hi - fhi * (hi - lo) / (fhi - flo); fm = Z(mid)
            left = np.sign(fm) == np.sign(flo)
            lo = np.where(left, mid, lo); flo = np.where(left, fm, flo * 0.5)
            hi = np.where(left, hi, mid); fhi = np.where(left, fhi * 0.5, fm)
        roots.append(hi - fhi * (hi - lo) / (fhi - flo))
        prev_t, prev_z = tg[-1], zg[-1]
    g = np.concatenate(roots)
    np.save(f"zeros_{int(T)}.npy", g)
    Nsmooth = theta(g) / np.pi + 1
    S = np.arange(1, len(g) + 1) - 0.5 - Nsmooth          # S(γ) ≈ rang − ½ − θ/π − 1
    print(f"{len(g)} zéros jusqu'à {T:.0f} en {time.time() - t0:.0f} s ; premiers : {g[:3]} ; n° 100 000 : {g[99999] if len(g) >= 100000 else None}")
    print(f"S(T) moyen {S.mean():.3f}, min {S.min():.2f}, max {S.max():.2f} (dérive ⇒ zéros manqués)")
