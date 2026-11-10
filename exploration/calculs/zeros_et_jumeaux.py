# Des zéros jusqu'aux premiers jumeaux (figure zeros_et_jumeaux.png).
# 1. Corrélation de paires R₂(u) des zéros au-dessus de 10⁴ (dépliés : écart moyen 1), comparée à
#    - la loi GUE de Montgomery et Dyson : 1 − (sin πu / πu)² ;
#    - la formule de Bogomolny et Keating (1996), qui ajoute des corrections calculées avec les nombres premiers :
#      R₂ = 1 + [diag + off] / d̄², d̄ = ln(E/2π)/2π, ε = u/d̄,
#      diag = Re[(ln ζ)''(1 + iε) − Σ_p Σ_{j ≥ 2} (j − 1)(ln p)² p^{−j(1 + iε)}] / 2π²,
#      off  = Re[|ζ(1 + iε)|² e^{−2iπεd̄} A(ε)] / 2π²,   A(ε) = Π_p (1 − ((1 − p^{−iε})/(p − 1))²).
#    A(ε) est la trace, dans les zéros, du produit de Hardy–Littlewood des premiers jumeaux (Keating et Smith, 2019 :
#    connaître ces corrélations à tous les ordres revient à connaître la conjecture des k-uplets).
# 2. Remonter : on remplace A par A^κ et on cherche le κ qui colle le mieux aux zéros (κ = 1 : Hardy–Littlewood).
# 3. Les paires (p, p + h) jusqu'à 10¹⁰ contre S(h)·∫ dt/(ln t ln(t + h)), et la variance dans les petits intervalles
#    contre Montgomery–Soundararajan : H·(ln(x/H) + B), B = 1 − γ − ln 2π.
# Usage : python3 zeros_et_jumeaux.py zeros_100000.npy crible_1e+10.json     (une demi-minute ; fichiers de zeros_riemann_siegel.py et crible_paires.py)
import sys, json, math
import numpy as np
from scipy import integrate
from auto_imitation import zeta                                   # ζ par Euler–Maclaurin (même dossier)
C2 = 0.66016181584686957392781211                                 # constante des premiers jumeaux
def S(h):
    """série singulière de Hardy–Littlewood : S(h) = 2C₂ Π_{p | h, p > 2} (p − 1)/(p − 2), et 0 si h est impair"""
    if h % 2: return 0.0
    s, m, p = 2 * C2, h, 3
    while m > 1 and p <= h:
        if m % p == 0:
            s *= (p - 1) / (p - 2)
            while m % p == 0: m //= p
        p += 2
    return s

g = np.load(sys.argv[1]); cr = json.load(open(sys.argv[2]))
th = lambda t: t / 2 * np.log(t / (2 * np.pi)) - t / 2 - np.pi / 8 + 1 / (48 * t)
sel = g > 1e4; xs = th(g[sel]) / np.pi + 1; gs = g[sel]
b = np.linspace(0, 3, 61); um = (b[1:] + b[:-1]) / 2
dd = np.concatenate([xs[k:] - xs[:-k] for k in range(1, 10)])
hcount, _ = np.histogram(dd, b); R2 = hcount / (len(xs) * np.diff(b)); err = np.sqrt(hcount) / (len(xs) * np.diff(b))
gue = 1 - (np.sin(np.pi * um) / (np.pi * um)) ** 2

def primes_upto(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
P = primes_upto(1_000_000).astype(float); lP = np.log(P)
def morceaux(E):
    """les morceaux de la formule de Bogomolny–Keating à la hauteur E"""
    db = math.log(E / (2 * math.pi)) / (2 * math.pi); eps = um / db; s = 1 + 1j * eps; hh = 1e-4
    z0 = zeta(s); ll = (np.log(zeta(s + hh) / z0) + np.log(zeta(s - hh) / z0)) / hh ** 2
    corr = np.array([np.sum(sum((j - 1) * lP ** 2 * P ** (-j * (1 + 1j * e)) for j in range(2, 8))) for e in eps])
    lA = np.array([np.sum(np.log(1 - ((1 - P ** (-1j * e)) / (P - 1)) ** 2)) for e in eps])
    return db, eps, z0, ll - corr, lA
PT = [morceaux(E) for E in np.quantile(gs, np.linspace(0.05, 0.95, 10))]     # moyenne sur dix hauteurs
def modele(kappa):
    out = []
    for db, eps, z0, dg, lA in PT:
        off = (np.abs(z0) ** 2 * np.exp(-2j * math.pi * eps * db) * np.exp(kappa * lA)).real / (2 * math.pi ** 2)
        out.append(1 + (dg.real / (2 * math.pi ** 2) + off) / db ** 2)
    return np.mean(out, 0)
chi2 = lambda y: float(np.sum(((R2 - y) / err) ** 2))
ks = np.linspace(-0.5, 2.5, 301); chi = np.array([chi2(modele(k)) for k in ks]); i = int(np.argmin(chi)); ok = ks[chi <= chi[i] + 1]
res = dict(N=int(len(xs)), hauteur_mediane=float(np.median(gs)), u=um.tolist(), R2=R2.tolist(), err=err.tolist(), gue=gue.tolist(),
           bk1=modele(1).tolist(), bk0=modele(0).tolist(), kappa=ks.tolist(), chi=chi.tolist(), kbest=float(ks[i]),
           k_lo=float(ok.min()), k_hi=float(ok.max()), chi_gue=chi2(gue), chi_k1=chi2(modele(1)), chi_k0=chi2(modele(0)), chi_best=float(chi[i]))
print(f"{len(xs)} zéros au-dessus de 10⁴ (hauteur médiane {np.median(gs):.0f}) ; χ² sur {len(um)} intervalles : GUE {res['chi_gue']:.0f}, "
      f"Bogomolny–Keating {res['chi_k1']:.0f}, sans le produit de Hardy–Littlewood (κ = 0) {res['chi_k0']:.0f}")
print(f"le κ qui colle le mieux aux zéros : {ks[i]:.2f} (de {ok.min():.2f} à {ok.max():.2f}) ; Hardy–Littlewood dit κ = 1")

# 3. les paires jusqu'à NMAX, et la variance dans les petits intervalles
X = cr["NMAX"]; res["paires"] = []
for hs, c in cr["paires"].items():
    h = int(hs); li = integrate.quad(lambda v: math.exp(v) / (v * math.log(math.exp(v) + h)), math.log(2), math.log(X), limit=200)[0]
    res["paires"].append(dict(h=h, compte=c, predit=S(h) * li, S=S(h)))
ecart = max(abs(r["compte"] / r["predit"] - 1) for r in res["paires"])
print(f"paires (p, p + h) jusqu'à {X:.0e}, h = 2 … 60 : écart maximal à Hardy–Littlewood {100 * ecart:.3f} %")
B = 1 - 0.5772156649015329 - math.log(2 * math.pi); xm = cr["X0"] + cr["longueur"] / 2; res["variance"] = []
for Hs, v in cr["variance"].items():
    H = int(Hs); res["variance"].append(dict(H=H, mesure=v, ms=H * (math.log(xm / H) + B), cramer=H * math.log(xm)))
    print(f"H = {H:>6} : variance {v:>10.1f} ; Montgomery–Soundararajan {H * (math.log(xm / H) + B):>10.1f} ; Cramér {H * math.log(xm):>10.1f}")
res["xm"] = xm; json.dump(res, open("zeros_et_jumeaux.json", "w"))
