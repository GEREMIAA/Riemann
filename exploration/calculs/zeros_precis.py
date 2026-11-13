# Les zéros de ζ, affinés à ~10⁻¹⁰ près (nécessaires pour compter exactement les nombres premiers avec eux).
# zeros_riemann_siegel.py trouve les 138 069 zéros jusqu'à la hauteur 100 000, mais avec le seul premier terme correctif
# (erreur ~3·10⁻³ en bas, ~10⁻⁵ en haut). Ici on affine chacun d'eux sur la fonction Z(t) de Hardy, calculée :
#   - pour t < 5 000, par la formule d'Euler–Maclaurin (exacte à la précision de la machine) ;
#   - au-delà, par la formule de Riemann–Siegel avec ses cinq premiers termes correctifs C₀ … C₄ (erreur ~ t^(−11/4)).
# Les C_k sont des dérivées de Ψ(p) = cos 2π(p² − p − 1/16) / cos 2πp, dont on calcule une fois le développement de
# Taylor en haute précision (module decimal), car la division des séries est instable en double précision.
# Usage : python3 zeros_precis.py zeros_100000.npy zeros_precis.npy        (quelques minutes)
import sys, math, time
from decimal import Decimal, getcontext
import numpy as np
from scipy.special import loggamma

# ---------------------------------------------------------------- Ψ et ses dérivées (série de Taylor en q = p − ½)
def serie_psi(deg=120, prec=160):
    """coefficients ψ_k de Ψ = −cos(2πq² − 5π/8)/cos(2πq) = Σ ψ_k q^k (puissances paires), calculés en haute précision"""
    getcontext().prec = prec
    def pi_dec():                                   # recette de la documentation du module decimal
        getcontext().prec += 2
        three = Decimal(3); lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
        while s != lasts:
            lasts = s; n, na = n + na, na + 8; d, da = d + da, da + 32; t = (t * n) / d; s += t
        getcontext().prec -= 2; return +s
    def cos_sin(x):
        c, s, term, k = Decimal(0), Decimal(0), Decimal(1), 0
        while True:
            if k % 4 == 0: c += term
            elif k % 4 == 1: s += term
            elif k % 4 == 2: c -= term
            else: s -= term
            k += 1; term = term * x / k
            if abs(term) < Decimal(10) ** (-prec): break
        return c, s
    PI = pi_dec(); c58, s58 = cos_sin(5 * PI / 8)
    num = [Decimal(0)] * (deg + 1); den = [Decimal(0)] * (deg + 1)
    fact = [Decimal(1)]
    for k in range(1, 2 * deg + 2): fact.append(fact[-1] * k)
    for j in range(0, deg // 4 + 1):                  # cos(2πq²)cos(5π/8) + sin(2πq²)sin(5π/8)
        if 4 * j <= deg: num[4 * j] += (-1) ** j * (2 * PI) ** (2 * j) / fact[2 * j] * c58
        if 4 * j + 2 <= deg: num[4 * j + 2] += (-1) ** j * (2 * PI) ** (2 * j + 1) / fact[2 * j + 1] * s58
    for j in range(0, deg // 2 + 1): den[2 * j] = (-1) ** j * (2 * PI) ** (2 * j) / fact[2 * j]
    psi = [Decimal(0)] * (deg + 1)
    for n in range(deg + 1):                          # ψ·den = −num
        psi[n] = -num[n] - sum(den[k] * psi[n - k] for k in range(1, n + 1))
    return np.array([float(x) for x in psi]), float(PI)

PSI, PI_ = serie_psi()
def derivee_psi(q, m):
    k = np.arange(m, len(PSI)); coef = PSI[m:] * np.array([math.prod(range(kk - m + 1, kk + 1)) for kk in k], float)
    return np.polyval(coef[::-1], q)
def C_k(p):
    q = p - 0.5; P = math.pi; D = {m: derivee_psi(q, m) for m in (0, 1, 2, 3, 4, 5, 6, 8, 9, 12)}
    C0 = D[0]
    C1 = -D[3] / (96 * P ** 2)
    C2 = D[2] / (64 * P ** 2) + D[6] / (18432 * P ** 4)
    C3 = -D[1] / (64 * P ** 2) - D[5] / (3840 * P ** 4) - D[9] / (5308416 * P ** 6)
    C4 = D[0] / (128 * P ** 2) + 19 * D[4] / (24576 * P ** 4) + 11 * D[8] / (5898240 * P ** 6) + D[12] / (2038431744 * P ** 8)
    return C0, C1, C2, C3, C4

def theta(t):
    t = np.asarray(t, float)
    return t / 2 * np.log(t / (2 * np.pi)) - t / 2 - np.pi / 8 + 1 / (48 * t) + 7 / (5760 * t ** 3) + 31 / (80640 * t ** 5)

def Z_rs(t):
    """Riemann–Siegel avec C₀ … C₄"""
    t = np.atleast_1d(np.asarray(t, float)); tau = t / (2 * np.pi); a = np.sqrt(tau); N = np.floor(a).astype(int); p = a - N
    out = np.zeros_like(t); base = 0.5 * np.log(tau) - 0.5
    for Nv in np.unique(N):
        m = N == Nv; n = np.arange(1, Nv + 1); tt = t[m]
        ph = tt[:, None] * (base[m][:, None] - np.log(n)[None, :]) - np.pi / 8 + (1 / (48 * tt) + 7 / (5760 * tt ** 3))[:, None]
        out[m] = 2 * (np.cos(ph) / np.sqrt(n)).sum(1)
    C = C_k(p); ta = tau ** -0.5
    out += (-1.0) ** (N - 1) * tau ** -0.25 * (C[0] + ta * (C[1] + ta * (C[2] + ta * (C[3] + ta * C[4]))))
    return out

from fractions import Fraction
def _bernoulli(M):
    B = [Fraction(1)] + [Fraction(0)] * (2 * M)
    for m in range(1, 2 * M + 1):
        B[m] = -sum(math.comb(m + 1, k) * B[k] for k in range(m)) / (m + 1)
    return [float(B[2 * k]) / math.factorial(2 * k) for k in range(1, M + 1)]
BEM = _bernoulli(30)
def Z_em(t):
    """Euler–Maclaurin : ζ(½ + it), puis Z = e^{iθ} ζ (réel)"""
    t = np.atleast_1d(np.asarray(t, float)); out = np.zeros_like(t)
    th = loggamma(0.25 + 0.5j * t).imag - t / 2 * math.log(math.pi)
    for i, tv in enumerate(t):
        s = 0.5 + 1j * tv; N = int(tv / math.pi) + 30; n = np.arange(1, N)
        z = np.sum(np.exp(-s * np.log(n))) + N ** (1 - s) / (s - 1) + 0.5 * N ** (-s)
        prod, Np = s, N ** (-s - 1)
        for k in range(1, len(BEM) + 1):
            z += BEM[k - 1] * prod * Np
            prod *= (s + 2 * k - 1) * (s + 2 * k); Np /= N * N
        out[i] = (np.exp(1j * th[i]) * z).real
    return out

def Z(t):
    t = np.atleast_1d(np.asarray(t, float)); out = np.empty_like(t); bas = t < 5000
    if bas.any(): out[bas] = Z_em(t[bas])
    if (~bas).any(): out[~bas] = Z_rs(t[~bas])
    return out

def affine(z0):
    """affinage de chaque zéro approché : encadrement par changement de signe, puis méthode de l'Illinois"""
    h = 0.006 * (14.0 / z0) ** 0.75 + 2e-6
    lo, hi = z0 - h, z0 + h; flo, fhi = Z(lo), Z(hi)
    bad = np.sign(flo) == np.sign(fhi)
    for essai in range(6):                      # élargit les rares encadrements sans changement de signe
        if not bad.any(): break
        h[bad] *= 2; lo[bad] = z0[bad] - h[bad]; hi[bad] = z0[bad] + h[bad]
        flo[bad] = Z(lo[bad]); fhi[bad] = Z(hi[bad]); bad = np.sign(flo) == np.sign(fhi)
    assert not bad.any(), f"{bad.sum()} zéros sans changement de signe"
    for _ in range(40):
        mid = hi - fhi * (hi - lo) / (fhi - flo); fm = Z(mid)
        left = np.sign(fm) == np.sign(flo)
        lo = np.where(left, mid, lo); flo = np.where(left, fm, flo * 0.5)
        hi = np.where(left, hi, mid); fhi = np.where(left, fhi * 0.5, fm)
        if np.max(hi - lo) < 1e-12: break
    return hi - fhi * (hi - lo) / (fhi - flo), h

if __name__ == "__main__":
    z = np.load(sys.argv[1]); t0 = time.time()
    # contrôles : Riemann–Siegel contre Euler–Maclaurin, et quelques zéros connus
    tt = np.array([5000.3, 7005.06, 12345.6, 30000.1])
    print("RS − EM :", np.abs(Z_rs(tt) - Z_em(tt)))
    res = []
    for a in range(0, len(z), 4000):
        r, h = affine(z[a:a + 4000].copy()); res.append(r)
        print(f"  {a + len(r)} zéros affinés ({time.time() - t0:.0f} s)", flush=True)
    zp = np.concatenate(res)
    assert np.all(np.diff(zp) > 0), "zéros non strictement croissants"
    connus = {1: "14.134725141734693790", 2: "21.022039638771554993", 3: "25.010857580145688763", 10: "49.773832477672302182",
              100: "236.52422966581620580", 1000: "1419.4224809459956865"}
    for k, v in connus.items(): print(f"γ_{k} = {zp[k - 1]:.15f}   (connu {v} ; écart {zp[k - 1] - float(v):+.1e})")
    print("plus grand déplacement :", np.max(np.abs(zp - z)), " ; |Z| au plus aux zéros :", np.max(np.abs(Z(zp[::97]))))
    np.save(sys.argv[2], zp); print(f"{len(zp)} zéros en {time.time() - t0:.0f} s")
