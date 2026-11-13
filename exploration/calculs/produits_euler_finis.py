# « Vrai avec les premiers jusqu'à X, donc vrai avec tous ? » Les approximations de ζ par des produits d'Euler finis.
#
# Avec les seuls nombres premiers p ≤ X, on forme le produit d'Euler fini P_X(s) = Π_{p ≤ X} (1 − p^(−s))^(−1) et on le
# symétrise comme ζ, d'après une idée de Gonek (2007) : sur la droite critique s = ½ + it, on pose
#     ζ_X(½ + it) = P_X(s) + χ(s) · conj(P_X(s)),   où ζ(s) = χ(s) ζ(1 − s) est l'équation fonctionnelle et χ = e^(−2iϑ(t)),
# c'est-à-dire ζ_X(½ + it) = 2 e^(−iϑ(t)) · Re( e^(iϑ(t)) P_X(½ + it) ).
# ζ_X s'annule sur la droite chaque fois que Φ_X(t) = ϑ(t) + arg P_X(½ + it) passe par π/2 + kπ : ce sont les zéros qu'on suit.
# Gonek travaille avec un produit lissé et prolonge son modèle hors de la droite par P_X(s) + χ(s)·conj(P_X(s)), qui n'est pas
# analytique ; il démontre, sans hypothèse, que tous ses zéros au-dessus d'une petite hauteur sont sur la droite (presque par
# construction : |χ| ne vaut 1 que sur la droite). C'est « vrai avec les premiers jusqu'à X ».
# Question : quand X grandit, ces zéros tendent-ils vers ceux de ζ ? On suit les zéros entre les hauteurs 10 et 60 pour
# X = 2, 3, 5, … jusqu'à un million.
# Usage : python3 produits_euler_finis.py 1000000        (une à deux minutes)
import sys, json, math
import numpy as np

XMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
t = np.arange(8.0, 62.0, 0.005)
def theta(t):                                               # ϑ(t) = Im ln Γ(1/4 + it/2) − (t/2) ln π, développement asymptotique
    return t / 2 * np.log(t / (2 * np.pi)) - t / 2 - np.pi / 8 + 1 / (48 * t) + 7 / (5760 * t ** 3) + 31 / (80640 * t ** 5)
crible = np.ones(XMAX + 1, bool); crible[:2] = False
for i in range(2, int(XMAX ** 0.5) + 1):
    if crible[i]: crible[i * i::i] = False
premiers = np.nonzero(crible)[0]
# valeurs de X suivies : tous les premiers jusqu'à 50, puis une échelle logarithmique
suivis = sorted(set([int(p) for p in premiers if p <= 50] + [int(premiers[premiers <= v][-1]) for v in np.unique(np.round(np.logspace(np.log10(53), np.log10(XMAX), 70)).astype(int))]))
th = theta(t); argP = np.zeros_like(t); res = {}
j = 0
for p in premiers:
    a = p ** -0.5
    lp = math.log(p)
    argP -= np.arctan2(a * np.sin(t * lp), 1 - a * np.cos(t * lp))   # 1 − p^(−½−it) = 1 − a cos(t ln p) + i a sin(t ln p)
    if j < len(suivis) and p == suivis[j]:
        phi = th + argP
        k = np.floor((phi - np.pi / 2) / np.pi)
        ch = np.nonzero(np.diff(k) != 0)[0]                  # Φ_X passe par π/2 + kπ entre t[i] et t[i+1]
        zs = []
        for i in ch:
            c = (max(k[i], k[i + 1])) * np.pi + np.pi / 2
            zs.append(float(t[i] + (c - phi[i]) / (phi[i + 1] - phi[i]) * (t[i + 1] - t[i])))
        res[int(p)] = [z for z in zs if 10 <= z <= 60]
        j += 1
vrais = [14.134725142, 21.022039639, 25.01085758, 30.424876126, 32.935061588, 37.586178159, 40.918719012, 43.327073281,
         48.005150881, 49.773832478, 52.970321478, 56.446247697, 59.347044003]
print("X        nombre de zéros dans [10, 60]   écart moyen aux zéros de ζ (les 13 premiers)")
ecarts = {}
for X, zs in res.items():
    if len(zs) >= 13:
        e = float(np.mean([min(abs(z - v) for z in zs) for v in vrais])); ecarts[X] = e
    else: ecarts[X] = None
    if X in (2, 3, 5, 7, 11, 13, 29, 47) or X == max(res) or X in list(res)[30::8]:
        print(f"{X:8d}  {len(zs):5d}   {ecarts[X] if ecarts[X] is None else round(ecarts[X], 4)}")
json.dump(dict(zeros={str(k): v for k, v in res.items()}, ecarts={str(k): v for k, v in ecarts.items()}, vrais=vrais), open("produits_euler_finis.json", "w"))
