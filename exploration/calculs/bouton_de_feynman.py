# Le bouton de Feynman (figure bouton_de_feynman.png), à partir des comptages de liouville_hasard.py.
# 1. Le cercle des Liouville. Pour z = e^{iθ}, S(z, x) = Σ_{n ≤ x} z^Ω(n). La méthode de Selberg–Delange (un théorème)
#    donne S(z, x) ≈ x (ln x)^(z − 1) [μ₀(z) + μ₁(z)/ln x], avec μ₀ = G(z)/Γ(z), G(z) = Π_p (1 − z/p)^(−1) (1 − 1/p)^z,
#    μ₁ = G(z) [zγ + z(1 − z) Σ_p ln p / ((p − 1)(p − z)) − 1] / Γ(z − 1).
#    En z = −1 (la fonction de Liouville), 1/Γ s'annule : tout le terme principal disparaît, il ne reste que les fluctuations
#    de l'ordre de √x, et dire qu'elles restent de cet ordre, c'est l'hypothèse de Riemann.
# 2. Tourner le bouton : z réel près de −1. Le terme principal vaut environ −(z + 1)·ζ(2)·x/(ln x)², et finit par écraser √x.
# 3. Le hasard : la vraie somme M(x) de Möbius contre des « Möbius au hasard » (signes tirés à pile ou face, Wintner 1944).
#    Même taille √x, mais le spectre (transformée de Fourier en ln x) les sépare : des notes pour M, un bruit pour le hasard.
#    Formule explicite : M(x) ≈ Σ_ρ x^ρ / (ρ ζ'(ρ)) ; chaque zéro donne une note de volume 2/|ρ ζ'(ρ)|.
# Usage : python3 bouton_de_feynman.py liouville_1e+09.npz zeros_100000.npy
import sys, json, math
import numpy as np
from scipy.special import rgamma                        # 1/Γ, nulle aux entiers ≤ 0
from auto_imitation import zeta                                   # ζ par Euler–Maclaurin (même dossier)

d = np.load(sys.argv[1]); zeros = np.load(sys.argv[2])
U, X, Nk = d["U"], d["X"].astype(float), d["Nk"].astype(float); K = Nk.shape[1]
def premiers(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0].astype(float)
P = premiers(2_000_000); lP = np.log(P)
def selberg_delange(z, x):
    """S(z, x) ≈ x (ln x)^(z − 1) [μ₀(z) + μ₁(z)/ln x], pour un tableau de z et un tableau de x"""
    zz = np.atleast_1d(np.asarray(z, complex)); x = np.asarray(x, float); lx = np.log(x)
    G = np.exp(np.array([np.sum(-np.log(1 - w / P) + w * np.log(1 - 1 / P)) for w in zz]))
    T = np.array([np.sum(lP / ((P - 1) * (P - w))) for w in zz])
    mu0 = G * rgamma(zz); mu1 = G * (zz * 0.5772156649015329 + zz * (1 - zz) * T - 1) * rgamma(zz - 1)
    pw = np.exp(np.multiply.outer(zz - 1, np.log(lx)))
    return pw * x[None, :] * (mu0[:, None] + mu1[:, None] / lx[None, :])
res = {}; j = len(X) - 1; x = X[j]; rx = math.sqrt(x)
L = Nk @ ((-1.0) ** np.arange(K))
# 1. le cercle
th = np.unique(np.concatenate([np.linspace(0, 2 * np.pi, 721), np.pi + np.linspace(-0.05, 0.05, 201)]))
z = np.exp(1j * th); Sx = (Nk[j] * z[:, None] ** np.arange(K)).sum(1)
sd = selberg_delange(z, np.array([x]))[:, 0]
res["cercle"] = dict(x=x, theta=th.tolist(), mesure=(np.abs(Sx) / rx).tolist(), selberg_delange=(np.abs(sd) / rx).tolist())
i0 = np.argmin(np.abs(th - np.pi))
print(f"x = {x:.3e} : |S(−1, x)|/√x = {abs(Sx[i0]) / rx:.3f} ; |S(i, x)|/√x = {abs(Sx[np.argmin(abs(th - np.pi / 2))]) / rx:.0f} ; S(1, x)/√x = {abs(Sx[0]) / rx:.0f}")
for t in (np.pi / 2, 0.9 * np.pi, 0.99 * np.pi, 0.999 * np.pi):
    k = np.argmin(np.abs(th - t)); print(f"   θ = {t / np.pi:.3f}·π : mesuré {abs(Sx[k]) / rx:10.2f} ; Selberg–Delange {abs(sd[k]) / rx:10.2f}")
# 2. le bouton réel
zs = [-1.02, -1.01, -1.0, -0.99, -0.98]; res["bouton"] = dict(u=U.tolist(), courbes={})
for w in zs:
    Sw = Nk @ (w ** np.arange(K)); sdw = selberg_delange(np.array([w]), X)[0].real if w != -1.0 else np.zeros_like(X)
    res["bouton"]["courbes"][str(w)] = dict(mesure=(Sw / np.sqrt(X)).tolist(), selberg_delange=(sdw / np.sqrt(X)).tolist())
    print(f"z = {w:+.2f} : S(z, x)/√x à 10⁶, 10⁸, 10⁹ = " + ", ".join(f"{Sw[np.argmin(abs(X - v))] / math.sqrt(v):+.2f}" for v in (1e6, 1e8, x)) +
          ("" if w == -1.0 else f" ; Selberg–Delange à 10⁹ : {sdw[-1] / rx:+.2f}"))
# moyenne de L(x)/√x le long de ln x : la formule explicite prédit 1/ζ(½) = −0,6848 (le « biais de Pólya »)
m = U >= 9; res["biais_L"] = float(np.mean(L[m] / np.sqrt(X[m])))
print(f"moyenne de L(x)/√x (en ln x, de 8 000 à 10⁹) : {res['biais_L']:.3f} ; formule explicite : 1/ζ(½) = −0,685")
# 3. le hasard contre μ
M = d["M"].astype(float); F = d["F"].astype(float)
res["hasard"] = dict(u=U.tolist(), M=(M / np.sqrt(X)).tolist(), F=(F / np.sqrt(X)[None, :]).tolist())
mm = U >= math.log(1e6)
print(f"max |M(x)|/√x de 10⁶ à 10⁹ : {np.max(np.abs(M[mm]) / np.sqrt(X[mm])):.2f} ; tirages au hasard : " + ", ".join(f"{np.max(np.abs(F[s][mm]) / np.sqrt(X[mm])):.2f}" for s in range(len(F))))
w = np.hanning(m.sum()); u = U[m]; gam = np.arange(1, 60, 0.02)
def spectre(y):
    yy = (y[m] - y[m].mean()) * w; return np.abs(np.exp(-1j * np.outer(gam, u)) @ yy) * 2 / w.sum()
sM = spectre(M / np.sqrt(X)); sF = [spectre(F[s] / np.sqrt(X)) for s in range(len(F))]
gz = zeros[zeros < 60]; amp = []
for g0 in gz:
    rho = 0.5 + 1j * g0; hh = 1e-5
    dz = (zeta(np.array([rho + hh]))[0] - zeta(np.array([rho - hh]))[0]) / (2 * hh)
    amp.append(2 / abs(rho * dz))
res["spectre"] = dict(gamma=gam.tolist(), M=sM.tolist(), F=[s.tolist() for s in sF], zeros=gz.tolist(), volume_predit=amp)
for g0, a in list(zip(gz, amp))[:6]:
    k = np.argmin(np.abs(gam - g0)); print(f"   note γ = {g0:.2f} : volume dans M {sM[k - 5:k + 6].max():.3f} (prédit 2/|ρζ'(ρ)| = {a:.3f}) ; hasard (moyenne) {np.mean([s[k] for s in sF]):.3f}")
ki = np.argmin(np.abs(th - np.pi / 2)); c99 = np.array(res["bouton"]["courbes"]["-0.99"]["mesure"])
res["resume"] = dict(cercle_i=[float(abs(Sx[ki]) / rx), float(abs(sd[ki]) / rx)], L_final=float(L[j] / rx), z099=float(c99[j]),
                     biais=res["biais_L"], max_M=float(np.max(np.abs(M[mm]) / np.sqrt(X[mm]))),
                     max_F=[float(np.max(np.abs(F[s][mm]) / np.sqrt(X[mm]))) for s in range(len(F))], volumes=[float(a) for a in amp])
json.dump(res, open("bouton_de_feynman.json", "w"))
json.dump(res["resume"], open("bouton_de_feynman_resume.json", "w"), indent=1)
