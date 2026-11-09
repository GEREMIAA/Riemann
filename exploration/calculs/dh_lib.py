# Bibliothèque : fonction de Davenport–Heilbronn et ζ par Euler–Maclaurin (utilisée par dh_zeros.py).
# Fonction de Davenport–Heilbronn : même symétrie que ζ (équation fonctionnelle), mais pas de produit d'Euler.
# f(s) = Σ a(n) n^-s, a périodique modulo 5 : a = (1, τ, −τ, −1, 0) pour n ≡ 1, 2, 3, 4, 0.
import math
from fractions import Fraction
import numpy as np
from scipy.special import loggamma

def _bern_even(M):
    B = [Fraction(1)] + [Fraction(0)] * (2 * M)
    for m in range(1, 2 * M + 1):
        B[m] = -sum(math.comb(m + 1, k) * B[k] for k in range(m)) / Fraction(m + 1)
    return [float(B[2 * r]) for r in range(1, M + 1)]
BE = _bern_even(25)

def hurwitz(s, a, N=100, M=20, chunk=20000):
    """ζ(s, a) par Euler–Maclaurin (s complexe, tableau numpy)."""
    shape = np.shape(s); s = np.atleast_1d(np.asarray(s, complex)); out = np.empty_like(s)
    lk = np.log(np.arange(N) + a); w = N + a; lw = math.log(w)
    for i in range(0, s.size, chunk):
        z = s.ravel()[i:i + chunk]
        S = np.exp(-np.multiply.outer(z, lk)).sum(1)
        S += np.exp((1 - z) * lw) / (z - 1) + 0.5 * np.exp(-z * lw)
        poch, fact, tw = z.copy(), 2.0, np.exp(-(z + 1) * lw)
        for r in range(1, M + 1):
            S += BE[r - 1] / fact * poch * tw
            poch = poch * (z + 2 * r - 1) * (z + 2 * r); fact *= (2 * r + 1) * (2 * r + 2); tw = tw / (w * w)
        out.ravel()[i:i + chunk] = S
    return out.reshape(shape)

# le caractère χ modulo 5 avec χ(2) = i, sa somme de Gauss et l'angle θ
CHI = {1: 1, 2: 1j, 4: -1, 3: -1j}
GAUSS = sum(CHI[a] * np.exp(2j * np.pi * a / 5) for a in CHI)
EPS = GAUSS / (1j * math.sqrt(5))                       # nombre de racine ε(χ), |ε| = 1
THETA = np.angle(EPS) / 2                                # e^{2iθ} = ε(χ)
TAU_FORMULA = (math.sqrt(10 - 2 * math.sqrt(5)) - 2) / (math.sqrt(5) - 1)
TAU = math.tan(THETA)
COEF = {1: 1.0, 2: TAU, 3: -TAU, 4: -1.0}

def f_dh(s, **kw):
    s = np.asarray(s, complex)
    return np.exp(-s * math.log(5)) * sum(c * hurwitz(s, j / 5, **kw) for j, c in COEF.items())

def zeta(s, **kw):
    return hurwitz(s, 1.0, **kw)

def theta_dh(t):
    """phase du facteur gamma (5/π)^{(s+1)/2} Γ((s+1)/2) sur la droite s = ½ + it"""
    t = np.asarray(t, float)
    return 0.5 * t * math.log(5 / math.pi) + loggamma(0.75 + 0.5j * t).imag

def Z_dh(t, **kw):
    """fonction réelle sur la droite critique : e^{iϑ(t)} f(½ + it) (sa partie imaginaire doit être nulle)"""
    t = np.asarray(t, float)
    return np.exp(1j * theta_dh(t)) * f_dh(0.5 + 1j * t, **kw)

def Lambda_dh(s, **kw):
    s = np.asarray(s, complex)
    return np.exp((s + 1) / 2 * math.log(5 / math.pi) + loggamma((s + 1) / 2)) * f_dh(s, **kw)
