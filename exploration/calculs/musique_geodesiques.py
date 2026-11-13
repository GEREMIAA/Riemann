# La musique des géodésiques de la surface modulaire (figure trois_mondes.png).
#
# On écoute les « nombres premiers » de la surface modulaire, ses géodésiques fermées P, de norme N(P) = e^{longueur},
# exactement comme on écoute les nombres premiers pour entendre les zéros de Riemann :
#
#     H(r) = Σ_P ln N(P₀) · w(ln N(P)) · cos(r ln N(P)) / (N(P)^{1/2} − N(P)^{−1/2})
#
# (P₀ : la géodésique primitive dont P est un multiple ; w : une fenêtre douce). La formule des traces de Selberg (1956)
# dit que H(r) a un pic en chaque r_j tel que 1/4 + r_j² soit une valeur propre du laplacien (les formes de Maass) :
# ce sont les « zéros » de la fonction zêta de Selberg, sur la droite Re s = 1/2 — c'est démontré, parce que le
# laplacien est symétrique. Pour la surface modulaire s'y ajoute un terme venant de la pointe (la « diffusion »), qui
# contient ζ(2s) : on doit donc aussi entendre, plus faiblement, la moitié des zéros de Riemann, γ/2.
# On retire seulement la contribution de la valeur propre 0 (le terme principal, x), calculée exactement. Puis on
# compare à la prédiction de Selberg, calculée sans aucune géodésique : les 20 premières formes de Maass (LMFDB) et les
# 150 premiers zéros de Riemann (zeros150.json).
# Entrée : le fichier de geodesiques_modulaires.c (trace t, nombre m(t) de géodésiques primitives de trace t).
# Usage : python3 musique_geodesiques.py traces_100000.txt zeros150.json        (deux minutes)
import sys, json, math
import numpy as np
from scipy.special import expi

d = np.loadtxt(sys.argv[1], dtype=np.int64); t = d[:, 0].astype(float); m = d[:, 1].astype(float)
gam = json.load(open(sys.argv[2]))
lnN = 2 * np.arccosh(t / 2)                                  # ln N = 2 argch(t/2)
U = float(lnN.max())

# ------------------------------------------------------------ le théorème des géodésiques premières : π(x) et ψ(x)
cum_pi = np.cumsum(m)                                        # π_Γ(N_t) : géodésiques primitives de norme ≤ N_t
ks = []
for k in range(1, 60):                                       # ψ_Γ : chaque classe P₀^k de norme ≤ x compte ln N(P₀)
    sel = k * lnN <= U + 1e-9
    if not sel.any(): break
    ks.append((k * lnN[sel], m[sel] * lnN[sel], m[sel] * lnN[sel] / (np.exp(k * lnN[sel] / 2) - np.exp(-k * lnN[sel] / 2))))
uu = np.concatenate([a for a, b, c in ks]); lam = np.concatenate([b for a, b, c in ks]); poids = np.concatenate([c for a, b, c in ks])
o = np.argsort(uu); uu, lam, poids = uu[o], lam[o], poids[o]
psi = np.cumsum(lam)
# échantillon pour les figures : en x = N_t, juste après chaque saut, sur une grille régulière en ln x
grille = np.linspace(2.0, U, 1500)
idx = np.searchsorted(uu, grille, side="right") - 1
x = np.exp(grille); psi_g = np.where(idx >= 0, psi[np.maximum(idx, 0)], 0.0)
idp = np.searchsorted(lnN, grille, side="right") - 1
pi_g = np.where(idp >= 0, cum_pi[np.maximum(idp, 0)], 0.0)
li_g = expi(grille)

# ------------------------------------------------------------ la musique
def fenetre(u):
    a = np.clip((u - 1.0) / 0.8, 0, 1); b = np.clip((U - u) / (0.25 * U), 0, 1)
    return np.sin(np.pi * a / 2) ** 2 * np.sin(np.pi * b / 2) ** 2
fw = poids * fenetre(uu)
ug = np.linspace(0, U, 200001); wg = fenetre(ug); du = ug[1] - ug[0]
R = np.arange(2.0, 26.0005, 0.005)
H = np.empty_like(R); H0 = np.empty_like(R)
for i, r in enumerate(R):
    H[i] = np.sum(fw * np.cos(r * uu))
    H0[i] = 2 * np.sum(wg * np.cos(r * ug) * np.cosh(ug / 2)) * du      # la valeur propre 0 : h(i/2)
musique = H - H0
pics = [(float(R[i]), float(musique[i])) for i in range(1, len(R) - 1)
        if musique[i] > musique[i - 1] and musique[i] > musique[i + 1] and musique[i] > 2.0]
maass = [9.53369526, 12.1730083, 13.7797513, 14.3585095, 16.1380731, 16.6442592, 17.7385633, 18.1809178, 19.4234814,
         19.4847138, 20.1066946, 21.3157959, 21.4790575, 22.1946739, 22.7859084, 23.2013961, 23.2637115, 24.1123527,
         24.4197154, 25.0508548]                             # LMFDB, formes de Maass de niveau 1
# ------------------------------------------------------------ la prédiction de Selberg : formes de Maass + zéros de Riemann
# côté spectral de la formule des traces, avec h(r) = ½[W(r − R) + W(r + R)], W(r) = 2∫ w(u) cos(ru) du :
#   • chaque forme de Maass donne ½[W(r_j − R) + W(r_j + R)] (valeurs r_j : LMFDB) ;
#   • le spectre continu donne (1/4π) ∫ W(r − R) · (−φ'/φ)(½ + ir) dr, où φ est la matrice de diffusion de la pointe,
#     φ(s) = Λ(2s − 1)/Λ(2s) avec Λ(s) = π^{−s/2} Γ(s/2) ζ(s), d'où −φ'/φ(½ + ir) = 4 [Σ_ρ ½/(¼ + (2r − γ)²) − 1/(1 + 4r²)] :
#     une bosse de hauteur 8 en chaque r = γ/2 ;
#   • les termes de l'identité, elliptiques et paraboliques sont négligeables ici (w(0) = 0, R ≥ 3).
rr = np.arange(-80, 80.0001, 0.01); ug2 = ug[::5]; wg2 = wg[::5]; du2 = ug2[1] - ug2[0]
W = np.array([2 * np.sum(wg2 * np.cos(r * ug2)) * du2 for r in rr])
def Wf(v): return np.interp(v, rr, W, left=0.0, right=0.0)
gz = np.array(gam)
moins_phi = 4 * (np.sum(0.5 / (0.25 + (2 * rr[:, None] - gz[None, :]) ** 2) + 0.5 / (0.25 + (2 * rr[:, None] + gz[None, :]) ** 2), axis=1)
                 - 1 / (1 + 4 * rr ** 2))
pred_maass = np.array([0.5 * np.sum(Wf(np.array(maass) - x) + Wf(np.array(maass) + x)) for x in R])
pred_riemann = np.array([np.sum(Wf(rr - x) * moins_phi) * 0.01 / (4 * math.pi) for x in R])
for lo, hi, nom in ((6.5, 8.0, "autour de γ₁/2 = 7,07"), (9.0, 11.0, "autour de γ₂/2 = 10,51"), (3.0, 24.0, "de 3 à 24")):
    s = (R >= lo) & (R <= hi)
    print(f"   {nom} : écart à la prédiction, Maass seules {np.abs(musique[s] - pred_maass[s]).max():.2f} ; "
          f"Maass + zéros de Riemann {np.abs(musique[s] - pred_maass[s] - pred_riemann[s]).max():.2f} (max) "
          f"{np.sqrt(np.mean((musique[s] - pred_maass[s] - pred_riemann[s]) ** 2)):.2f} (rms)")
print(f"{int(m.sum()):,} géodésiques primitives, normes jusqu'à e^{U:.2f} = {math.exp(U):.3e}".replace(",", " "))
for lx in (10, 15, 20, U):
    j = np.searchsorted(grille, lx) - 1 if lx < U else len(grille) - 1
    print(f"   x = e^{grille[j]:.1f} : π_Γ(x) = {pi_g[j]:.0f}, li(x) = {li_g[j]:.0f} ; ψ_Γ(x)/x = {psi_g[j] / x[j]:.6f} ; "
          f"(ψ_Γ − x)/√x = {(psi_g[j] - x[j]) / math.sqrt(x[j]):+.2f}")
print("pics de la musique :", "  ".join(f"{r:.3f} ({h:.1f})" for r, h in pics))
print("formes de Maass   :", "  ".join(f"{r:.3f}" for r in maass))
print("zéros de Riemann/2:", "  ".join(f"{g / 2:.3f}" for g in gam[:12]))
json.dump(dict(U=U, R=R[::4].tolist(), musique=musique[::4].tolist(), pred_maass=pred_maass[::4].tolist(),
               pred_riemann=pred_riemann[::4].tolist(), pics=pics, maass=maass, gamma_demi=[g / 2 for g in gam[:20]],
               lnx=grille.tolist(), psi=psi_g.tolist(), pi=pi_g.tolist(), li=li_g.tolist(), total=int(m.sum())),
          open("musique_geodesiques.json", "w"))
