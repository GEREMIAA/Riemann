# Les triplets de nombres premiers entendent-ils aussi les fonctions L ? (figure musique_des_triplets.png)
# Pour un motif H = (0, a, b) (ou un quadruplet), W_H(x) = Σ_{p ≤ x} ln p · ln(p + a) · ln(p + b) sur les p où tous les
# p + a_i sont premiers (compté par triplets_rapide.c). Hardy–Littlewood : W_H(x) ≈ S(H)·x, avec la série singulière
# S(H) = Π_p (1 − ν_p/p)(1 − 1/p)^(−k), ν_p = nombre de restes distincts de H modulo p, k = nombre d'éléments.
# Prédiction (densité (1 + ε)(1 + ε′)(1 + ε″) ≈ 1 + ε + ε′ + ε″) : l'écart E_H = (W_H − S(H)·x)/√x contient
#   k·S(H) fois la musique de ζ, f = (ψ(x) − x)/√x ;
#   S(H)·c_χ(H) fois celle de L(s, χ), g_χ = ψ(x, χ)/√x, avec c_χ(H) = moyenne, sur les classes a admissibles
#   modulo q, de Σ_i χ̄(a + a_i). Pour les triplets, même un caractère impair peut compter : (0, 2, 6) impose
#   p ≡ 2 (mod 3), d'où c_χ₃ = χ₃(2) + χ₃(1) + χ₃(2) = −1, et (0, 4, 6) impose p ≡ 1, d'où c_χ₃ = +1.
# Usage : python3 musique_des_triplets.py crible_1e+10.npz sortie_triplets_1e+10.bin motifs_triplets.txt   (quelques secondes)
# Erreurs : par « glissements » des gabarits, comme pour les paires ; la synthèse sur les 50 motifs est refaite pour chaque
# glissement, parce que les motifs partagent leurs nombres premiers (l'erreur naïve, qui les croirait indépendants, est trop petite).
import sys, json, math
import numpy as np
from scipy import integrate
from musique_des_jumeaux import CAR, Filtre, moindres_carres, GLISSEMENTS

def premiers(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0]
PR = premiers(10_000_000)
def serie_singuliere(H):
    k = len(H); nu = np.array([len({a % int(p) for a in H}) for p in PR[PR <= 200]])
    pe = PR[PR <= 200].astype(float); l = np.sum(np.log(1 - nu / pe) - k * np.log(1 - 1 / pe))
    pg = PR[PR > 200].astype(float); l += np.sum(np.log(1 - k / pg) - k * np.log(1 - 1 / pg))
    return math.exp(l)
def c_chi(nom, H):
    q, v = CAR[nom]; adm = [a for a in range(q) if all(math.gcd(a + h, q) == 1 for h in H)]
    return sum(sum(complex(v[(a + h) % q]).conjugate() for h in H) for a in adm) / len(adm)

if __name__ == "__main__":
    d = np.load(sys.argv[1]); U, X = d["U"], d["X"].astype(float)
    mot = [tuple(map(int, l.split())) for l in open(sys.argv[3]) if l.strip()]; nm = len(mot)
    raw = np.fromfile(sys.argv[2], dtype=np.uint8).reshape(len(X), nm, 16)
    C = raw[:, :, :8].copy().view(np.int64)[:, :, 0]; W = raw[:, :, 8:].copy().view(np.float64)[:, :, 0]
    f = (d["psi"] - X) / np.sqrt(X); chi = {nom: d["chi"][i] / np.sqrt(X) for i, nom in enumerate(d["caracteres"])}
    F = Filtre(U, 9.0, U[-1])
    noms = ["zeta"]; gab = [f]
    for nom in CAR:
        noms.append(nom); gab.append(chi[nom].real)
        if any(abs(complex(v).imag) > 0 for v in CAR[nom][1].values()): noms.append(nom + "_im"); gab.append(chi[nom].imag)
    def systeme(dec):
        T = [F(t, dec) for t in gab]; return T, np.array([[np.real(np.vdot(a, b)) for b in T] for a in T])
    def resout(TA, y):
        T, A = TA; return np.linalg.solve(A, np.array([np.real(np.vdot(a, y)) for a in T]))
    S0 = systeme(0); Sg = [systeme(s) for s in GLISSEMENTS]
    res = dict(motifs=[]); xmax = X[-1]; GL = []          # GL : coefficients obtenus avec les gabarits glissés (le bruit)
    for k, H in enumerate(mot):
        SH = serie_singuliere(H); E = (W[:, k] - SH * X) / np.sqrt(X)
        li = integrate.quad(lambda v: math.exp(v) / np.prod([math.log(math.exp(v) + a) if a else v for a in H]), math.log(2), math.log(xmax), limit=400)[0]
        y = F(E); c0 = resout(S0, y); cg = np.array([resout(TA, y) for TA in Sg]); br = np.std(cg, axis=0); GL.append(cg)
        pr = {"zeta": len(H) * SH}
        for nom in CAR:
            c = c_chi(nom, H)
            if nom + "_im" in noms: pr[nom] = 2 * SH * c.real; pr[nom + "_im"] = -2 * SH * c.imag
            else: pr[nom] = SH * c.real
        res["motifs"].append(dict(H=list(H), S=SH, compte=int(C[-1, k]), predit_compte=SH * li, coef=dict(zip(noms, c0.tolist())),
                                  bruit=dict(zip(noms, br.tolist())), predit=pr))
        print(f"{str(H):>14} : S = {SH:.4f} ; compté {C[-1, k]:>9} / Hardy–Littlewood {SH * li:>11.0f} ({100 * (C[-1, k] / (SH * li) - 1):+.3f} %) ; "
              f"ζ {c0[0] / pr['zeta']:+.2f} ± {br[0] / pr['zeta']:.2f} ; χ₃ {c0[noms.index('chi3')] / SH:+.2f} ± {br[noms.index('chi3')] / SH:.2f} (prédit {pr['chi3'] / SH:+.2f})", flush=True)
    trip = [m for m in res["motifs"] if len(m["H"]) == 3]; it = [k for k, m in enumerate(res["motifs"]) if len(m["H"]) == 3]
    GL = np.array(GL)                                    # (motifs, glissements, gabarits)
    res["synthese"] = {}
    # Les 50 motifs partagent les mêmes nombres premiers : leurs bruits sont corrélés. L'erreur « naïve » les suppose
    # indépendants ; l'erreur « glissements » refait la synthèse entière avec chaque gabarit glissé, ce qui compte la corrélation.
    for j, nom in enumerate(noms):
        b = np.array([m["coef"][nom] for m in trip]); s = np.array([m["bruit"][nom] for m in trip]); p = np.array([m["predit"][nom] for m in trip])
        g = GL[it, :, j]; c2 = float(np.sum((b / s) ** 2)); c2g = np.sum((g / s[:, None]) ** 2, axis=0)
        d = dict(chi2_zero=c2, chi2_glissements=[float(np.mean(c2g)), float(np.std(c2g))], p_chi2=float(np.mean(c2g >= c2)), n=len(b))
        if np.any(np.abs(p) > 1e-9):
            w = (p / s ** 2) / np.sum(p ** 2 / s ** 2); kap = float(np.sum(b * w)); err = float(1 / np.sqrt(np.sum(p ** 2 / s ** 2)))
            ks = np.sum(g * w[:, None], axis=0); eg = float(np.std(ks))
            d.update(kappa=kap, err_naif=err, err=max(err, eg), err_glissements=eg, kappa_glissements=ks.tolist(), nuls=int(np.sum(np.abs(p) < 1e-9)))
            print(f"{nom:>8} : mesuré = {kap:.3f} ± {max(err, eg):.3f} × prédit ({kap / max(err, eg):.1f} σ ; erreur naïve {err:.3f}, par glissements {eg:.3f}) ; "
                  f"prédiction nulle pour {d['nuls']} motifs sur {len(b)}")
        else:
            d.update(kappa=None, err=None, nuls=len(b))
            print(f"{nom:>8} : prédit 0 pour tous les triplets ; χ² à zéro = {c2:.1f} pour {len(b)} motifs (bruit : {np.mean(c2g):.1f} ± {np.std(c2g):.1f} ; "
                  f"{100 * d['p_chi2']:.0f} % des glissements font plus)")
        res["synthese"][nom] = d
    # caractères complexes : parties réelle et imaginaire ensemble (erreur par glissements, qui compte leur corrélation)
    for nom in CAR:
        A_, B_ = res["synthese"].get(nom, {}), res["synthese"].get(nom + "_im", {})
        if A_.get("kappa") is None or B_.get("kappa") is None: continue
        wa, wb = 1 / A_["err"] ** 2, 1 / B_["err"] ** 2; wa, wb = wa / (wa + wb), wb / (wa + wb)
        ks = wa * np.array(A_["kappa_glissements"]) + wb * np.array(B_["kappa_glissements"])
        en = 1 / math.sqrt(1 / A_["err_naif"] ** 2 + 1 / B_["err_naif"] ** 2); kt = wa * A_["kappa"] + wb * B_["kappa"]
        res["synthese"][nom + "_tout"] = dict(kappa=kt, err=max(en, float(np.std(ks))), err_naif=en, err_glissements=float(np.std(ks)))
        print(f"{nom:>8} (réel et imaginaire ensemble) : {kt:.3f} ± {max(en, float(np.std(ks))):.3f} × prédit ({kt / max(en, float(np.std(ks))):.1f} σ)")
    ec = [abs(m["compte"] / m["predit_compte"] - 1) for m in trip]
    res["ecart_hl_max"] = float(max(ec)); print(f"Hardy–Littlewood, {len(trip)} triplets jusqu'à {xmax:.2e} : écart maximal {100 * max(ec):.3f} %")
    json.dump(res, open("musique_des_triplets.json", "w"), indent=1)
