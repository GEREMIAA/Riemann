# Les jumeaux seuls, enfin entendus — et les notes des fonctions L (figure musique_des_jumeaux.png).
# On écoute l'écart des paires (p, p + h) à Hardy–Littlewood, E_h(u) = (W_h(x) − S(h)·x)/√x, u = ln x, avec un
# « filtre adapté » (comme LIGO pour les ondes gravitationnelles) : on garde toutes les fréquences de 50 à 6 000, là où le
# bruit propre des paires est faible devant la musique, et on projette sur des gabarits :
#   f(u) = (ψ(x) − x)/√x                      la musique des zéros de ζ,      volume prédit 2S(h) ;
#   g_χ(u) = ψ(x, χ)/√x                       la musique des zéros de L(s, χ), volume prédit S(h)·c_χ(h), avec
#   c_χ(h) = moyenne, sur les classes a admissibles modulo q, de χ̄(a) + χ̄(a + h)  (densité (1 + ε)(1 + ε') ≈ 1 + ε + ε').
#   Pour q premier et χ pair : c_χ(h) = −2 χ̄(h)/(q − 2) ; pour χ impair, c = 0 ; pour χ₈ et χ₁₂ aussi (tests témoins).
# Le bruit se mesure par « glissements » : on décale les gabarits le long de u, ce qui détruit l'accord avec les vraies
# notes, et on regarde de combien la mesure varie (même méthode que LIGO).
# Enfin, l'épreuve à l'aveugle : avec la prédiction fixée, on écoute les jumeaux nouveaux, entre 10¹⁰ et 10¹², comptés par
# jumeaux_rapide.c ; le gabarit vient alors des zéros eux-mêmes : f(u) = −2 Re Σ_γ e^{iγu}/(½ + iγ).
# Usage : python3 musique_des_jumeaux.py crible_1e+10.npz zeros_100000.npy [sortie_1e+12.bin grille_1e+12.bin]
import sys, json, math
import numpy as np

C2 = 0.66016181584686957392781211
def S(h):
    if h % 2: return 0.0
    s, m, p = 2 * C2, h, 3
    while m > 1 and p <= h:
        if m % p == 0:
            s *= (p - 1) / (p - 2)
            while m % p == 0: m //= p
        p += 2
    return s
W3 = complex(-0.5, math.sqrt(3) / 2)
CAR = {"chi3": (3, {1: 1, 2: -1}), "chi4": (4, {1: 1, 3: -1}), "chi5": (5, {1: 1, 2: -1, 3: -1, 4: 1}),
       "chi5i": (5, {1: 1, 2: 1j, 4: -1, 3: -1j}), "chi7c": (7, {1: 1, 3: W3, 2: W3 ** 2, 6: 1, 4: W3, 5: W3 ** 2}),
       "chi8": (8, {1: 1, 3: -1, 5: -1, 7: 1}), "chi12": (12, {1: 1, 5: -1, 7: -1, 11: 1}),
       "chi13": (13, {a: (1 if a in (1, 3, 4, 9, 10, 12) else -1) for a in range(1, 13)})}
def c_chi(nom, h):
    q, v = CAR[nom]; adm = [a for a in range(q) if math.gcd(a, q) == 1 and math.gcd(a + h, q) == 1]
    return sum(complex(v[a]).conjugate() + complex(v[(a + h) % q]).conjugate() for a in adm) / len(adm)

BANDE = (50.0, 6000.0)
class Filtre:
    """produits scalaires dans la bande de fréquences, après une fenêtre de Hann sur u ∈ [u0, u1]"""
    def __init__(self, U, u0, u1):
        self.m = (U >= u0) & (U <= u1); n = int(self.m.sum()); du = U[1] - U[0]
        self.w = np.hanning(n); fr = 2 * np.pi * np.fft.rfftfreq(n, du); self.garde = (fr >= BANDE[0]) & (fr <= BANDE[1])
    def __call__(self, y, decalage=0):
        z = y[self.m]; z = np.roll(z, decalage) if decalage else z
        return np.fft.rfft((z - z.mean()) * self.w)[self.garde]
def moindres_carres(T, y):
    """coefficients c minimisant ‖y − Σ c_i T_i‖² (vecteurs complexes de la bande)"""
    A = np.array([[np.real(np.vdot(a, b)) for b in T] for a in T]); r = np.array([np.real(np.vdot(a, y)) for a in T])
    return np.linalg.solve(A, r)
GLISSEMENTS = [int(s) for s in np.linspace(1500, 26000, 50)]            # décalages, en pas de 0,0005 (de 0,75 à 13 en u)

def gabarit_zeros(U, zeros, gmax=7000.0):
    g = zeros[zeros < gmax]; a = 1 / (0.5 + 1j * g); out = np.zeros(len(U))
    for i in range(0, len(U), 2000):
        out[i:i + 2000] = -2 * np.real(np.exp(1j * np.outer(U[i:i + 2000], g)) @ a)
    return out

if __name__ == "__main__":
    d = np.load(sys.argv[1]); zeros = np.load(sys.argv[2]); res = {}
    U, X, HS = d["U"], d["X"].astype(float), [int(h) for h in d["HS"]]; Sh = np.array([S(h) for h in HS])
    f = (d["psi"] - X) / np.sqrt(X); E = (d["W"] - Sh[:, None] * X[None, :]) / np.sqrt(X)[None, :]
    chi = {nom: d["chi"][i] / np.sqrt(X) for i, nom in enumerate(d["caracteres"])}
    F = Filtre(U, 9.0, U[-1])
    # gabarits : ζ, puis chaque caractère (partie réelle, et partie imaginaire s'il est complexe)
    noms = ["zeta"]; gab = [f]
    for nom in CAR:
        noms.append(nom); gab.append(chi[nom].real)
        if any(abs(complex(v).imag) > 0 for v in CAR[nom][1].values()): noms.append(nom + "_im"); gab.append(chi[nom].imag)
    def systeme(dec):
        T = [F(t, dec) for t in gab]; A = np.array([[np.real(np.vdot(a, b)) for b in T] for a in T]); return T, A
    Ey = [F(e) for e in E]
    def resout(TA, y):
        T, A = TA; return np.linalg.solve(A, np.array([np.real(np.vdot(a, y)) for a in T]))
    S0 = systeme(0); Sg = [systeme(s) for s in GLISSEMENTS]
    res["paires"] = []; GL = []                      # GL : coefficients obtenus avec les gabarits glissés (le bruit)
    for k, h in enumerate(HS):
        c0 = resout(S0, Ey[k]); gl = np.array([resout(TA, Ey[k]) for TA in Sg]); bruit = gl.std(axis=0); GL.append(gl)
        if h == 2: res["glissements_jumeaux"] = (gl[:, 0] / (2 * Sh[k])).tolist()
        r = dict(h=h, S=Sh[k], coef=dict(zip(noms, c0.tolist())), bruit=dict(zip(noms, bruit.tolist())),
                 predit={"zeta": 2 * Sh[k]})
        for nom in CAR:
            c = c_chi(nom, h)
            if nom + "_im" in noms: r["predit"][nom] = 2 * Sh[k] * c.real; r["predit"][nom + "_im"] = -2 * Sh[k] * c.imag
            else: r["predit"][nom] = Sh[k] * c.real
        res["paires"].append(r)
        print(f"h = {h:>2} : ζ {c0[0] / (2 * Sh[k]):+.3f} ± {bruit[0] / (2 * Sh[k]):.3f} (prédit 1) ; χ₅ {c0[noms.index('chi5')] / Sh[k]:+.2f} ± {bruit[noms.index('chi5')] / Sh[k]:.2f}"
              f" (prédit {c_chi('chi5', h).real:+.2f})", flush=True)
    # synthèse : pour chaque gabarit, la pente « mesuré = κ × prédit » sur les 30 écarts, et pour les témoins le χ² à zéro.
    # Les 30 écarts partagent les mêmes nombres premiers : leurs bruits sont corrélés. L'erreur « naïve » les suppose
    # indépendants ; l'erreur « glissements » refait la synthèse entière avec chaque gabarit glissé, ce qui compte la corrélation.
    res["synthese"] = {}; GL = np.array(GL)              # (écarts, glissements, gabarits)
    for i, nom in enumerate(noms):
        b = np.array([p["coef"][nom] for p in res["paires"]]); s = np.array([p["bruit"][nom] for p in res["paires"]])
        pr = np.array([p["predit"][nom] for p in res["paires"]])
        g = GL[:, :, i]; c2 = float(np.sum((b / s) ** 2)); c2g = np.sum((g / s[:, None]) ** 2, axis=0)
        dd = dict(chi2_zero=c2, chi2_glissements=[float(np.mean(c2g)), float(np.std(c2g))], p_chi2=float(np.mean(c2g >= c2)), n=len(b))
        if np.any(np.abs(pr) > 1e-12):
            w = (pr / s ** 2) / np.sum(pr ** 2 / s ** 2); kap = float(np.sum(b * w)); err = float(1 / np.sqrt(np.sum(pr ** 2 / s ** 2)))
            ks = np.sum(g * w[:, None], axis=0); eg = float(np.std(ks))
            dd.update(kappa=kap, err_naif=err, err=max(err, eg), err_glissements=eg, kappa_glissements=ks.tolist())
            print(f"{nom:>8} : mesuré = {kap:.3f} ± {max(err, eg):.3f} × prédit   (signal à {kap / max(err, eg):.1f} σ ; erreur naïve {err:.3f}, par glissements {eg:.3f})")
        else:
            dd.update(kappa=None, err=None)
            print(f"{nom:>8} : prédit 0 ; χ² à zéro = {c2:.1f} pour {len(b)} écarts (bruit : {np.mean(c2g):.1f} ± {np.std(c2g):.1f} ; {100 * dd['p_chi2']:.0f} % des glissements font plus)")
        res["synthese"][nom] = dd
    # caractères complexes : parties réelle et imaginaire ensemble (erreur par glissements, qui compte leur corrélation)
    for nom in CAR:
        A_, B_ = res["synthese"].get(nom, {}), res["synthese"].get(nom + "_im", {})
        if A_.get("kappa") is None or B_.get("kappa") is None: continue
        wa, wb = 1 / A_["err"] ** 2, 1 / B_["err"] ** 2; wa, wb = wa / (wa + wb), wb / (wa + wb)
        ks = wa * np.array(A_["kappa_glissements"]) + wb * np.array(B_["kappa_glissements"])
        en = 1 / math.sqrt(1 / A_["err_naif"] ** 2 + 1 / B_["err_naif"] ** 2); kt = wa * A_["kappa"] + wb * B_["kappa"]
        res["synthese"][nom + "_tout"] = dict(kappa=kt, err=max(en, float(np.std(ks))), err_naif=en, err_glissements=float(np.std(ks)))
        print(f"{nom:>8} (réel et imaginaire ensemble) : {kt:.3f} ± {max(en, float(np.std(ks))):.3f} × prédit ({kt / max(en, float(np.std(ks))):.1f} σ)")
    # jumeaux seuls (h = 2) : ζ et χ₅ ensemble
    p2 = res["paires"][0]
    res["jumeaux"] = dict(zeta=p2["coef"]["zeta"] / (2 * Sh[0]), zeta_err=p2["bruit"]["zeta"] / (2 * Sh[0]))
    print(f"jumeaux seuls : musique de ζ = {res['jumeaux']['zeta']:.2f} ± {res['jumeaux']['zeta_err']:.2f} (prédit 1)")
    # le gabarit tiré des zéros reproduit-il celui du crible ? (contrôle sur [10³, 10¹⁰])
    fz = gabarit_zeros(U, zeros); a, b = F(f), F(fz)
    res["controle_gabarit"] = float(np.real(np.vdot(a, b)) / np.sqrt(np.real(np.vdot(a, a)) * np.real(np.vdot(b, b))))
    print(f"gabarit des zéros contre gabarit du crible (bande {BANDE[0]:.0f}–{BANDE[1]:.0f}) : corrélation {res['controle_gabarit']:.5f}")
    # le bruit propre grandit-il avec ln x ? écart-type du résidu filtré par tranches de u (jumeaux)
    m = F.m; z = E[0][m] - 2 * Sh[0] * f[m]; Z = np.fft.rfft((z - z.mean()) * F.w); Z[~F.garde] = 0; rz = np.fft.irfft(Z, m.sum())
    uu = U[m]; res["bruit_par_tranche"] = []
    for lo_, hi_ in [(10, 12.5), (12.5, 15), (15, 17.5), (17.5, 20), (20, 22.5)]:
        sel = (uu >= lo_) & (uu < hi_)
        res["bruit_par_tranche"].append(dict(u=(lo_ + hi_) / 2, ecart_type=float(np.sqrt(np.mean(rz[sel] ** 2) / np.mean(F.w[sel] ** 2)))))
    print("bruit propre filtré des jumeaux, par tranche de u :", [(t["u"], round(t["ecart_type"], 2)) for t in res["bruit_par_tranche"]])
    # l'épreuve à l'aveugle : les jumeaux nouveaux, de 10¹⁰ à 10¹²
    if len(sys.argv) > 4:
        Xg = np.fromfile(sys.argv[4], dtype=np.int64); raw = np.fromfile(sys.argv[3], dtype=np.uint8).reshape(-1, 48)
        Cn = raw[:, :24].copy().view(np.int64).reshape(-1, 3); Wn = raw[:, 24:].copy().view(np.float64).reshape(-1, 3)
        Un = U[0] + 0.0005 * np.arange(len(Xg))                                                # même grille que le crible
        assert np.array_equal(Xg[:len(X)], d["X"]), "grilles différentes"
        Xf = Xg.astype(float); fzn = gabarit_zeros(Un, zeros)
        res["aveugle"] = {}; SLn = []; Bn = []
        for k, h in enumerate((2, 4, 6)):
            En = (Wn[:, k] - S(h) * Xf) / np.sqrt(Xf)
            Fn = Filtre(Un, math.log(1e10), Un[-1])
            b0 = moindres_carres([Fn(fzn)], Fn(En))[0] / (2 * S(h))
            sl = [moindres_carres([Fn(fzn, s)], Fn(En))[0] / (2 * S(h)) for s in np.linspace(800, 8000, 40).astype(int)]
            # et toute la plage, de 10³ à 10¹²
            Ft = Filtre(Un, 9.0, Un[-1]); bt = moindres_carres([Ft(fzn)], Ft(En))[0] / (2 * S(h))
            st = [moindres_carres([Ft(fzn, s)], Ft(En))[0] / (2 * S(h)) for s in GLISSEMENTS]
            res["aveugle"][str(h)] = dict(nouveau=float(b0), nouveau_err=float(np.std(sl)), total=float(bt), total_err=float(np.std(st))); SLn.append(sl); Bn.append(b0)
            print(f"h = {h} : jumeaux nouveaux (10¹⁰ → 10¹²) {b0:.2f} ± {np.std(sl):.2f} ; toute la plage (10³ → 10¹²) {bt:.2f} ± {np.std(st):.2f}   (prédit 1)")
        # h = 2, 4, 6 ensemble : moyenne pondérée, erreur par glissements (les trois écarts partagent leurs nombres premiers)
        SLn = np.array(SLn); w = 1 / SLn.std(axis=1) ** 2; w /= w.sum(); bc = float(np.dot(w, Bn))
        res["aveugle"]["ensemble"] = dict(nouveau=bc, err_naif=float(1 / np.sqrt(np.sum(1 / SLn.std(axis=1) ** 2))), err=float(np.std(w @ SLn)))
        print(f"h = 2, 4, 6 ensemble, jumeaux nouveaux : {bc:.2f} ± {res['aveugle']['ensemble']['err']:.2f} (erreur naïve {res['aveugle']['ensemble']['err_naif']:.2f})")
        # le rapport signal sur bruit selon la borne x_max (que gagne-t-on à monter ?)
        res["gain"] = []
        En = (Wn[:, 0] - S(2) * Xf) / np.sqrt(Xf)
        for umax in np.arange(16.0, Un[-1] + 1e-9, 1.0):
            Fm = Filtre(Un, 9.0, umax); b0 = moindres_carres([Fm(fzn)], Fm(En))[0] / (2 * S(2))
            sl = np.std([moindres_carres([Fm(fzn, s)], Fm(En))[0] / (2 * S(2)) for s in np.linspace(1200, 9000, 30).astype(int)])
            res["gain"].append(dict(xmax=float(math.exp(umax)), beta=float(b0), err=float(sl)))
            print(f"jusqu'à x = {math.exp(umax):.1e} : jumeaux {b0:.2f} ± {sl:.2f}  ({b0 / sl:.1f} σ)", flush=True)
    json.dump(res, open("musique_des_jumeaux.json", "w"), indent=1)
