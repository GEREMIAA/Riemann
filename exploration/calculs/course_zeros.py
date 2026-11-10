# Les courses de nombres premiers (figures course_zeros.png et course_mod3.png) :
#   q = 4 : 4k + 1 contre 4k + 3 ;  q = 3 : 3k + 1 contre 3k + 2.
#   1) on compte jusqu'à N et on liste les moments où les nombres premiers de la forme qk + 1 mènent ;
#   2) on calcule les zéros de L(s, χ_q) jusqu'à la hauteur T ;
#   3) avec ces seuls zéros, on cherche où la somme des ondes passe au-dessus de 0, jusqu'à 10¹⁴.
# Usage : python3 course_zeros.py 4 1000000000 5000   (quelques minutes ; « 3 100000000 1000 » va beaucoup plus vite)
import sys, math, numpy as np
from scipy.optimize import brentq
from scipy.special import loggamma, expi
from dh_lib import hurwitz

q = int(sys.argv[1]) if len(sys.argv) > 1 else 4
N = int(sys.argv[2]) if len(sys.argv) > 2 else 100_000_000
T = float(sys.argv[3]) if len(sys.argv) > 3 else 1000.0
assert q in (3, 4)
def chi_p(p): return np.where(p % q == 1, 1, -1)          # pour les premiers p qui ne divisent pas q

# 1) la course, par crible segmenté des nombres impairs
R = math.isqrt(N) + 1
sv = np.ones(R + 1, bool); sv[:2] = False
for i in range(2, math.isqrt(R) + 1):
    if sv[i]: sv[i * i::i] = False
base = np.nonzero(sv)[0]; base = base[base > 2]
D, lo, runs = (-1 if q == 3 else 0), (5 if q == 3 else 3), []   # q = 3 : 2 compte −1, 3 ne compte pas
while lo <= N:
    hi = min(lo + 20_000_000, N + 1); isp = np.ones((hi - lo + 1) // 2, bool)
    for p in base.tolist():
        if p * p >= hi: break
        st = max(p * p, ((lo + p - 1) // p) * p)
        if st % 2 == 0: st += p
        isp[(st - lo) // 2::p] = False
    pr = lo + 2 * np.nonzero(isp)[0]; pr = pr[pr <= N]
    cs = D + np.cumsum(chi_p(pr))
    d = np.diff(np.concatenate([[0], (cs > 0).astype(int), [0]]))
    for a, b in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
        if runs and pr[a] - runs[-1][1] < 0.05 * runs[-1][1]: runs[-1][1] = int(pr[b - 1])
        else: runs.append([int(pr[a]), int(pr[b - 1])])
    D = int(cs[-1]) if len(cs) else D; lo = hi if hi % 2 == 1 else hi + 1
print(f"Jusqu'à {N:,} : les {q}k + 1 mènent")
for r in runs: print(f"   du premier {r[0]:,} au premier {r[1]:,}")

# 2) les zéros de L(s, χ₄) sous la hauteur T
NE = max(400, int(T / 3))
def Lq(s):                                                      # L(s, χ_q) = q⁻ˢ [ζ(s, 1/q) − ζ(s, (q−1)/q)]
    s = np.asarray(s, complex)
    return np.exp(-s * math.log(q)) * (hurwitz(s, 1 / q, N=NE, M=24, chunk=3000) - hurwitz(s, (q - 1) / q, N=NE, M=24, chunk=3000))
def theta(t):
    t = np.asarray(t, float)
    return 0.5 * t * math.log(q / math.pi) + loggamma(0.75 + 0.5j * t).imag
def Z(t): return (np.exp(1j * theta(t)) * Lq(0.5 + 1j * np.asarray(t, float))).real
g = []
for a in np.arange(0.0, T, 250.0):
    t = np.arange(a, min(a + 250.0, T) + 1e-9, 0.01); z = Z(t)       # fenêtres jointives : aucun trou entre deux fenêtres
    g += [brentq(lambda u: float(Z(u)), t[i], t[i + 1], xtol=1e-12) for i in np.nonzero(np.sign(z[:-1]) * np.sign(z[1:]) < 0)[0]]
g = np.unique(np.round(g, 10)); rho = 0.5 + 1j * g
print(f"\n{len(g)} zéros de L(s, χ_{q}) sous la hauteur {T:g} (le premier : γ = {g[0]:.6f})")

# 3) la somme des ondes : biais (carrés des premiers) − 2 Σ k(γ/T) Re[ xⁱᵞ S(ρ ln x) / ρ ], puis les plus hauts pics
PM = 10_000_000
sp = np.ones(PM + 1, bool); sp[:2] = False
for i in range(2, math.isqrt(PM) + 1):
    if sp[i]: sp[i * i::i] = False
P = np.nonzero(sp)[0]
def pi(y):
    y = np.asarray(y, float)
    approx = expi(np.log(np.maximum(y, 2.0))) - 0.5 * expi(0.5 * np.log(np.maximum(y, 2.0)))
    return np.where(y <= PM, np.searchsorted(P, np.floor(np.minimum(y, PM)), side="right"), approx)
k = (1 - g / T) * np.cos(np.pi * g / T) + np.sin(np.pi * g / T) / np.pi
def E(u):
    out = np.empty(len(u))
    for i in range(0, len(u), 2000):
        uu = u[i:i + 2000]; x = np.exp(uu)
        w = np.outer(uu, rho); S = np.ones_like(w); term = np.ones_like(w)
        for j in range(1, 11): term = term * j / w; S = S + term
        bias = -(uu / np.sqrt(x)) * (0.5 * (pi(np.sqrt(x)) - 1) + 0.25 * (pi(x ** 0.25) - 1))   # carrés des premiers (sauf celui qui divise q)
        out[i:i + 2000] = bias - 2 * np.real(np.exp(1j * np.outer(uu, g)) * S / rho) @ k
    return out
u = np.arange(math.log(1e4), math.log(1e14), 0.0002); a = E(u)
d = np.diff(np.concatenate([[0], (a > 0).astype(int), [0]]))
print("Régions où la somme des ondes dépasse 0 (10⁴ à 10¹⁴) :")
for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
    print(f"   de {math.exp(u[s]):.5g} à {math.exp(u[e - 1]):.5g}   (pic {a[s:e].max():+.3f})")
pk = [i for i in range(1, len(a) - 1) if a[i] >= a[i - 1] and a[i] >= a[i + 1]]
print("Les 5 plus hauts pics :", [(f"{math.exp(u[i]):.5g}", round(float(a[i]), 3)) for i in sorted(pk, key=lambda i: -a[i])[:5]])
