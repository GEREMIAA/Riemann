# De l'autre côté de la droite : le critère de Speiser (figure de_l_autre_cote.png).
#
# Speiser (1934) : l'hypothèse de Riemann équivaut à « la dérivée ζ′(s) n'a aucun zéro à gauche de la droite critique,
# dans la bande 0 < Re s < ½ ». Levinson et Montgomery (1974) l'ont rendu quantitatif : à gauche de la droite, ζ′ a
# autant de zéros que ζ, à un petit nombre près. Chaque zéro fautif de ζ en fabrique donc un pour ζ′, de l'autre côté.
#
# On regarde ce côté-là sur la pièce bonne et sur la pièce mauvaise :
#   - ζ : on compte les zéros de ζ′ dans le rectangle −1 < Re s < ½, 1 < Im s < T (principe de l'argument) ;
#   - la fonction de Davenport–Heilbronn f, qui a la symétrie de ζ et des zéros hors de la droite : même compte pour f′.
# Puis on localise tous les zéros des deux dérivées jusqu'à la hauteur 205 (minimums de |g′| sur une grille, affinés
# par la méthode de Newton), pour la figure.
#
# Le script calcule aussi deux autres signatures « un seul cas suffit » avec nos propres zéros :
#   - les coefficients de Li, λ_n = Σ_ρ [1 − (1 − 1/ρ)^n] : l'hypothèse équivaut à λ_n ≥ 0 pour tout n ;
#   - l'intégrale de Balazard, Saias et Yor, ∫ ln|ζ(½ + it)| / (¼ + t²) dt : l'hypothèse équivaut à « elle vaut 0 ».
#
# Enfin, pour un même zéro fautif (partie réelle ¾, hauteur 3·10¹², juste au-dessus de la zone vérifiée), il estime à
# partir d'où chaque forme de l'hypothèse le verrait : ce sont des ordres de grandeur, obtenus en comparant la
# contribution de ce zéro à la marge du critère.
#
# Suite : sentinelles.py (le zéro de la dérivée attaché à chaque paire de zéros) et sentinelle.c.
#
# Usage : python3 de_l_autre_cote.py zeros_20000.bin        (quatre minutes ; zeros_20000.bin vient de
#         ./zeros_au_plus_juste -z 20000 zeros_20000.bin)
import sys, json, math
import numpy as np
from dh_lib import f_dh, zeta

H = 1e-5
def derivee(F):
    return lambda s, **kw: (F(s + H, **kw) - F(s - H, **kw)) / (2 * H)

def tours(G, sa, sb, ta, tb, pas=0.002, **kw):
    """nombre de zéros de G dans le rectangle [sa, sb] × [ta, tb] : variation de l'argument le long du bord, divisée par 2π"""
    def cote(z0, z1):
        n = max(8, int(abs(z1 - z0) / pas)); return z0 + (z1 - z0) * np.arange(n) / n
    bord = np.concatenate([cote(sa + 1j * ta, sb + 1j * ta), cote(sb + 1j * ta, sb + 1j * tb), cote(sb + 1j * tb, sa + 1j * tb), cote(sa + 1j * tb, sa + 1j * ta), [sa + 1j * ta]])
    ph = np.angle(G(bord, **kw)); d = np.diff(ph); d = (d + np.pi) % (2 * np.pi) - np.pi
    return float(d.sum() / (2 * np.pi)), float(np.abs(d).max())

def zeros_de(G, s0, s1, t0, t1, pas=0.02, **kw):
    """zéros de G dans le rectangle : minimums locaux de |G| sur une grille, puis Newton"""
    sg = np.arange(s0, s1 + pas / 2, pas); out = []
    for a in np.arange(t0, t1, 50.0):
        tg = np.arange(a - pas, min(a + 50.0, t1) + 1.5 * pas, pas); S, T = np.meshgrid(sg, tg); A = np.abs(G(S + 1j * T, **kw))
        m = (A[1:-1, 1:-1] < A[:-2, 1:-1]) & (A[1:-1, 1:-1] < A[2:, 1:-1]) & (A[1:-1, 1:-1] < A[1:-1, :-2]) & (A[1:-1, 1:-1] < A[1:-1, 2:])
        for i, j in zip(*np.nonzero(m)):
            z = complex(S[i + 1, j + 1], T[i + 1, j + 1])
            for _ in range(60):
                g = complex(G(np.array([z]), **kw)[0]); dg = complex((G(np.array([z + 1e-4]), **kw)[0] - G(np.array([z - 1e-4]), **kw)[0]) / 2e-4)
                if dg == 0: break
                pasn = g / dg; z -= pasn
                if abs(pasn) < 1e-11: break
            if abs(complex(G(np.array([z]), **kw)[0])) < 1e-6 and s0 - 0.05 < z.real < s1 + 0.05 and t0 <= z.imag < t1 and all(abs(z - w) > 1e-5 for w in out): out.append(z)
    return sorted(out, key=lambda z: z.imag)

def seuils(beta=0.75, gam=3e12):
    """à partir d'où chaque côté verrait un zéro fautif β + iγ (et ses trois symétriques) : ordres de grandeur"""
    b = beta - 0.5; out = {}
    out["rang"] = gam / (2 * math.pi) * math.log(gam / (2 * math.pi * math.e)) + 7 / 8           # son numéro, sur la droite ou de l'autre côté
    c = math.log(gam / (2 * math.pi)) / 2; b0 = 2 * b                                           # le film : la paire, en x = 2γ ± i·b0, tombe vers l'axe à la vitesse c + 1/b
    out["film"] = (b0 / c - math.log(1 + c * b0) / c ** 2, b0 ** 2 / 2)                         # (champ moyen des voisins + attraction du zéro symétrique) ; borne de de Bruijn
    out["onde"] = (gam / 2) ** (1 / b)                                                          # l'onde 2x^β/γ dépasse √x
    lx = 100.0
    for _ in range(200): lx = (math.log(gam / (16 * math.pi)) + 2 * math.log(lx)) / b           # 2x^β/(γ ln x) = √x ln x/8π (Schoenfeld)
    out["schoenfeld_log10"] = lx / math.log(10)
    out["robin_chiffres"] = ((math.sqrt(2) - 1) * gam ** 2) ** (1 / b) / math.log(10)           # 2x^(β−1)/γ² = 2(√2−1)/√x, et n ≈ e^x
    n = 1e20
    for _ in range(200): n = gam ** 2 / b * math.log(n * math.log(n) / 4)                       # (1 + b/γ²)^n = (n/4) ln n
    out["li"] = n
    out["bsy"] = 4 * math.pi * b / gam ** 2                                                     # 2π Σ ln|ρ/(1−ρ)| sur les deux zéros de droite
    return out

if __name__ == "__main__":
    res = {}
    dz, df = derivee(zeta), derivee(f_dh)
    # ------------------------------------------------------------ 1. le compte à gauche de la droite
    print("Zéros de la dérivée à gauche de la droite critique (rectangle −1 < Re s < ½) :")
    res["gauche_zeta"] = []
    for T in (205.5, 500.5, 1000.5):
        n, saut = tours(dz, -1.0, 0.5, 1.0, T, pas=0.001, N=420); res["gauche_zeta"].append((T, n))
        print(f"   ζ′, hauteurs 1 à {T} : {n:+.4f} zéro (plus grand saut de phase le long du bord : {saut:.2f} radian)")
    n_f, saut = tours(f_dh, 0.0, 0.49, 1.0, 205.5, pas=0.001); n_df, saut2 = tours(df, -1.0, 0.5, 1.0, 205.5, pas=0.001)     # 0,49 : on évite les zéros posés sur la droite
    print(f"   Davenport–Heilbronn, hauteurs 1 à 205,5 : f a {n_f:.4f} zéros à gauche (bande 0 < Re s < 0,49), f′ en a {n_df:.4f} (sauts {saut:.2f} et {saut2:.2f})")
    res["gauche_dh"] = dict(f=n_f, df=n_df)
    # ------------------------------------------------------------ 2. la carte des zéros jusqu'à la hauteur 205
    T = 205.0
    zz = zeros_de(dz, -1.0, 4.0, 1.0, T, N=150); zf = zeros_de(df, -1.0, 4.0, 1.0, T)
    hors = [z for z in zeros_de(f_dh, 0.0, 1.0, 1.0, T) if abs(z.real - 0.5) > 1e-4]
    print(f"\nCarte jusqu'à la hauteur {T:.0f} :")
    print(f"   ζ′ : {len(zz)} zéros, dont {sum(1 for z in zz if z.real < 0.5)} à gauche ; les premiers : " + ", ".join(f"{z.real:.4f} + {z.imag:.4f} i" for z in zz[:3]) + f" ; le plus proche de la droite : Re = {min(z.real for z in zz):.4f}")
    g = [z for z in zf if z.real < 0.5]
    print(f"   f′ (Davenport–Heilbronn) : {len(zf)} zéros, dont {len(g)} à gauche : " + ", ".join(f"{z.real:.4f} + {z.imag:.3f} i" for z in g))
    print(f"   f : {len(hors)} zéros hors de la droite : " + ", ".join(f"{z.real:.4f} + {z.imag:.3f} i" for z in hors))
    res["carte"] = dict(T=T, dzeta=[(z.real, z.imag) for z in zz], df=[(z.real, z.imag) for z in zf], hors=[(z.real, z.imag) for z in hors])
    if len(sys.argv) > 1:
        gam = np.fromfile(sys.argv[1])
        # -------------------------------------------------------- 3. les coefficients de Li, avec nos zéros
        th = 2 * np.arctan(1 / (2 * gam)); Tm = gam[-1]                   # 1 − 1/ρ = e^(iθ) pour ρ = ½ + iγ
        def li(n): return 2 * np.sum(1 - np.cos(n * th)) + n * n / (2 * math.pi) * (math.log(Tm / (2 * math.pi)) + 1) / Tm       # + les zéros au-dessus de Tm
        res["li"] = [(n, float(li(n))) for n in list(range(1, 21)) + list(range(25, 2001, 25))]
        print(f"\nCoefficients de Li avec {len(gam)} zéros : λ_1 = {li(1):.6f} (valeur connue : 0,023096), λ_2 = {li(2):.6f} (0,092346), λ_10 = {li(10):.4f}, λ_100 = {li(100):.2f}, λ_2000 = {li(2000):.1f}")
        print(f"   tous positifs de n = 1 à 2000 : {all(li(n) > 0 for n in range(1, 2001))}")
        # -------------------------------------------------------- 4. l'intégrale de Balazard, Saias et Yor
        # entre deux zéros consécutifs, ln|ζ(½ + it)| est lisse ; près des zéros, la singularité logarithmique s'intègre
        # exactement : on retire ln|t − γ| pour les deux zéros voisins, et on rajoute son intégrale.
        def bsy(Tmax, n=40):
            x, w = np.polynomial.legendre.leggauss(n); tot = 0.0; bords = np.concatenate([[0.0], gam[gam < Tmax], [Tmax]])
            for a, b in zip(bords[:-1], bords[1:]):
                t = 0.5 * (b - a) * x + 0.5 * (b + a); wt = 0.5 * (b - a) * w
                v = np.log(np.abs(zeta(0.5 + 1j * t, N=max(100, int(Tmax / 2.5) + 60)))) / (0.25 + t * t)
                la = np.log(np.maximum(t - a, 1e-300)) / (0.25 + a * a) if a > 0 else 0.0; lb = np.log(np.maximum(b - t, 1e-300)) / (0.25 + b * b) if b < Tmax else 0.0
                tot += np.sum(wt * (v - la - lb)); L = b - a
                if a > 0: tot += (L * math.log(L) - L) / (0.25 + a * a)
                if b < Tmax: tot += (L * math.log(L) - L) / (0.25 + b * b)
            return 2 * tot
        res["bsy"] = [(Tm2, float(bsy(Tm2))) for Tm2 in (100.0, 300.0, 1000.0)]
        print("\nIntégrale de Balazard, Saias et Yor, limitée à |t| < T : " + " ; ".join(f"T = {a:.0f} : {b:+.5f}" for a, b in res["bsy"]) + "   (elle doit tendre vers 0)")
    # ------------------------------------------------------------ 5. à partir d'où chaque côté verrait le zéro fautif de référence
    s = seuils(); res["seuils"] = s
    print(f"\nZéro fautif de référence, ¾ + 3·10¹² i :")
    print(f"   sur la droite et de l'autre côté : à son rang, {s['rang']:.3e} ; le film : collision vers l'instant {s['film'][0]:.3f} (au plus {s['film'][1]:.3f})")
    print(f"   nombres premiers : son onde dépasse √x vers x = {s['onde']:.1e}, et la borne de Schoenfeld vers 10^{s['schoenfeld_log10']:.1f}")
    print(f"   diviseurs (Robin) : pour un nombre de {s['robin_chiffres']:.1e} chiffres ; coefficients de Li : vers n = {s['li']:.1e} ; intégrale : elle vaudrait {s['bsy']:.2e}")
    json.dump(res, open("de_l_autre_cote.json", "w"))
