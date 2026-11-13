# Contrôles numériques des formules de la note demontre.pdf (ils ne remplacent pas les démonstrations).
#   (i)   la formule de Lévy–Khintchine pour Re ψ(¼ + ir/2) ;                (ii) la constante κ ;
#   (iii) la proposition 7 : la marge de Nicolas comme intégrale sur l'avenir (à la queue de l'intégrale près, constante) ;
#   (iv)  le lemme 8 : le seuil θ*(p) et son encadrement ;
#   (v)   la formule explicite (1)-(2) et la décomposition W = P + B, sur une onde paire et une onde impaire :
#         la somme sur les zéros (les 150 premiers suffisent ici) doit redonner P + partie archimédienne + nombres premiers.
# Usage : python3 controles_de_la_note.py ../../zeros150.json        (une à deux minutes)
import sys, json, math, numpy as np
from scipy.special import digamma
from scipy.integrate import quad
from scipy.optimize import brentq
G = 0.5772156649015329
# (i) Lévy–Khintchine : Re ψ(1/4 + ir/2) − ψ(1/4) = ∫ (1 − cos ru) e^{u/2}/sh u du
for r in (0.7, 3.0, 14.134725):
    nu = lambda u: math.exp(u / 2) / math.sinh(u) if u < 300 else 2 * math.exp(-u / 2)
    I1 = quad(lambda u: (1 - math.cos(r * u)) * nu(u), 0, 1, limit=400)[0]
    I2 = quad(lambda u: nu(u), 1, 200, limit=400)[0] - quad(lambda u: nu(u), 1, 200, weight="cos", wvar=r, limit=2000)[0]
    print(f"(i) r = {r}: gauche {digamma(0.25 + 0.5j * r).real - digamma(0.25):.10f}  droite {I1 + I2:.10f}")
# (ii) κ
print("(ii) κ =", math.log(math.pi) - digamma(0.25), " ln(8π) + γ + π/2 =", math.log(8 * math.pi) + G + math.pi / 2)
# crible
N = 20_000_000
cr = np.ones(N + 1, bool); cr[:2] = False
for i in range(2, int(N ** 0.5) + 1):
    if cr[i]: cr[i * i::i] = False
ps = np.nonzero(cr)[0].astype(np.float64); lp = np.log(ps); th = np.cumsum(lp)
# (iii) proposition « avenir » : F_k = ∫_{p_k}^∞ (t − θ(t)) w(t) dt − H_k + ε_k
# entre deux premiers consécutifs q < q', θ = θ(q) : ∫ (t − θ) w = [ln ln t − 1/ln t] + θ [1/(t ln t)]
A = np.cumsum(-np.log1p(-1 / ps))
a_, b_ = ps[:-1], ps[1:]
seg = (np.log(np.log(b_)) - 1 / np.log(b_)) - (np.log(np.log(a_)) - 1 / np.log(a_)) + th[:-1] * (1 / (b_ * np.log(b_)) - 1 / (a_ * np.log(a_)))
cumseg = np.concatenate([[0.0], np.cumsum(seg)])            # ∫_{p_1}^{p_j}
Xf = ps[-1]
# queue au-delà de X : t − θ(t) ≈ √t (premier ordre) → ∫_X^∞ √t w dt ≈ ∫ (1 + ln t)/(t^{3/2} ln² t) dt
queue = quad(lambda t: (1 + math.log(t)) / (t ** 1.5 * math.log(t) ** 2), Xf, np.inf)[0]
h = -np.log1p(-1 / ps) - 1 / ps; Htot = 0.5772156649015329 - 0.2614972128476428   # γ − M
for k in (10, 100, 1000, 10000, 100000):
    p = ps[k - 1]; F = A[k - 1] - G - math.log(math.log(th[k - 1]))
    I = (cumseg[-1] - cumseg[k - 1]) + queue
    H = Htot - h[:k].sum()
    eps = math.log(math.log(p)) - math.log(math.log(th[k - 1])) - (p - th[k - 1]) / (p * math.log(p))
    print(f"(iii) k = {k:6d}, p = {int(p):8d} : F = {F:.9f} ; ∫ − H + ε = {I - H + eps:.9f} ; H = {H:.2e} < 1/2p = {0.5 / p:.2e} ; ε = {eps:.2e}")
# (iv) critère exact : θ*(p) et encadrement
for p in (5.0, 101.0, 10007.0, 1e9 + 7):
    L = math.log(p); f = lambda t: (p - 1) * math.log1p(L / t) - math.log(t)
    ts = brentq(f, 1.0000001, p)
    print(f"(iv) p = {p:.0f} : θ* = p − {p - ts:.4f} ; ½ ln p + ¾ = {L / 2 + 0.75:.4f} ; encadrement vrai : {p - L / 2 - 0.75 < ts < p}")
# équivalence signe(ΔF) ⇔ θ_k < θ*(p_{k+1}) sur les 2000 premiers pas
ok = 0
for k in range(2, 2002):
    p = ps[k]; L = lp[k]; t = th[k - 1]
    dF = -math.log1p(-1 / p) - math.log(math.log(t + L) / math.log(t))
    phi = (p - 1) * math.log1p(L / t) - math.log(t)
    ok += (dF < 0) == (phi > 0)
print("(iv) équivalence vérifiée sur", ok, "pas sur 2000")

# (v) la formule explicite et W = P + B
gam = np.array(json.load(open(sys.argv[1])))
a = math.log(8) / 2
t = np.linspace(-a, a, 40001); dt = t[1] - t[0]
def simpson(y): return dt / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())
for nom, phi in (("paire", (1 - (t / a) ** 2) ** 5), ("impaire", (t / a) * (1 - (t / a) ** 2) ** 5)):
    pair = nom == "paire"
    def chapeau(r):       # |φ̂(r)|
        r = np.atleast_1d(r); out = np.empty(len(r))
        for i in range(0, len(r), 2000):
            rr = r[i:i + 2000, None]; w = np.cos(rr * t[None, :]) if pair else np.sin(rr * t[None, :])
            y = w * phi[None, :]
            out[i:i + 2000] = dt / 3 * (y[:, 0] + y[:, -1] + 4 * y[:, 1:-1:2].sum(1) + 2 * y[:, 2:-1:2].sum(1))
        return out
    zeros = 2 * np.sum(chapeau(gam) ** 2)
    ep, em = simpson(phi * np.exp(t / 2)), simpson(phi * np.exp(-t / 2))
    P = 2 * ep * em
    rg = np.linspace(0, 400, 80001); f2 = chapeau(rg) ** 2
    m = digamma(0.25 + 0.5j * rg).real - math.log(math.pi)
    y = f2 * m; dr = rg[1] - rg[0]
    arch = (1 / math.pi) * dr / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())
    def g(u):
        k = int(round(u / dt)); frac = u / dt - k
        if k >= len(t) - 1: return 0.0
        sh = np.interp(t + u, t, phi, left=0, right=0); return simpson(phi * sh)
    prem = -2 * sum(L / math.sqrt(n) * g(math.log(n)) for n, L in ((2, math.log(2)), (3, math.log(3)), (4, math.log(2)), (5, math.log(5)), (7, math.log(7))))
    # la forme de Lévy : E(φ) − κ‖φ‖²
    nu = lambda u: math.exp(u / 2) / math.sinh(u)
    n2 = simpson(phi ** 2)
    E = quad(lambda u: (n2 - g(u)) * nu(u), 0, 2 * a, limit=400)[0] + n2 * quad(nu, 2 * a, 60)[0]
    kappa = math.log(math.pi) - digamma(0.25)
    print(f"onde {nom} : somme sur les zéros = {zeros:.10f} ; W = P + arch + premiers = {P + arch + prem:.10f}")
    print(f"     P = {P:+.8f} (lemme : {'+2⟨φ,c⟩²' if pair else '−2⟨φ,s⟩²'} = {(2 if pair else -2) * simpson(phi * (np.cosh(t / 2) if pair else np.sinh(t / 2))) ** 2:+.8f}) ; arch (Fourier) = {arch:+.8f} ; arch (Lévy) = {E - kappa * n2:+.8f}")
