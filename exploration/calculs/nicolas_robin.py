# Nicolas et Robin : l'hypothèse de Riemann « premier après premier » et « sur les non-premiers ».
#
# Entrée : la sortie de nicolas_premier_apres_premier.c (points de contrôle jusqu'à 10¹¹) et les zéros de ζ.
#
# 1. Nicolas (1983). F(p) = Σ_{q ≤ p} −ln(1 − 1/q) − γ − ln ln θ(p) ; l'hypothèse ⇔ F(p) > 0 pour tout premier p.
#    On décompose F(p) exactement (Mertens, et la formule explicite de von Mangoldt) :
#        F(p) = [A − S](p) + E(p)/(p ln p) + ln ln p − ln ln θ(p) − I(p),
#    où S(p) = Σ_{q^m ≤ p} 1/(m q^m), E = ψ − x, et I(p) = ∫_p^∞ E(t)(ln t + 1)/(t² ln² t) dt.
#    Tout est connu dès qu'on connaît les premiers ≤ p, sauf I(p), qui ne dépend que des premiers au-delà de p.
#    Les zéros prédisent I : I(p) = −Σ_ρ [E₁((1 − ρ) ln p) + p^(ρ−1)/(ρ ln p)] − ln(2π)/(p ln p).
#    Sous l'hypothèse de Riemann, G(p) = F(p)·√p·ln p tend vers la bande [2 − β, 2 + β], β = Σ_ρ 1/(ρ(1 − ρ)) = 0,0462.
# 2. Robin (1984). Pour les nombres « colossalement abondants » N (les plus riches en diviseurs), on calcule
#    σ(N)/(N ln ln N), à comparer à e^γ : l'hypothèse ⇔ ce rapport reste sous e^γ pour tout n > 5 040, et il suffit de
#    le vérifier pour ces nombres-là (Broughan, 2017). Le plus grand facteur premier de N est le point de contrôle P.
# Usage : python3 nicolas_robin.py nicolas_1e11.txt zeros_precis.npy
import sys, json, math
import numpy as np

GAMMA = 0.57721566490153286061
G_INF = 0.31571845205389007686                               # Σ_p [−ln(1 − 1/p) − 1/p] = γ − M (Meissel–Mertens)
D = [l.split() for l in open(sys.argv[1])]
x = np.array([float(l[0]) for l in D]); P = np.array([int(l[1]) for l in D]); PI = np.array([int(l[2]) for l in D])
TH = np.array([float(l[3]) for l in D]); A = np.array([float(l[4]) for l in D]); B = np.array([float(l[5]) for l in D])
F = np.array([float(l[6]) for l in D]); G = np.array([float(l[7]) for l in D])
Gmin = np.array([float(l[8]) for l in D]); Gmax = np.array([float(l[9]) for l in D])
NUP = int(D[-1][10]); NEX = int(D[-1][11])
gam = np.load(sys.argv[2])
print(f"jusqu'à {x[-1]:.3g} : {PI[-1]:,} nombres premiers ; F a augmenté {NUP} fois ; marches vérifiées exactement : {NEX:,}".replace(",", " "))
print(f"F({P[-1]}) = {F[-1]:.6e} ; G = F·√p·ln p = {G[-1]:.5f}")

# petits nombres premiers (jusqu'à 10⁶ : assez pour √p et pour les nombres colossalement abondants)
M6 = 10**6
cr = np.ones(M6 + 1, bool); cr[:2] = False
for i in range(2, 1001):
    if cr[i]: cr[i * i::i] = False
q = np.nonzero(cr)[0].astype(float); lq = np.log(q)
cum_theta = np.cumsum(lq)
def theta_petit(y):
    k = np.searchsorted(q, y, side="right"); return cum_theta[k - 1] if k > 0 else 0.0

# ------------------------------------------------------------------ 1. Nicolas : la partie connue et la partie « future »
sel = P >= 1000
res_n = dict(p=[], G=[], Gmin=[], Gmax=[], Gpred=[], Iobs=[], Ipred=[])
z = 0.5 + 1j * gam; zc = 1 - z                               # ρ et 1 − ρ (les conjugués s'ajoutent : 2 Re)
for i in np.nonzero(sel)[0]:
    p = float(P[i]); L = math.log(p)
    # A − S = G_∞ − Σ_{q^m ≤ p, m ≥ 2} 1/(m q^m) − Σ_{q > p} g(q), le dernier ≈ 1/(2 p ln p)
    qs = q[q <= math.sqrt(p)]; s2 = 0.0
    m = 2
    while True:
        qq = qs[qs ** m <= p]
        if len(qq) == 0: break
        s2 += float(np.sum(1.0 / (m * qq ** m))); m += 1
    AmS = G_INF - s2 - 1.0 / (2 * p * L)
    psi = TH[i] + sum(theta_petit(p ** (1.0 / k)) for k in range(2, 64) if p ** (1.0 / k) >= 2)
    E = psi - p
    lnln = math.log(L) - math.log(math.log(TH[i]))           # ln ln p − ln ln θ(p)
    I_obs = AmS + E / (p * L) + lnln - F[i]
    w = zc * L
    J = np.exp(-w) / w * (1 - 1 / w + 2 / w ** 2 - 6 / w ** 3 + 24 / w ** 4) + np.exp((z - 1) * L) / (z * L)
    I_pred = -2 * float(np.sum(J.real)) - math.log(2 * math.pi) / (p * L)
    F_pred = AmS + E / (p * L) + lnln - I_pred
    k = math.sqrt(p) * L
    for key, val in (("p", p), ("G", G[i]), ("Gmin", Gmin[i]), ("Gmax", Gmax[i]), ("Gpred", F_pred * k), ("Iobs", I_obs * k), ("Ipred", I_pred * k)):
        res_n[key].append(float(val))
beta = 2 + GAMMA - math.log(4 * math.pi)
Gp = np.array(res_n["G"]); Gq = np.array(res_n["Gpred"]); pp = np.array(res_n["p"])
for a, b in ((1e3, 1e6), (1e6, 1e9), (1e9, 1.01e11)):
    s = (pp >= a) & (pp < b)
    if not s.any(): continue
    print(f"p ∈ [{a:.0e}, {b:.0e}] : G entre {np.min(np.array(res_n['Gmin'])[s]):.4f} et {np.max(np.array(res_n['Gmax'])[s]):.4f} ; "
          f"écart à la prédiction des zéros : max {np.max(np.abs(Gp[s] - Gq[s])):.2e}")
print(f"bande de l'hypothèse de Riemann, quand p → ∞ : [2 − β, 2 + β] = [{2 - beta:.4f}, {2 + beta:.4f}]")
Io = np.array(res_n["Iobs"]); Ip = np.array(res_n["Ipred"])
print(f"la partie « future » −I·√p·ln p à p = {pp[-1]:.3g} : mesurée {-Io[-1]:.5f}, prédite par les zéros {-Ip[-1]:.5f}")

# ------------------------------------------------------------------ 2. Robin : nombres colossalement abondants
def robin_ca(i):
    Pm = float(P[i]); eps = math.log1p(1 / Pm) / math.log(Pm)
    lnN = TH[i]; lsig = B[i]
    for qq, lqq in zip(q, lq):
        if math.log1p(1 / (qq + qq * qq)) / lqq < eps: break   # a_q = 1 pour tous les q suivants (fonction décroissante)
        a = 1
        while True:
            somme = (qq ** (a + 2) - qq) / (qq - 1)              # q + q² + … + q^(a+1)
            if math.log1p(1 / somme) / lqq >= eps: a += 1
            else: break
        lnN += (a - 1) * lqq
        lsig += math.log((1 - qq ** (-a - 1)) / (1 - 1 / qq)) - math.log1p(1 / qq)
    return lnN, lsig
res_r = dict(lnN=[], R=[], P=[])
for i in np.nonzero(P >= 30)[0][::4]:
    lnN, lsig = robin_ca(i)
    res_r["lnN"].append(lnN); res_r["R"].append(math.exp(lsig) / math.log(lnN)); res_r["P"].append(float(P[i]))
eg = math.exp(GAMMA)
Rr = np.array(res_r["R"]); ln_N = np.array(res_r["lnN"])
print(f"Robin : {len(Rr)} nombres colossalement abondants, de plus grand facteur premier 31 à {res_r['P'][-1]:.3g} (N jusqu'à 10^{ln_N[-1] / math.log(10):.4g})")
print(f"   σ(N)/(N ln ln N) maximal : {Rr.max():.6f} (e^γ = {eg:.6f}) ; marge e^γ − rapport au plus grand N : {eg - Rr[-1]:.3e}")
# les exceptions jusqu'à 5 040
sig = np.zeros(5041, dtype=np.int64)
for d in range(1, 5041): sig[d::d] += d
exc = sorted(set(n for n in range(2, 5041) if (math.log(n) <= 1) or sig[n] >= eg * n * math.log(math.log(n))))
print(f"   exceptions jusqu'à 5 040 : {len(exc)} nombres : {exc}")
prem = [n for n in exc if all(n % d for d in range(2, int(n ** 0.5) + 1))]
print(f"   dont les nombres premiers {prem} (ln ln n y est minuscule) ; tous les autres sont composés")
json.dump(dict(nicolas=res_n, beta=beta, nup=NUP, nexact=NEX, pi=int(PI[-1]), pmax=int(P[-1]),
               F_trace=dict(p=P[P >= 3].tolist(), F=F[P >= 3].tolist()),
               robin=dict(lnN=res_r["lnN"], R=res_r["R"], P=res_r["P"], exceptions=exc,
                          exc_R=[float(sig[n] / (n * math.log(math.log(n)))) if math.log(n) > 1 else None for n in exc])),
          open("nicolas_robin.json", "w"))
