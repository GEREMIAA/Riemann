# Et si l'hypothèse était fausse ? Commencer par la fin (figure par_la_fin.png).
#
# 1. La pièce mauvaise. La fonction de Davenport–Heilbronn a la même symétrie que ζ et des zéros hors de la droite.
#    Sur la droite, cela se voit : sa fonction Z (réelle) a un creux qui ne descend pas jusqu'à zéro, et il manque
#    deux zéros à l'appel (le compte attendu vient du principe de l'argument). C'est à cela que ressemblerait la
#    preuve que l'hypothèse de Riemann est fausse.
# 2. La pièce bonne, au plus juste. Pour ζ, zeros_au_plus_juste.c examine tous les creux jusqu'à la hauteur 10⁸ :
#    tous descendent jusqu'à zéro. On lit ici la liste des paires de zéros les plus serrées.
# 3. Le film à l'envers. On déforme ζ avec un « temps » t (le flot de de Bruijn et Newman) : H_t(x) = ∫ e^(tu²) Φ(u)
#    cos(xu) du, et H_0(x) = ξ(½ + ix/2)/8, dont les zéros sont x = 2γ. Pour t ≥ 0,2, tous les zéros sont réels
#    (théorème : Polymath 15, puis Platt et Trudgian). Les zéros se repoussent : dx_k/dt = 2 Σ_{j≠k} 1/(x_k − x_j).
#    En remontant le temps ils se rapprochent, et deux zéros voisins, écartés de Δγ à l'instant 0, se percutent à
#    l'instant t ≈ −Δγ²/2, puis quittent la droite. L'hypothèse de Riemann dit : aucune collision avant l'instant 0.
#    Elle serait fausse si une seule paire avait un instant de collision positif. On simule le film autour de la
#    paire de Lehmer (hauteur 7005), et on donne la « marge » Δγ²/2 de chaque paire serrée.
# 4. La fin des nombres. Un zéro hors de la droite, de partie réelle β à la hauteur γ, ajoute au compte des nombres
#    premiers une onde d'amplitude 2x^β/γ, qui finit par dominer √x : à partir de x = (γ/2)^(1/(β − ½)).
#
# Usage : ./zeros_au_plus_juste 100000000 > zeros_au_plus_juste.txt
#         ./zeros_au_plus_juste -z 20000 zeros_20000.bin > /dev/null
#         ./zeros_au_plus_juste -f 7005.0816 0.6 1200 > fenetre_7005.txt
#         python3 par_la_fin.py zeros_au_plus_juste.txt zeros_20000.bin fenetre_7005.txt        (dix secondes)
import sys, json, math
import numpy as np
from dh_lib import f_dh, Z_dh, theta_dh

# ---------------------------------------------------------------- 1. la pièce mauvaise
def compte_dh(T, n=40000):
    """nombre de zéros de la fonction de Davenport–Heilbronn de partie imaginaire entre 0 et T (principe de l'argument)"""
    chemin = np.concatenate([2 + 1j * np.linspace(0, T, n), np.linspace(2, 0.5, n) + 1j * T])
    ph = np.unwrap(np.angle(f_dh(chemin))); assert np.max(np.abs(np.diff(ph))) < 0.5
    return (theta_dh(T) + ph[-1] - ph[0]) / math.pi
def zeros_sur_la_droite(Zf, a, b, pas=0.002):
    t = np.arange(a, b, pas); z = Zf(t); i = np.nonzero(z[:-1] * z[1:] < 0)[0]
    return t[i] - z[i] * pas / (z[i + 1] - z[i]), t, z

# ---------------------------------------------------------------- 3. le film
def film(g, k0, W=300, tfin=0.2):
    """g : les zéros (hauteurs γ) ; k0 : rang (à partir de 1) du premier zéro de la paire. Renvoie les trajectoires."""
    x = 2 * g; lo, hi = k0 - 1 - W, k0 + 1 + W                       # indices des zéros mobiles
    xm = x[lo:hi].copy(); fixes = np.concatenate([x[:lo], x[hi:], -x])       # les autres, et les zéros symétriques, restent fixes
    F0 = np.array([2 * np.sum(1 / (v - fixes)) for v in xm]); F1 = np.array([-2 * np.sum(1 / (v - fixes) ** 2) for v in xm])
    x0 = xm.copy(); n = len(xm); c = W                                # la paire : indices c et c + 1
    def vitesse(y):
        D = y[:, None] - y[None, :]; np.fill_diagonal(D, np.inf)
        return 2 * np.sum(1 / D, axis=1) + F0 + F1 * (y - x0)
    def rk4(y, dt):
        k1 = vitesse(y); k2 = vitesse(y + dt / 2 * k1); k3 = vitesse(y + dt / 2 * k2); k4 = vitesse(y + dt * k3)
        return y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    vue = slice(c - 6, c + 8)
    # vers l'avant : de l'instant 0 à l'instant tfin
    y, t, T1, Y1 = xm.copy(), 0.0, [0.0], [xm[vue].copy()]
    while t < tfin:
        dt = min(2e-4, 0.02 * np.min(np.diff(y)) ** 2, tfin - t); y = rk4(y, dt); t += dt; T1.append(t); Y1.append(y[vue].copy())
    # vers l'arrière : de l'instant 0 jusqu'à la collision de la paire
    y, t, T2, Y2 = xm.copy(), 0.0, [0.0], [xm[vue].copy()]; e0 = y[c + 1] - y[c]; hist = [(0.0, e0 ** 2)]
    while y[c + 1] - y[c] > 1e-3 * e0:
        dt = -0.01 * (y[c + 1] - y[c]) ** 2; y = rk4(y, dt); t += dt; T2.append(t); Y2.append(y[vue].copy()); hist.append((t, (y[c + 1] - y[c]) ** 2))
    (ta, ea), (tb, eb) = hist[-2], hist[-1]; tc = tb - eb * (tb - ta) / (eb - ea)          # l'écart au carré s'annule linéairement
    autres = np.concatenate([x[:k0 - 1], x[k0 + 1:], -x]); G = np.sum(1 / (0.5 * (x[k0 - 1] + x[k0]) - autres) ** 2)
    return dict(T1=T1, Y1=np.array(Y1) / 2, T2=T2, Y2=np.array(Y2) / 2, tc=tc, deux_corps=-e0 ** 2 / 8,
                voisins_figes=math.log(1 - G * e0 ** 2 / 2) / (4 * G))

if __name__ == "__main__":
    res = {}
    # ------------------------------------------------------------ 1. Davenport–Heilbronn entre 82,5 et 88,5
    Zd = lambda u: Z_dh(u).real
    zd, td, vd = zeros_sur_la_droite(Zd, 82.5, 88.5)
    a, b = 82.5, 88.5; attendu = compte_dh(b) - compte_dh(a)
    w = (td > 85.2) & (td < 86.2); k = np.argmin(np.abs(vd[w])); creux = (float(td[w][k]), float(vd[w][k]))
    hors = 0.808517 + 85.699348j                                    # le zéro hors de la droite (Spira, 1994 ; retrouvé par dh_zeros.py)
    for _ in range(40):                                             # on l'affine par la méthode de Newton
        d = (f_dh(hors + 1e-6) - f_dh(hors - 1e-6)) / 2e-6; hors = hors - f_dh(hors) / d
    print(f"Pièce mauvaise (Davenport–Heilbronn), hauteurs {a} à {b} : {attendu:.3f} zéros attendus, {len(zd)} sur la droite ({', '.join('%.3f' % v for v in zd)}).")
    print(f"   Il en manque {attendu - len(zd):.3f}. Le creux de |Z| s'arrête à {creux[1]:+.4f} en t = {creux[0]:.3f}.")
    print(f"   Les deux absents : {hors.real:.6f} + {hors.imag:.6f} i (|f| = {abs(f_dh(hors)):.1e}) et son symétrique {1 - hors.real:.6f} + {hors.imag:.6f} i (|f| = {abs(f_dh(1 - hors.conjugate())):.1e}).")
    res["dh"] = dict(t=td[::5].tolist(), z=vd[::5].tolist(), zeros=zd.tolist(), attendu=float(attendu), creux=creux, hors=[hors.real, hors.imag])
    # ------------------------------------------------------------ 2. ζ : le bilan du balayage et les paires serrées
    entete, paires = {}, []
    for l in open(sys.argv[1]):
        if l.startswith("#"):
            if "zéros trouvés" in l: entete["zeros"] = int(l.split(":")[1])
            if "hauteur T" in l: entete["T"] = float(l.split("=")[1])
            if "attendu" in l: entete["attendu"] = float(l.split(":")[1])
            if "S(t)" in l: entete["S"] = l[2:].strip()
            if "creux" in l: entete["creux"] = int(l.split(":")[1].split(";")[0]); entete["resolus"] = int(l.split(":")[2].split(";")[0]); entete["candidats"] = int(l.split(":")[-1])
            if "blocs repris" in l: entete["repris"] = int(l.split(":")[1].split(";")[0]); entete["alertes"] = int(l.split(":")[-1])
            if "plus grande valeur" in l: entete["zmax"] = float(l.split(":")[1])
        elif l.strip(): v = l.split(); paires.append((int(v[0]), float(v[1]), float(v[2]), float(v[3])))
    P = np.array(paires); marge = (P[:, 2] - P[:, 1]) ** 2 / 2
    print(f"\nPièce bonne (ζ), jusqu'à la hauteur {entete['T']:.0f} : {entete['zeros']} zéros sur la droite, {entete['attendu']:.1f} attendus.")
    print(f"   {entete['creux']} creux de |Z| examinés, {entete['resolus']} descendent jusqu'à zéro, {entete['candidats']} candidat contre-exemple.")
    print(f"   {entete['S']}")
    N = entete["zeros"]; x = 0.05; gue = N * (math.pi ** 2 / 9 * x ** 3 - 2 * math.pi ** 4 / 225 * x ** 5)
    print(f"   {len(P)} paires d'écart inférieur à 5 % de l'écart moyen ; la loi des matrices aléatoires en prévoit {gue:.0f} ± {math.sqrt(gue):.0f}.")
    ordre = np.argsort(marge)
    print("   Les paires les plus serrées (rang, hauteur, écart Δγ, marge Δγ²/2) :")
    for i in ordre[:6]: print(f"      n° {int(P[i, 0]):>10d}   {P[i, 1]:16.6f}   {P[i, 2] - P[i, 1]:.6f}   {marge[i]:.3e}")
    rec, m = [], 1.0                                                # les records successifs en montant
    for i in range(len(P)):
        if marge[i] < m: m = marge[i]; rec.append((int(P[i, 0]), float(P[i, 1]), float(P[i, 2] - P[i, 1]), float(marge[i])))
    print("   Les records successifs en montant :"); [print(f"      n° {r[0]:>10d}   hauteur {r[1]:14.3f}   marge {r[3]:.3e}") for r in rec]
    res["zeta"] = dict(entete=entete, records=rec, npaires=len(P), gue=gue, hauteurs=P[:, 1].tolist(), marges=marge.tolist())
    # la loi attendue : parmi N zéros, le plus petit écart vaut environ (9/(π²N))^(1/3) écart moyen
    tt = np.logspace(3, math.log10(entete["T"]), 60); Nt = tt / (2 * math.pi) * np.log(tt / (2 * math.pi * math.e)) + 7 / 8
    res["loi"] = dict(t=tt.tolist(), marge=(((9 / (math.pi ** 2 * Nt)) ** (1 / 3) * 2 * math.pi / np.log(tt / (2 * math.pi))) ** 2 / 2).tolist())
    # ------------------------------------------------------------ 3. le film autour de la paire de Lehmer
    g = np.fromfile(sys.argv[2]); k0 = 6709
    assert abs(g[k0 - 1] - 7005.0629) < 1e-3 and abs(g[k0] - 7005.1006) < 1e-3
    F = film(g, k0)
    print(f"\nLe film à l'envers, autour de la paire de Lehmer (zéros n° {k0} et {k0 + 1}, écart {g[k0] - g[k0 - 1]:.6f}) :")
    print(f"   collision à l'instant {F['tc']:.4e} (simulation) ; {F['deux_corps']:.4e} (deux zéros seuls, −Δγ²/2) ; {F['voisins_figes']:.4e} (voisins figés).")
    res["film"] = dict(T1=F["T1"], Y1=F["Y1"].tolist(), T2=F["T2"], Y2=F["Y2"].tolist(), tc=F["tc"], deux_corps=F["deux_corps"], k0=k0)
    if len(sys.argv) > 3:
        d = np.loadtxt(sys.argv[3]); res["fenetre"] = dict(t=d[:, 0].tolist(), z=d[:, 1].tolist())
        w = (d[:, 0] > g[k0 - 1]) & (d[:, 0] < g[k0]); res["bosse"] = float(d[w, 1].max()); res["zmax_fenetre"] = float(np.abs(d[:, 1]).max())
        print(f"   Entre les deux zéros, Z ne monte qu'à {res['bosse']:.5f} (|Z| atteint {res['zmax_fenetre']:.2f} tout près).")
    # ------------------------------------------------------------ 4. où s'entendrait une fausse note
    print("\nUn zéro hors de la droite à la hauteur 3·10¹² (juste au-dessus de la zone vérifiée) : son onde dépasse √x à partir de")
    res["fausse_note"] = []
    for beta in (0.875, 0.75, 0.6, 0.51):
        e = math.log10(1.5e12) / (beta - 0.5); res["fausse_note"].append((beta, e)); print(f"   partie réelle {beta} : x ≈ 10^{e:.0f}")
    json.dump(res, open("par_la_fin.json", "w"))
