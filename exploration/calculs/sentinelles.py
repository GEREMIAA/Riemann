# Les sentinelles : le zéro de la dérivée attaché à chaque paire de zéros (figure de_l_autre_cote.png, C et D).
#
# Entre deux zéros voisins sur la droite critique, la dérivée a un zéro juste à droite de la droite : la « sentinelle ».
# Modèle à deux zéros : pour une paire d'écart δ à la hauteur t, avec L = ln(t/2π) pour ζ (ln(5t/2π) pour la fonction de
# Davenport–Heilbronn), la sentinelle est à la distance
#        x = (2/L)·(1 − √(1 − u)),   u = L²δ²/16        (x ≈ L·δ²/16 quand la paire est serrée).
# Pour une paire qui a quitté la droite, ½ ± a + iγ, le même calcul donne u = −L²a²/4 : x est négatif, la sentinelle
# est passée à gauche. Une seule courbe, donc, en fonction du « carré de l'écart » : positif tant que la paire est sur
# la droite, nul quand les deux zéros se confondent, négatif quand ils l'ont quittée.
#
# On le vérifie directement, sans le modèle :
#   1. ζ : les paires serrées parmi les 22 491 premiers zéros (hauteur ≤ 20 000) ; méthode de Newton sur ζ′ ;
#   2. Davenport–Heilbronn : tous ses zéros jusqu'à la hauteur 2000, sur la droite et hors de la droite, contrôlés par
#      l'appel ; puis la sentinelle de chaque paire serrée et de chaque paire fautive ;
#   3. le compte, par le principe de l'argument, des zéros de la dérivée à gauche de la droite : ζ′ jusqu'à la hauteur
#      10 000, la dérivée de Davenport–Heilbronn jusqu'à 2000.
# Les cinq paires record de ζ (jusqu'à la hauteur 18 882 503) sont traitées à part, en quadruple précision : sentinelle.c.
#
# Usage : python3 sentinelles.py zeros_20000.bin        (sept minutes ; zeros_20000.bin vient de
#         ./zeros_au_plus_juste -z 20000 zeros_20000.bin)
import sys, json, math
import numpy as np
from dh_lib import BE, COEF, theta_dh

def hurwitz_d(s, a, N=100, M=20, bloc=4000000):
    """ζ(s, a) et sa dérivée en s, par Euler–Maclaurin (s complexe, tableau numpy)"""
    shape = np.shape(s); s = np.atleast_1d(np.asarray(s, complex)).ravel(); o0 = np.empty_like(s); o1 = np.empty_like(s)
    lk = np.log(np.arange(N) + a); w = N + a; lw = math.log(w); pas = max(1, bloc // N)
    for i in range(0, s.size, pas):
        z = s[i:i + pas]
        E = np.exp(-np.multiply.outer(z, lk)); S = E.sum(1); S1 = -(E @ lk)
        A = np.exp((1 - z) * lw) / (z - 1); B = 0.5 * np.exp(-z * lw)
        S += A + B; S1 += A * (-lw - 1 / (z - 1)) - lw * B
        poch, fact, tw, D = z.copy(), 2.0, np.exp(-(z + 1) * lw), 1 / z - lw
        for r in range(1, M + 1):
            T = BE[r - 1] / fact * poch * tw
            S += T; S1 += T * D
            u, v = z + (2 * r - 1), z + 2 * r
            poch = poch * u * v; D = D + 1 / u + 1 / v; fact *= (2 * r + 1) * (2 * r + 2); tw = tw / (w * w)
        o0[i:i + pas] = S; o1[i:i + pas] = S1
    return o0.reshape(shape), o1.reshape(shape)

def zeta_d(s, **kw): return hurwitz_d(s, 1.0, **kw)
def dh_d(s, **kw):
    s = np.asarray(s, complex); z0 = 0; z1 = 0
    for j, c in COEF.items():
        a, b = hurwitz_d(s, j / 5, **kw); z0 = z0 + c * a; z1 = z1 + c * b
    p = np.exp(-s * math.log(5))
    return p * z0, p * (z1 - math.log(5) * z0)
def Z_dh(t, **kw): return (np.exp(1j * theta_dh(t)) * dh_d(0.5 + 1j * np.asarray(t, float), **kw)[0]).real
def termes(t): return int(t / 2.5) + 60                              # nombre de termes de la somme directe à la hauteur t

def newton(FD, z, ordre, tmax, n=60, h=1e-4, borne=0.05):
    """zéros de F (ordre 0) ou de F′ (ordre 1), à partir des points z ; FD renvoie (F, F′). Renvoie (zéros, résidus)."""
    z = np.array(z, complex); N = termes(tmax)
    for _ in range(n):
        if ordre == 0: g, dg = FD(z, N=N)
        else: g = FD(z, N=N)[1]; dg = (FD(z + h, N=N)[1] - FD(z - h, N=N)[1]) / (2 * h)
        pas = g / dg; r = np.abs(pas); pas = np.where(r > borne, pas * borne / np.maximum(r, 1e-300), pas); z = z - pas
        if r.max() < 1e-12: break
    return z, np.abs(FD(z, N=N)[ordre])

def par_tranches(FD, z0, ordre, larg=250.0):
    """Newton par tranches de hauteur (le nombre de termes dépend de la hauteur)"""
    z0 = np.asarray(z0, complex); out = np.empty_like(z0); res = np.empty(len(z0))
    for a in np.arange(0.0, z0.imag.max() + larg, larg):
        m = (z0.imag >= a) & (z0.imag < a + larg)
        if m.any(): out[m], res[m] = newton(FD, z0[m], ordre, a + larg + 1)
    return out, res

def modele(L, u):
    """distance de la sentinelle à la droite, dans le modèle à deux zéros (u = L²δ²/16, ou −L²a²/4 hors de la droite)"""
    return 2 / L * (1 - np.sqrt(1 - u))

def sentinelles(FD, t, sep, L, hors):
    """t : hauteur de la paire ; sep : écart δ (sur la droite) ou demi-écart a (hors de la droite, hors = True)"""
    u = -(L * sep) ** 2 / 4 if hors else (L * sep) ** 2 / 16
    z, res = par_tranches(FD, 0.5 + modele(L, u) + 1j * t, 1)
    ok = (res < 1e-7) & (np.abs(z.imag - t) < 0.5 * 2 * np.pi / L) & ((z.real < 0.5) if hors else (z.real > 0.5))
    return u, z, ok

def tours(FD, ordre, sa, sb, ta, tb, pas=0.01, seuil=0.3):
    """nombre de zéros de F (ordre 0) ou F′ (ordre 1) dans le rectangle [sa, sb] × [ta, tb] : variation de l'argument
       le long du bord, divisée par 2π. Là où la phase tourne vite, on resserre les points."""
    def valeurs(z):
        v = np.empty(len(z), complex)
        for b in np.arange(0.0, tb + 250.0, 250.0):
            m = (z.imag >= b) & (z.imag < b + 250.0)
            if m.any(): v[m] = FD(z[m], N=termes(b + 251.0))[ordre]
        return v
    coins = [sa + 1j * ta, sb + 1j * ta, sb + 1j * tb, sa + 1j * tb, sa + 1j * ta]; total = 0.0; pire = 0.0
    for z0, z1 in zip(coins[:-1], coins[1:]):
        n = max(8, int(abs(z1 - z0) / pas)); l = np.arange(n + 1) / n; v = valeurs(z0 + (z1 - z0) * l)
        for _ in range(45):
            d = np.diff(np.angle(v)); d = (d + np.pi) % (2 * np.pi) - np.pi; gros = np.nonzero(np.abs(d) > seuil)[0]
            if len(gros) == 0: break
            ln = (l[gros] + l[gros + 1]) / 2; vn = valeurs(z0 + (z1 - z0) * ln)
            l = np.concatenate([l, ln]); v = np.concatenate([v, vn]); o = np.argsort(l); l = l[o]; v = v[o]
        assert len(gros) == 0, "phase non résolue sur le bord"
        total += d.sum(); pire = max(pire, float(np.abs(d).max()))
    return total / (2 * np.pi), pire

if __name__ == "__main__":
    res = {}
    # ------------------------------------------------------------ 1. ζ : les paires serrées des 22 491 premiers zéros
    gam = np.fromfile(sys.argv[1]); d = np.diff(gam); t = (gam[:-1] + gam[1:]) / 2; L = np.log(t / (2 * np.pi)); g = d * L / (2 * np.pi)
    m = g < 0.6
    u, z, ok = sentinelles(zeta_d, t[m], d[m], L[m], False)
    x = z.real - 0.5; k = np.argmin(x)
    print(f"ζ : {len(gam)} zéros jusqu'à la hauteur {gam[-1]:.0f} ; {m.sum()} paires d'écart inférieur à 0,6 fois l'écart moyen ; sentinelle trouvée pour {ok.sum()} d'entre elles, toutes à droite : {bool((x[ok] > 0).all())}")
    print(f"   la plus proche de la droite : {x[k]:.6e}, à la hauteur {z[k].imag:.4f} (paire d'écart {d[m][k]:.6f} ; modèle à deux zéros : {modele(L[m][k], u[k]):.6e})")
    for lim in (0.05, 0.1, 0.2, 0.4):
        q = ok & (g[m] < lim); r = x[q] / modele(L[m][q], u[q])
        print(f"   écart < {lim} fois l'écart moyen : {q.sum()} paires ; sentinelle / modèle entre {r.min():.4f} et {r.max():.4f}")
    res["zeta"] = dict(t=t[m][ok].tolist(), d=d[m][ok].tolist(), L=L[m][ok].tolist(), x=x[ok].tolist())
    # ------------------------------------------------------------ 2. Davenport–Heilbronn jusqu'à la hauteur TD
    TD, pas = 2000.0, 0.002
    tt = np.arange(0.5, TD + pas / 2, pas); Z = np.empty(len(tt))
    for a in np.arange(0.0, TD, 50.0):
        mm = (tt >= a) & (tt < a + 50.0); Z[mm] = Z_dh(tt[mm], N=termes(a + 50.0))
    Z[-1] = Z_dh(tt[-1:], N=termes(TD + 1))[0]
    i = np.nonzero(Z[:-1] * Z[1:] < 0)[0]; depart = tt[i] - Z[i] * pas / (Z[i + 1] - Z[i])
    # les creux de |Z| sans changement de signe sur la grille : minimum positif ou maximum négatif de Z
    c = np.nonzero((Z[1:-1] * Z[:-2] > 0) & (Z[1:-1] * Z[2:] > 0) & (np.abs(Z[1:-1]) < np.abs(Z[:-2])) & (np.abs(Z[1:-1]) <= np.abs(Z[2:])))[0] + 1
    z2 = (Z[c - 1] - 2 * Z[c] + Z[c + 1]) / pas ** 2; z1 = (Z[c + 1] - Z[c - 1]) / (2 * pas); tm = tt[c] - z1 / z2; zm = Z[c] - z1 ** 2 / (2 * z2)
    cache = zm / z2 <= 0                                              # le creux passe par zéro entre deux points de la grille : deux zéros sur la droite
    if cache.any(): e = np.sqrt(-2 * zm[cache] / z2[cache]); depart = np.sort(np.concatenate([depart, tm[cache] - e, tm[cache] + e]))
    sur, r0 = par_tranches(dh_d, 0.5 + 1j * depart, 0)
    assert r0.max() < 1e-9 and np.abs(sur.real - 0.5).max() < 1e-9 and (np.diff(sur.imag) > 0).all()
    sur = sur.imag; tm = tm[~cache]
    # les autres creux n'atteignent pas zéro : on cherche le zéro hors de la droite dans une boîte, à droite de la droite
    sg = np.arange(0.51, 1.6, 0.01); hg = np.arange(-0.3, 0.3001, 0.01); dep = []
    for t0 in tm:
        S, H = np.meshgrid(sg, t0 + hg); A = np.abs(dh_d(S + 1j * H, N=termes(t0 + 1))[0]); j = np.unravel_index(np.argmin(A), A.shape); dep.append(S[j] + 1j * H[j])
    hors, r0 = par_tranches(dh_d, np.array(dep), 0)
    assert r0.max() < 1e-9 and (hors.real - 0.5 > 1e-6).all() and (np.abs(hors.imag - tm) < 0.35).all() and (np.diff(hors.imag) > 0).all()
    # l'appel : θ(T)/π + la variation de l'argument de f entre 2 + iT et ½ + iT (sur Re s = 2, f reste dans le demi-plan droit)
    def appel(T):
        ch = np.linspace(2.0, 0.5, 4000) + 1j * T; ph = np.unwrap(np.angle(dh_d(ch, N=termes(T + 1))[0])); assert np.abs(np.diff(ph)).max() < 0.5
        return (theta_dh(T) + ph[-1]) / math.pi
    att = appel(TD + 0.25); trouve = int((sur < TD + 0.25).sum() + 2 * (hors.imag < TD + 0.25).sum())
    print(f"\nDavenport–Heilbronn jusqu'à la hauteur {TD:.0f} : {len(sur)} zéros sur la droite, {len(hors)} paires hors de la droite (creux de |Z| qui n'atteignent pas zéro : {len(tm)} ; creux qui cachaient deux zéros : {int(cache.sum())})")
    print(f"   l'appel : {att:.4f} zéros attendus, {trouve} trouvés ({len(sur)} + 2 × {len(hors)})")
    for T in np.arange(100.25, TD, 100.0):
        a = appel(T); n = int((sur < T).sum() + 2 * (hors.imag < T).sum()); assert abs(a - n) < 0.01, (T, a, n)
    a = hors.real - 0.5; Lh = np.log(5 * hors.imag / (2 * np.pi))
    uh, zh, okh = sentinelles(dh_d, hors.imag, a, Lh, True)
    xh = zh.real - 0.5; r = xh[okh] / modele(Lh[okh], uh[okh])
    print(f"   paires hors de la droite : sentinelle trouvée pour {okh.sum()} sur {len(hors)}, toutes à gauche : {bool((xh[okh] < 0).all())} ; sentinelle / modèle entre {r.min():.4f} et {r.max():.4f}")
    print("   les plus écartées : " + " ; ".join(f"{hors[j].real:.4f} + {hors[j].imag:.3f} i → {zh[j].real:.4f}" for j in np.argsort(-a)[:4]))
    print("   les plus proches de la droite : " + " ; ".join(f"{hors[j].real:.6f} + {hors[j].imag:.3f} i → {zh[j].real:.6f}" for j in np.argsort(a)[:4]))
    dd = np.diff(sur); ts = (sur[:-1] + sur[1:]) / 2; Ls = np.log(5 * ts / (2 * np.pi)); gs = dd * Ls / (2 * np.pi)
    voisins = np.array([((hors.imag > p) & (hors.imag < q)).any() for p, q in zip(sur[:-1], sur[1:])])    # pas de paire fautive entre les deux
    ms = (gs < 0.6) & ~voisins
    us, zs, oks = sentinelles(dh_d, ts[ms], dd[ms], Ls[ms], False)
    xs = zs.real - 0.5
    print(f"   paires serrées sur la droite (écart < 0,6) : {ms.sum()} ; sentinelle trouvée pour {oks.sum()}, toutes à droite : {bool((xs[oks] > 0).all())}")
    res["dh"] = dict(T=TD, sur=len(sur), attendu=att, hors=[(float(h.real), float(h.imag)) for h in hors], x_hors=xh.tolist(), ok_hors=okh.tolist(), L_hors=Lh.tolist(),
                     t=ts[ms][oks].tolist(), d=dd[ms][oks].tolist(), L=Ls[ms][oks].tolist(), x=xs[oks].tolist())
    json.dump(res, open("sentinelles.json", "w"))
    # ------------------------------------------------------------ 3. le compte à gauche de la droite
    n, saut = tours(dh_d, 1, -1.0, 0.5, 1.0, TD + 0.25)
    print(f"\nZéros de la dérivée à gauche de la droite (rectangle −1 < Re s < ½, principe de l'argument) :")
    print(f"   Davenport–Heilbronn, hauteurs 1 à {TD + 0.25} : {n:.4f} (paires hors de la droite : {int((hors.imag < TD + 0.25).sum())}) ; plus grand saut de phase {saut:.2f}")
    res["gauche_dh"] = (TD + 0.25, n)
    json.dump(res, open("sentinelles.json", "w"))
    TZ = 10000.5
    n, saut = tours(zeta_d, 1, -1.0, 0.5, 1.0, TZ)
    print(f"   ζ′, hauteurs 1 à {TZ} : {n:+.4f} ({int((gam < TZ).sum())} zéros de ζ sur la droite) ; plus grand saut de phase {saut:.2f}")
    res["gauche_zeta"] = (TZ, n)
    json.dump(res, open("sentinelles.json", "w"))
