# La fonction zêta du papillon et ses « zéros » (développement en cycles de Cvitanović, à partir des orbites périodiques
# calculées par papillon_premiers.py).
#
# Comme Euler pour les nombres premiers, on fait un produit sur les « premiers » du papillon, ses orbites périodiques p,
# de période T_p et de multiplicateur instable Λ_p (une erreur sur l'orbite est multipliée par Λ_p en un tour) :
#
#     1/ζ(s) = Π_p (1 − e^{−s T_p} / |Λ_p|)                       (fonction zêta dynamique de Ruelle)
#     D(s)   = exp(− Σ_p Σ_r e^{−s r T_p} / (r |det(1 − M_p^r)|))  (déterminant spectral, plus précis)
#
# On développe en regroupant les termes par nombre total de boucles (≤ N), puis on fait N = 13. Les orbites longues
# « s'ombrent » sur les courtes, si bien que les termes se compensent et que la série converge vite.
#   • s = 0 doit être un zéro exact (rien ne s'échappe de l'attracteur) : c'est le test de la méthode ;
#   • la pente donne l'exposant de Lyapunov λ = ⟨ln|Λ|⟩/⟨T⟩ (à comparer à la mesure directe, 0,906) ;
#   • avec des poids 1 au lieu de 1/|Λ_p|, le zéro réel est l'entropie topologique h (le « théorème des nombres
#     premiers » du papillon : environ e^{ht}/(ht) orbites de période ≤ t) ;
#   • les autres zéros de D(s), complexes, sont les résonances de Ruelle–Pollicott : ils règlent la vitesse à laquelle
#     le papillon « oublie » son passé. Ce sont les analogues des zéros de Riemann. Sont-ils alignés ?
# Usage : python3 zeta_papillon.py papillon_premiers.json   (écrit zeta_papillon.json et la table orbites_papillon.txt)
import sys, json, math
import numpy as np

D = json.load(open(sys.argv[1])); orb = D["orbites"]
NMAX = max(o["n"] for o in orb)

def pseudo_orbites(N):
    """les produits d'orbites distinctes de longueur totale ≤ N : (T total, Σ ln|Λ|, signe)"""
    k_ = [[] for _ in range(N + 1)]; k_[0] = [(0.0, 0.0, 1)]
    for o in orb:
        n = o["n"]
        if n > N: continue
        T, A = o["T"], math.log(abs(o["Lambda"]))
        for k in range(N, n - 1, -1):
            if k_[k - n]: k_[k] = k_[k] + [(t + T, a + A, -s) for (t, a, s) in k_[k - n]]
    out = []
    for k in range(1, N + 1):
        if k_[k]: out.append(np.array(k_[k]))
    return np.concatenate(out) if out else np.zeros((0, 3))

def zeta_dyn(P, s, beta=0.0):
    """1/ζ(s) tronquée, et sa dérivée ; poids |Λ|^(β−1)"""
    T, A, S = P[:, 0], P[:, 1], P[:, 2]
    w = S * np.exp(-s * T + (beta - 1.0) * A)
    return 1.0 + np.sum(w), -np.sum(T * w)

def zeta_top(P, s):
    T, S = P[:, 0], P[:, 2]; w = S * np.exp(-s * T)
    return 1.0 + np.sum(w), -np.sum(T * w)

def zero_reel(f, s):
    for _ in range(60):
        v, d = f(s); s2 = s - v / d
        if abs(s2 - s) < 1e-14: return s2
        s = s2
    return s

# ------------------------------------------------------------------ le déterminant spectral, par les identités de Newton
REP = []                                                     # (n_p, r, T_p, |det(1 − M_p^r)|)
def prepare_rep(N):
    global REP
    REP = []
    for o in orb:
        n = o["n"]; L = o["Lambda"]; Ls = o.get("stable", 0.0)
        for r in range(1, N // n + 1):
            REP.append((n * r, r, o["T"] * r, abs((1 - L ** r) * (1 - Ls ** r))))
    REP = np.array(REP)

def det_spectral(s, N):
    m, r, T, dt = REP[:, 0], REP[:, 1], REP[:, 2], REP[:, 3]
    sel = m <= N
    c = np.exp(-s * T[sel]) / (r[sel] * dt[sel]); mm = m[sel].astype(int)
    C = np.zeros(N + 1, complex); np.add.at(C, mm, c)
    Q = np.zeros(N + 1, complex); Q[0] = 1.0
    for k in range(1, N + 1):
        Q[k] = -sum(j * C[j] * Q[k - j] for j in range(1, k + 1)) / k
    return Q.sum()

def zeros_complexes(f, re=(-3.0, 0.4), im=(0.5, 30.0), pas=0.05):
    """les zéros d'une fonction holomorphe dans un rectangle : minima de |f| sur une grille, puis Newton (dérivée numérique)"""
    xs = np.arange(re[0], re[1], pas); ys = np.arange(im[0], im[1], pas)
    G = np.array([[abs(f(complex(x, y))) for x in xs] for y in ys])
    cand = []
    for i in range(1, len(ys) - 1):
        for j in range(1, len(xs) - 1):
            v = G[i, j]
            if v <= G[i - 1:i + 2, j - 1:j + 2].min() and v < 0.3: cand.append(complex(xs[j], ys[i]))
    zs = []
    for z in cand:
        for _ in range(40):
            h = 1e-6; v = f(z); d = (f(z + h) - f(z - h)) / (2 * h)
            if d == 0: break
            z2 = z - v / d
            if abs(z2 - z) < 1e-11: z = z2; break
            z = z2
        if re[0] - 0.2 < z.real < re[1] + 0.2 and im[0] - 0.2 < z.imag < im[1] + 0.2 and abs(f(z)) < 1e-8:
            if all(abs(z - w) > 1e-6 for w in zs): zs.append(z)
    return sorted(zs, key=lambda z: z.imag)

if __name__ == "__main__":
    print(f"{len(orb)} orbites, jusqu'à {NMAX} boucles")
    res = dict(table=[], zeros={})
    prepare_rep(NMAX)
    for N in range(4, NMAX + 1):
        P = pseudo_orbites(N)
        s0 = zero_reel(lambda s: zeta_dyn(P, s), 0.0)
        T, A, S = P[:, 0], P[:, 1], P[:, 2]; w = S * np.exp(-s0 * T - A)
        lam = np.sum(A * w) / np.sum(T * w)
        h = zero_reel(lambda s: zeta_top(P, s), 0.9)
        d0 = zero_reel(lambda s: (det_spectral(s, N).real, ((det_spectral(s + 1e-7, N) - det_spectral(s - 1e-7, N)) / 2e-7).real), 0.0)
        res["table"].append(dict(N=N, termes=len(P), s0=s0, s0_det=d0, lyapunov=lam, entropie=h))
        print(f"N = {N:2d} : {len(P):6d} pseudo-orbites ; zéro réel de 1/ζ : {s0:+.2e} ; du déterminant : {d0:+.2e} ; "
              f"λ = {lam:.5f} ; h = {h:.5f}", flush=True)
    # extrapolation : les écarts successifs décroissent à peu près géométriquement (méthode d'Aitken)
    def aitken(v):
        a, b, c = v[-3:]; d = (c - b) - (b - a)
        return c - (c - b) ** 2 / d if d != 0 else c
    for cle in ("s0_det", "lyapunov", "entropie"):
        v = [r[cle] for r in res["table"]]; res[cle + "_extrapole"] = aitken(v)
        print(f"{cle} : N = {NMAX} → {v[-1]:.5f} ; extrapolé → {res[cle + '_extrapole']:.5f}")
    # les zéros complexes : on ne garde que ceux qui ne bougent plus quand on ajoute des orbites
    Zs = {}
    for N in (NMAX - 2, NMAX - 1, NMAX):
        Zs[N] = zeros_complexes(lambda s: det_spectral(s, N))
        res["zeros"][N] = [[z.real, z.imag] for z in Zs[N]]
        print(f"N = {N} : zéros complexes du déterminant spectral (Re s, Im s) :", flush=True)
        print("   " + "  ".join(f"({z.real:+.3f}, {z.imag:.3f})" for z in Zs[N][:16]))
    stables = []
    for z in Zs[NMAX]:
        d1 = min((abs(z - w) for w in Zs[NMAX - 1]), default=9); d2 = min((abs(z - w) for w in Zs[NMAX - 2]), default=9)
        if d1 < 0.02 and d2 < 0.05: stables.append([z.real, z.imag, d1])
    res["zeros_stables"] = stables
    print("zéros stables (ne bougent plus de N − 2 à N) :", "  ".join(f"({a:+.4f}, {b:.4f}) ±{c:.0e}" for a, b, c in stables))
    json.dump(res, open("zeta_papillon.json", "w"))
    # la table des orbites, avec la géodésique de la surface modulaire qui porte le même mot (Ghys) :
    # L → (1 1 / 0 1), R → (1 0 / 1 1), trace t, taille N = ((t + √(t² − 4))/2)²
    with open("orbites_papillon.txt", "w") as f:
        f.write("# mot  boucles  période T  multiplicateur Λ  trace (surface modulaire)  taille N = e^longueur\n")
        for o in sorted(orb, key=lambda o: (o["n"], o["T"])):
            a, b, c, d = 1, 0, 0, 1
            for ch in o["mot"]:
                if ch == "L": a, b, c, d = a, a + b, c, c + d
                else: a, b, c, d = a + b, b, c + d, d
            t = a + d; Nm = ((t + math.sqrt(t * t - 4)) / 2) ** 2
            f.write(f"{o['mot']:14s} {o['n']:3d}  {o['T']:.10f}  {o['Lambda']:14.6f}  {t:8d}  {Nm:.6f}\n")
