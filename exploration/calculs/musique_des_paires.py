# La musique des nombres premiers, et celle des paires (figure musique_des_paires.png).
# On écoute trois signaux, en fonction de u = ln x :
#   f(u) = (ψ(x) − x)/√x                                   les nombres premiers ;
#   E_h(u) = (W_h(x) − S(h)·x)/√x, h = 2, 4, …, 60          les paires (p, p + h), écart à Hardy–Littlewood ;
#   g(u) = Σ_h E_h(u) / Σ_h 2S(h)                          les paires moyennées.
# Formule explicite : f(u) = −Σ_ρ e^{iγu}/ρ + petits termes. Chaque zéro ½ + iγ est une note tenue, de fréquence γ et
# de volume 2/|ρ| ; un zéro β + iγ hors de la droite serait une note qui enfle comme e^{(β − ½)u} (un « crescendo »).
# Heuristique (méthode du cercle : la densité des premiers fluctue de (1 + ε), celle des paires de (1 + ε)², soit 1 + 2ε) :
#   E_h(u) ≈ 2S(h)·f(u) + bruit propre aux paires. Chaque écart h rejoue la musique des zéros, au volume 2S(h).
#   (La version moyennée sur h est l'approximation de Korevaar et te Riele, arXiv 0902.4352.)
# Ce programme mesure : le volume total de f, le crescendo des dix premières notes, le volume β_h de la musique de ζ
# dans chaque E_h (projection sur f aux fréquences des zéros), et le spectrogramme par paquets d'ondes gaussiens.
# Usage : python3 musique_des_paires.py crible_1e+10.npz zeros_100000.npy   (une minute ; fichiers de crible_paires.py et zeros_riemann_siegel.py)
import sys, json
import numpy as np
C2 = 0.66016181584686957392781211                # constante des premiers jumeaux
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

d = np.load(sys.argv[1]); zeros = np.load(sys.argv[2])
U, X, HS = d["U"], d["X"].astype(float), d["HS"]; Sh = np.array([S(h) for h in HS])
f = (d["psi"] - X) / np.sqrt(X)
E = (d["W"] - Sh[:, None] * X[None, :]) / np.sqrt(X)[None, :]
g = E.sum(0) / (2 * Sh.sum()); t = E[0] / (2 * Sh[0])
res = {}

# 1. volume total : moyenne de f² = Σ_ρ 1/|ρ|² = 2 + γ_Euler − ln 4π, si tous les zéros sont sur la droite
m = U >= 8
res["volume"] = dict(mesure=float(f[m].std()), predit=float(np.sqrt(2 + 0.5772156649015329 - np.log(4 * np.pi))))
print(f"volume total de f : écart-type {res['volume']['mesure']:.4f} ; prédit √(2 + γ − ln 4π) = {res['volume']['predit']:.4f}")

# 2. le crescendo : volume de chacune des dix premières notes, dans un paquet gaussien (largeur 1,5) qui glisse le long de u
sig = 1.5; u0 = np.linspace(U[0] + 3 * sig, U[-1] - 3 * sig, 60); res["crescendo"] = []
for z in zeros[:10]:
    ez = np.exp(-1j * z * U); amp = []
    for c in u0:
        w = np.exp(-0.5 * ((U - c) / sig) ** 2); w[np.abs(U - c) > 5 * sig] = 0
        amp.append(abs(np.sum(f * w * ez)) * 2 / w.sum())
    pente = np.polyfit(u0, np.log(amp), 1)[0]
    res["crescendo"].append(dict(gamma=float(z), volume=float(np.mean(amp)), attendu=float(2 / np.hypot(0.5, z)), pente=float(pente)))
    print(f"note γ = {z:7.3f} : volume {np.mean(amp):.4f} (attendu 2/|ρ| = {2 / np.hypot(0.5, z):.4f}) ; croissance β − ½ ≈ {pente:+.4f}")

# 3. le volume de la musique de ζ dans chaque écart h : β_h = ⟨F_h, F⟩ / ⟨F, F⟩ aux fréquences des zéros γ < 100
mm = U >= 8.0; u = U[mm]; w = np.hanning(mm.sum())
def coef(y, gam):
    y = (y[mm] - y[mm].mean()) * w; out = np.empty(len(gam), complex)
    for i in range(0, len(gam), 500): out[i:i + 500] = np.exp(-1j * np.outer(gam[i:i + 500], u)) @ y
    return out * 2 / w.sum()
gz = zeros[zeros < 100]; F = coef(f, gz); res["paires"] = []
for k, h in enumerate(HS):
    Fh = coef(E[k], gz); beta = np.sum(np.conj(F) * Fh) / np.sum(abs(F) ** 2)
    bruit = np.std([(np.sum(np.conj(F) * coef(E[k], gz + dec)) / np.sum(abs(F) ** 2)).real for dec in (-0.9, -0.6, -0.4, 0.4, 0.6, 0.9)])
    res["paires"].append(dict(h=int(h), S=float(Sh[k]), beta=float(beta.real), beta_im=float(beta.imag), bruit=float(bruit)))
b = np.array([r["beta"] for r in res["paires"]]); p = 2 * Sh
res["pente"] = float(np.sum(b * p) / np.sum(p * p)); res["correlation"] = float(np.corrcoef(b, p)[0, 1])
print(f"volume de la musique de ζ dans les paires : pente β_h / 2S(h) = {res['pente']:.3f}, corrélation {res['correlation']:.3f} (30 écarts)")

# 4. spectres complets et spectrogrammes (paquets d'ondes gaussiens de largeur 1,25), volume normalisé par |ρ|/2
gam = np.arange(1, 120, 0.01)
spec = {nom: coef(y, gam) for nom, y in (("premiers", f), ("paires", g), ("jumeaux", t))}
gs = np.linspace(0.5, 62, 616); sig = 1.25; c0 = np.linspace(U[0] + 3 * sig, U[-1] - 3 * sig, 161)
Em = np.exp(-1j * np.outer(gs, U))
def gabor(y):
    out = np.zeros((len(gs), len(c0)))
    for j, c in enumerate(c0):
        wg = np.exp(-0.5 * ((U - c) / sig) ** 2); wg[np.abs(U - c) > 5 * sig] = 0
        out[:, j] = np.abs(Em @ ((y - np.sum(y * wg) / wg.sum()) * wg)) * 2 / wg.sum()
    return out * np.hypot(0.5, gs)[:, None] / 2
G = {nom: gabor(y) for nom, y in (("premiers", f), ("paires", g), ("jumeaux", t))}
for nom in G:
    on = np.mean([G[nom][np.argmin(abs(gs - z))].mean() for z in zeros[zeros < 60]])
    print(f"spectrogramme, {nom} : volume moyen sur les notes de ζ (γ < 60) {on:.3f} (1 = la note exacte)")
np.savez_compressed("musique_des_paires.npz", gam=gam, **{f"spec_{k}": v for k, v in spec.items()}, gs=gs, c0=c0,
                    **{f"G_{k}": v for k, v in G.items()})
json.dump(res, open("musique_des_paires.json", "w"), indent=1)
