# La fonction zêta des nombres premiers et celle des non-premiers (figure zeta_des_non_premiers.png).
#
# On coupe la somme ζ(s) = Σ 1/n^s en trois : le nombre 1, les nombres premiers, les non-premiers (les « composés ») :
#       ζ(s) = 1 + P(s) + C(s),      P(s) = Σ_p 1/p^s,      C(s) = Σ_{n composé} 1/n^s.
# P est la « fonction zêta des nombres premiers ». En prenant le logarithme du produit d'Euler, puis en inversant
# (formule de Möbius), on obtient son prolongement à tout le demi-plan Re s > 0 :
#       ln ζ(s) = Σ_m P(ms)/m       ⇔       P(s) = Σ_k μ(k)/k · ln ζ(ks).
# Là où ζ s'annule, son logarithme vaut −∞ : chaque zéro ρ de ζ est un point singulier de P (un « puits »), et, comme
# ζ = 1 + P + C reste finie, un point singulier de C (un « pic »). Il y en a aussi en ρ/2, ρ/3, ρ/5… et en 1, 1/2, 1/3…,
# qui s'accumulent sur l'axe Re s = 0, que P ne peut pas franchir (Landau et Walfisz, 1920).
# L'hypothèse de Riemann dit exactement : P (ou C) n'a aucun point singulier à droite de la droite Re s = ½, sauf s = 1.
#
# Les familles de non-premiers : P_k(s) = Σ 1/n^s sur les n qui ont k facteurs premiers (comptés avec répétition).
# Σ_k P_k(s) z^k = Π_p 1/(1 − z p^(−s)) = exp(Σ_m z^m P(ms)/m), d'où la récurrence k·P_k = Σ_{m=1..k} P(ms)·P_{k−m},
# par exemple P_2 = (P(s)² + P(2s))/2. Et Σ_k P_k(s) = ζ(s) : près d'un zéro, chaque famille est grande, leur somme
# est presque nulle.
# Usage : python3 zeta_des_non_premiers.py [familles_1e9.txt]        (deux à trois minutes)
import sys, json, math
from fractions import Fraction
import numpy as np

# ---------------------------------------------------------------- ζ(s) par la formule d'Euler–Maclaurin (vectorisée)
def _bernoulli(M):
    B = [Fraction(1)]
    for m in range(1, 2 * M + 1):
        B.append(-sum(math.comb(m + 1, j) * B[j] for j in range(m)) / (m + 1))
    return [float(B[2 * j] / math.factorial(2 * j)) for j in range(1, M + 1)]
_M = 16; _BJ = _bernoulli(_M)
def zeta(s):
    s = np.asarray(s, dtype=complex); forme = s.shape; s = s.ravel(); out = np.empty(len(s), complex)
    Nb = ((np.abs(s.imag) / 2).astype(int) + 25 + 49) // 50 * 50
    for N in np.unique(Nb):
        idx = np.nonzero(Nb == N)[0]; ln = np.log(np.arange(1, N)); pas = max(1, 4_000_000 // int(N))
        for i in range(0, len(idx), pas):
            c = idx[i:i + pas]; ss = s[c]
            S = np.exp(-np.outer(ss, ln)).sum(axis=1)
            Ns = np.exp(-ss * math.log(N)); S += N * Ns / (ss - 1) + Ns / 2
            terme = ss * Ns / N
            for j in range(1, _M + 1):
                S += _BJ[j - 1] * terme; terme = terme * (ss + 2 * j - 1) * (ss + 2 * j) / (N * N)
            out[c] = S
    return out.reshape(forme)

def mobius(n):
    mu = np.ones(n + 1, dtype=int); pr = np.ones(n + 1, bool)
    for p in range(2, n + 1):
        if pr[p]:
            mu[p::p] *= -1; pr[2 * p::p] = False; mu[p * p::p * p] = 0
    return mu
MU = mobius(2000)
PETITS = [p for p in range(2, 200) if all(p % d for d in range(2, int(p ** 0.5) + 1))]

def ln_module_zeta(z):
    """ln |ζ(z)| : Euler–Maclaurin si Re z ≤ 5, produit d'Euler sur les premiers < 200 sinon (erreur < 10⁻⁹)."""
    z = np.asarray(z, complex); out = np.empty(z.shape)
    bas = z.real <= 5
    if bas.any(): out[bas] = np.log(np.abs(zeta(z[bas])))
    if (~bas).any():
        zz = z[~bas]; acc = np.zeros(zz.shape)
        for p in PETITS: acc -= np.log(np.abs(1 - np.exp(-zz * math.log(p))))
        out[~bas] = acc
    return out

def re_P(s):
    """Re P(s) = Σ_k μ(k)/k · ln|ζ(ks)| : pas de problème de branche pour la partie réelle."""
    s = np.asarray(s, complex); out = np.zeros(s.shape); smin = s.real.min()
    k = 1
    while k * smin <= 45 and k < len(MU):
        if MU[k]:
            act = k * s.real <= 45
            out[act] += MU[k] / k * ln_module_zeta(k * s[act])
        k += 1
    return out

def ln_zeta(z):
    """ln ζ(z) complexe, prolongé depuis la droite le long de l'horizontale (branche habituelle), pour un point z."""
    z = complex(z)
    def droite(w): return sum(-np.log(1 - np.exp(-w * math.log(p))) for p in PETITS)
    if z.real >= 5: return complex(droite(z))
    sig = np.arange(5.0, z.real, -0.002); sig = np.append(sig, z.real)
    v = zeta(sig + 1j * z.imag); ph = np.unwrap(np.angle(v))
    ph += droite(5.0 + 1j * z.imag).imag - ph[0]
    return complex(math.log(abs(v[-1])), ph[-1])

def P(z):
    """P(z) complexe, pour un point z de partie réelle > 0 (loin des points singuliers)."""
    tot = 0j; k = 1
    while k * z.real <= 45:
        if MU[k]: tot += MU[k] / k * ln_zeta(k * z)
        k += 1
    return tot

def familles(s, K):
    """P_0 = 1, P_1 = P, …, P_K au point s, par la récurrence k·P_k = Σ_m P(ms)·P_{k−m}."""
    Pm = [None] + [P(m * s) for m in range(1, K + 1)]
    F = [1 + 0j]
    for k in range(1, K + 1): F.append(sum(Pm[m] * F[k - m] for m in range(1, k + 1)) / k)
    return F

if __name__ == "__main__":
    res = {}
    # ------------------------------------------------------------ contrôles en s = 2
    F2 = familles(2 + 0j, 30)
    print(f"P(2) = {F2[1].real:.15f} (valeur connue : 0,452247420041065…) ; Σ_k P_k(2) = {sum(F2).real:.12f} ; ζ(2) = {math.pi ** 2 / 6:.12f}")
    print(f"C(2) = ζ(2) − 1 − P(2) = {math.pi ** 2 / 6 - 1 - F2[1].real:.12f} : le poids des non-premiers")
    res["P2"] = [f.real for f in F2[:16]]
    if len(sys.argv) > 1:
        dern = open(sys.argv[1]).read().strip().split("\n")[-1].split()
        crible = {int(a.split(":")[0]): (int(a.split(":")[1]), float(a.split(":")[2])) for a in dern[4:]}
        res["crible"] = {str(k): v for k, v in crible.items()}; res["crible_x"] = int(dern[1]); res["liouville"] = int(dern[3])
        print(f"crible jusqu'à {dern[1]} : somme de Liouville L = {dern[3]}")
        for k in range(1, 9):
            print(f"   {k} facteur(s) : {crible[k][0]:>11,} entiers ; poids Σ 1/n² au crible {crible[k][1]:.12f} ; par la formule {F2[k].real:.12f}".replace(",", " "))
    # ------------------------------------------------------------ le paysage : Re P(s) dans la bande
    sig = np.linspace(0.10, 1.30, 241); tt = np.linspace(0.25, 44.0, 701)
    SG, TT = np.meshgrid(sig, tt)
    paysage = re_P(SG + 1j * TT)
    print("paysage calculé :", paysage.shape, "; min", np.nanmin(paysage), "max", np.nanmax(paysage))
    # ------------------------------------------------------------ le long de la droite critique
    t = np.arange(5.0, 45.0005, 0.005); s = 0.5 + 1j * t
    rp = re_P(s); rz = zeta(s).real; rc = rz - 1 - rp
    zeros = [14.134725142, 21.022039639, 25.01085758, 30.424876126, 32.935061588, 37.586178159, 40.918719012, 43.327073281]
    for g in zeros[:3]:
        i = np.argmin(np.abs(t - g)); print(f"près du zéro {g:.3f} : Re P = {rp[i]:+.2f}, Re C = {rc[i]:+.2f}, Re ζ − 1 = {rz[i] - 1:+.3f}")
    # et un peu à droite de la droite, pour comparer
    rp75 = re_P(0.75 + 1j * t)
    # ------------------------------------------------------------ les familles près d'un zéro
    K = 60; pts = {"près du premier zéro : s = 0,6 + 14,1347 i": 0.6 + 14.134725142j, "entre deux zéros : s = 0,6 + 17,5 i": 0.6 + 17.5j}
    res["familles"] = {}
    for nom, s0 in pts.items():
        F = familles(s0, K); z0 = complex(zeta(np.array([s0]))[0]); part = np.cumsum(F)
        res["familles"][nom] = dict(abs_zeta=abs(z0), partielles=[abs(v) for v in part], modules=[abs(f) for f in F],
                                    ecart=[abs(v - z0) for v in part])
        print(f"{nom} : |ζ| = {abs(z0):.4f} ; P = {F[1]:.3f} ; C = {z0 - 1 - F[1]:.3f} ; |1 + P| = {abs(part[1]):.3f} ; "
              f"|1 + P + P_2| = {abs(part[2]):.3f} ; avec {K} familles : {abs(part[-1]):.4f} (écart à ζ : {abs(part[-1] - z0):.1e})")
    np.savez_compressed("zeta_des_non_premiers.npz", sig=sig, tt=tt, paysage=paysage, t=t, rp=rp, rc=rc, rz=rz, rp75=rp75)
    json.dump(res, open("zeta_des_non_premiers.json", "w"))
