# Zéros de la fonction de Davenport–Heilbronn jusqu'à la hauteur 205, sur et hors de la droite (figure symetrie_davenport.png).
# Usage : python3 dh_zeros.py   (demande numpy et scipy ; environ 30 s)
import math, json, numpy as np
from scipy.optimize import brentq
from scipy.special import zeta as hz
from dh_lib import *
T = 205.0
# 0) au-delà de σ1, |f − 1| < 1 : aucun zéro
def tail(sig):   # Σ_{n≥2} |a(n)| n^-σ
    return TAU * (hz(sig, 2 / 5) + hz(sig, 3 / 5)) * 5 ** -sig + (hz(sig, 1 / 5) - 5 ** sig) * 5 ** -sig + hz(sig, 4 / 5) * 5 ** -sig
sig1 = brentq(lambda s: tail(s) - 1, 1.05, 4)
print("aucun zéro pour σ ≥ %.4f (|f − 1| < 1)" % sig1)
# 1) zéros sur la droite : changements de signe de Z(t)
t = np.arange(0, T, 0.002); Z = Z_dh(t).real
idx = np.nonzero(np.sign(Z[:-1]) * np.sign(Z[1:]) < 0)[0]
on = [brentq(lambda u: Z_dh(u).real, t[i], t[i + 1], xtol=1e-12) for i in idx]
print("zéros sur la droite, 0 < t < %g : %d   (les premiers : %s)" % (T, len(on), ", ".join("%.6f" % g for g in on[:5])))
print("plus petit écart entre deux changements de signe : %.4f" % np.min(np.diff(on)))
# 2) N(T) par le principe de l'argument : π N(T) = ϑ(T) + variation de arg f le long de 2 → 2+iT → ½+iT
def NT(TT, n1=40000, n2=40000):
    path = np.concatenate([2 + 1j * np.linspace(0, TT, n1), np.linspace(2, 0.5, n2) + 1j * TT])
    ph = np.unwrap(np.angle(f_dh(path)))
    assert np.max(np.abs(np.diff(ph))) < 0.5
    return (theta_dh(TT) + ph[-1] - ph[0]) / math.pi
checks = []
for TT in (50, 100, 150, 200, T):
    TT = float(TT)
    # on évite de tomber pile sur un zéro : on se place entre deux zéros de la droite
    k = np.searchsorted(on, TT); TT = (on[k - 1] + on[k]) / 2 if 0 < k < len(on) else TT
    nt = NT(TT); n0 = int(np.sum(np.array(on) < TT))
    checks.append((TT, nt, n0)); print("T = %8.3f : N(T) = %.4f zéros au total ; %d sur la droite ; il en manque %.4f" % (TT, nt, n0, nt - n0))
# 3) zéros hors de la droite : minima de |f| sur une grille σ ∈ [0,52 ; σ1], puis Newton
sg = np.arange(0.52, sig1 + 0.02, 0.01); tg = np.arange(0.0, T, 0.01)
cands = []
for i in range(0, len(tg), 2000):
    tt = tg[i:i + 2001]; S, TT2 = np.meshgrid(sg, tt); F = np.abs(f_dh(S + 1j * TT2))
    m = (F[1:-1, 1:-1] < F[:-2, 1:-1]) & (F[1:-1, 1:-1] < F[2:, 1:-1]) & (F[1:-1, 1:-1] < F[1:-1, :-2]) & (F[1:-1, 1:-1] < F[1:-1, 2:]) & (F[1:-1, 1:-1] < 0.08)
    for a, b in zip(*np.nonzero(m)): cands.append(S[a + 1, b + 1] + 1j * TT2[a + 1, b + 1])
def newton(z):
    for _ in range(60):
        h = 1e-6; d = (f_dh(z + h) - f_dh(z - h)) / (2 * h); step = f_dh(z) / d; z = z - step
        if abs(step) < 1e-14: break
    return z
off = []
for c in cands:
    z = newton(c)
    if z.real > 0.505 and 0 < z.imag < T and abs(f_dh(z)) < 1e-12 and all(abs(z - w) > 1e-6 for w in off): off.append(z)
off.sort(key=lambda z: z.imag)
# 4) contrôle par le principe de l'argument autour de chaque zéro, et vérification du jumeau 1 − ρ̄
def winding(z, r=0.02, n=4000):
    w = z + r * np.exp(2j * np.pi * np.arange(n + 1) / n); ph = np.unwrap(np.angle(f_dh(w)))
    return (ph[-1] - ph[0]) / (2 * math.pi)
res = []
for z in off:
    twin = 1 - z.conjugate()
    print("zéro hors de la droite : %.6f + %.6f i   |f| = %.0e   tour autour : %.3f   jumeau 1 − ρ̄ : |f| = %.0e" % (z.real, z.imag, abs(f_dh(z)), winding(z), abs(f_dh(twin))))
    res.append([z.real, z.imag])
# 5) bilan : le nombre de zéros manquants sur la droite = 2 × le nombre de zéros trouvés à droite
for TT, nt, n0 in checks:
    k = sum(1 for z in off if z.imag < TT)
    print("T = %8.3f : manquants %.0f   zéros hors de la droite trouvés (avec jumeaux) : %d" % (TT, round(nt - n0), 2 * k))
# 6) même chose pour ζ jusqu'à 205
tz = np.arange(10, T, 0.002)
def Zz(u):
    u = np.asarray(u, float); th = loggamma(0.25 + 0.5j * u).imag - 0.5 * u * math.log(math.pi)
    return (np.exp(1j * th) * zeta(0.5 + 1j * u)).real
Zv = Zz(tz); iz = np.nonzero(np.sign(Zv[:-1]) * np.sign(Zv[1:]) < 0)[0]
zz = [brentq(Zz, tz[i], tz[i + 1], xtol=1e-12) for i in iz]
print("ζ : %d zéros sur la droite entre 0 et %g ; premier %.9f, dernier %.6f" % (len(zz), T, zz[0], zz[-1]))
json.dump(dict(sigma1=sig1, on_line=on, off_line=res, checks=checks, zeta_zeros=zz, tau=TAU), open("dh_zeros.json", "w"))
