# ζ s'imite-t-elle elle-même ? (figure auto_imitation.png)
# Voronin (1975) : dans la bande ½ < Re s < 1, ζ(s + ih) imite toute fonction qui ne s'annule pas, pour bien des h.
# Bagchi (1981) : l'hypothèse de Riemann équivaut à « ζ s'imite elle-même » : ζ(s + ih) ≈ ζ(s) sur tout disque de la bande.
# On cherche de tels h en alignant les phases h·ln p des petits nombres premiers (p^{-ih} ≈ 1), on trie avec le produit
# d'Euler, puis on calcule exactement (Euler–Maclaurin). Même chose pour la fonction de Davenport–Heilbronn, sans
# produit d'Euler, autour de son zéro hors de la droite 0,8085 + 85,6993i : chaque imitation y recopie le zéro.
# Usage : python3 auto_imitation.py 1e7      (décalages jusqu'à 10⁷ ; une dizaine de minutes)
# Affiche le meilleur décalage pour ζ (3 341 346,511 : écart 3,4 %) et les 5 meilleurs zéros recopiés de
# Davenport–Heilbronn (la figure en montre 15, obtenus de la même façon).
import sys, math, time
from fractions import Fraction
import numpy as np

# ---------------------------------------------------------------- ζ(s, a) de Hurwitz, aussi très haut dans la bande
def _bern_even(M):
    B = [Fraction(1)] + [Fraction(0)] * (2 * M)
    for m in range(1, 2 * M + 1):
        B[m] = -sum(math.comb(m + 1, k) * B[k] for k in range(m)) / Fraction(m + 1)
    return [float(B[2 * r]) for r in range(1, M + 1)]
BE = _bern_even(24)

def hurwitz(s, a, M=20, chunk=40000):
    """Euler–Maclaurin avec N ≈ |t|/4 termes directs (alors |s|/(2πN) ≈ 0,64 et la série de Bernoulli converge)."""
    s = np.atleast_1d(np.asarray(s, complex))
    N = int(0.25 * np.abs(s.imag).max()) + 200
    S = np.zeros(s.shape, complex)
    for k0 in range(0, N, chunk):
        S += np.exp(-np.multiply.outer(s, np.log(np.arange(k0, min(N, k0 + chunk)) + a))).sum(-1)
    w = N + a; lw = math.log(w)
    S += np.exp((1 - s) * lw) / (s - 1) + 0.5 * np.exp(-s * lw)
    poch, fact, tw = s.copy(), 2.0, np.exp(-(s + 1) * lw)
    for r in range(1, M + 1):
        S += BE[r - 1] / fact * poch * tw
        poch = poch * (s + 2 * r - 1) * (s + 2 * r); fact *= (2 * r + 1) * (2 * r + 2); tw = tw / (w * w)
    return S

def zeta(s): return hurwitz(s, 1.0)

# Davenport–Heilbronn : f = a·L(s, χ) + b·L(s, χ̄), χ le caractère modulo 5 avec χ(2) = i ; coefficients (1, τ, −τ, −1)
CHI = {1: 1, 2: 1j, 4: -1, 3: -1j}
TAU = math.tan(np.angle(sum(CHI[a] * np.exp(2j * np.pi * a / 5) for a in CHI) / (1j * math.sqrt(5))) / 2)
A_DH, B_DH = (1 - 1j * TAU) / 2, (1 + 1j * TAU) / 2
def L_chi(s, conj=False):
    s = np.atleast_1d(np.asarray(s, complex))
    return np.exp(-s * math.log(5)) * sum((np.conj(c) if conj else c) * hurwitz(s, a / 5) for a, c in CHI.items())
def f_dh(s): return A_DH * L_chi(s) + B_DH * L_chi(s, conj=True)

# ---------------------------------------------------------------- recherche des décalages h
def premiers(n):
    t = np.ones(n + 1, bool); t[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if t[i]: t[i * i::i] = False
    return np.nonzero(t)[0]

def etape1(H, pas=0.05):
    """Minima locaux de J(h) = Σ_{p ≤ 13} p^{-1,4} (1 − cos(h ln p)) : les petits premiers presque alignés."""
    P1 = np.array([2, 3, 5, 7, 11, 13]); w = P1 ** -1.4; lp = np.log(P1)
    hs, Js = [], []
    for debut in np.arange(pas, H, 5_000_000 * pas):
        h = debut + pas * np.arange(5_000_000)
        J = sum(wi * (1 - np.cos(h * li)) for wi, li in zip(w, lp))
        loc = np.nonzero((J[1:-1] < J[:-2]) & (J[1:-1] <= J[2:]))[0] + 1
        loc = loc[J[loc] < 0.06 * w.sum()]
        hs.append(h[loc]); Js.append(J[loc])
    hs, Js = np.concatenate(hs), np.concatenate(Js)
    return hs[np.argsort(Js)]

P = premiers(20000); LP = np.log(P)
CHIP = np.array([0 if p == 5 else CHI[p % 5] for p in P], complex)
TH16 = 2 * np.pi * np.arange(16) / 16

def coefs(s, chi=None):
    """log F(s + ih) − log F(s) ≈ Σ_p Σ_k χ(p)^k p^{-ks} (p^{-ikh} − 1)/k : coefficients p^{-ks}/k (k ≤ 3 pour p ≤ 100)."""
    out = []
    for k in (1, 2, 3):
        sel = P <= (P[-1] if k == 1 else 100)
        c = np.exp(-k * np.multiply.outer(LP[sel], s)) / k
        if chi is not None: c = c * (chi[sel] ** k)[:, None]
        out.append((k, sel, c))
    return out

def delta(h, co):
    E = np.exp(-1j * np.multiply.outer(np.atleast_1d(h), LP))
    return sum((E[:, sel] ** k - 1) @ c for k, sel, c in co)

def par_lots(fun, h, B=2000):
    return np.concatenate([fun(h[i:i + B]) for i in range(0, len(h), B)])

def raffiner(fun, h0, demi=0.06):
    g = h0 + np.linspace(-demi, demi, 241); v = fun(g); i = int(np.argmin(v))
    g2 = g[i] + np.linspace(-demi / 60, demi / 60, 81); v2 = fun(g2); j = int(np.argmin(v2))
    return g2[j], v2[j]

def newton(f, z, pas=30):
    for _ in range(pas):
        e = 1e-6; d = (f(z + e)[0] - f(z - e)[0]) / (2 * e); dz = f(z)[0] / d; z = z - dz
        if abs(dz) < 1e-13: break
    return z

if __name__ == "__main__":
    H = float(sys.argv[1]) if len(sys.argv) > 1 else 1e7
    t0 = time.time()
    hs = etape1(H)[:60000]
    print(f"{len(hs)} décalages candidats jusqu'à {H:.0e} ({time.time() - t0:.0f} s)", flush=True)
    # ζ sur le cercle de centre 0,85 + 20i et de rayon 0,08
    CZ, RZ = 0.85 + 20j, 0.08
    coz = coefs(CZ + RZ * np.exp(1j * TH16))
    score_z = lambda h: np.abs(delta(h, coz)).max(1)
    v = par_lots(score_z, hs)
    meilleurs = sorted((raffiner(score_z, hs[i]) for i in np.argsort(v)[:150]), key=lambda x: x[1])[:25]
    sz = CZ + RZ * np.exp(1j * 2 * np.pi * np.arange(64) / 64); z0 = zeta(sz)
    res = sorted(((float(np.abs(zeta(sz + 1j * h) - z0).max() / np.abs(z0).max()), h) for h, _ in meilleurs))
    print(f"ζ : meilleur décalage h = {res[0][1]:.3f}, écart maximal sur le cercle {100 * res[0][0]:.1f} % de |ζ| ({time.time() - t0:.0f} s)", flush=True)
    # Davenport–Heilbronn autour de son zéro hors de la droite
    RHO, RD = 0.8085171824566364 + 85.69934848537758j, 0.1
    sd16 = RHO + RD * np.exp(1j * TH16)
    cod, codb = coefs(sd16, CHIP), coefs(sd16, np.conj(CHIP))
    Lc, Lb = L_chi(sd16), L_chi(sd16, conj=True); f16 = A_DH * Lc + B_DH * Lb
    def score_d(h):
        f = A_DH * Lc * np.exp(delta(h, cod)) + B_DH * Lb * np.exp(delta(h, codb))
        return np.abs(f - f16).max(1) / np.abs(f16).min()
    v = par_lots(score_d, hs)
    meilleurs = sorted((raffiner(score_d, hs[i]) for i in np.argsort(v)[:150]), key=lambda x: x[1])[:5]
    sd = RHO + RD * np.exp(1j * 2 * np.pi * np.arange(64) / 64); f0 = f_dh(sd)
    for h, _ in meilleurs:
        rouche = np.abs(f_dh(sd + 1j * h) - f0).max() / np.abs(f0).min()
        z = newton(f_dh, RHO + 1j * h)
        print(f"Davenport–Heilbronn, h = {h:.4f} : rapport de Rouché {rouche:.2f} (< 1 : un zéro dans le disque décalé) ; "
              f"zéro recopié {z.real:.6f} + {z.imag:.6f} i ({time.time() - t0:.0f} s)", flush=True)
