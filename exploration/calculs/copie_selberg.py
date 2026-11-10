# Recopier Selberg à la manière de Connes, Consani et Moscovici (figure copie_selberg.png).
# Leur plan : (1) énergie de Weil sur les ondes vivant entre 1/√x et √x (seuls les premiers ≤ x interviennent) ;
# (2) l'onde d'énergie la plus petite, supposée PAIRE et SEULE à son niveau ; (3) sa transformée de Fourier n'a que des
# zéros réels ; (4) quand x grandit, elle tend vers Ξ ; (5) Hurwitz : la limite n'a que des zéros réels (hypothèse de Riemann).
# Ce programme vérifie numériquement (2), (3) et (4) dans notre famille d'ondes :
#   - énergies des ondes paires (cos((m − ½)πt/a)) et impaires (sin(mπt/a)) : la plus basse est-elle paire et simple ?
#   - nombre de changements de signe des premières ondes propres (comme une corde vibrante : 0, 1, 2, 3) ;
#   - zéros de la transformée de Fourier de l'onde la plus fragile : tous réels ? (théorème de Sturm, comptage exact) ;
#   - distance de l'onde la plus fragile à la fonction Φ de Riemann, dont Ξ est la transformée de Fourier.
# Usage : python3 copie_selberg.py 8 20 160     (x, nombre d'ondes de chaque parité, chiffres ; une minute environ)
import sys
from decimal import Decimal as D
import numpy as np
import weil_hp as W

# ---------------------------------------------------------------- secteur impair : φ(t) = Σ v_m sin(mπt/a)
def G_impair(u, a, K):
    """G_jk(u) = ∫ sin(K_j t) sin(K_k (t+u)) dt sur [−a, a − u] : même forme fermée que pour les cosinus."""
    N = len(K); s = []; c = []
    for k in K:
        sk, ck = W.sincos(k * u); s.append(sk); c.append(ck)
    G = [[D(0)] * N for _ in range(N)]
    for i in range(N):
        G[i][i] = ((2 * a - u) * c[i] + s[i] / K[i]) / 2
        for j in range(i + 1, N):
            v = ((s[j] - s[i]) / (K[i] - K[j]) + (s[i] + s[j]) / (K[i] + K[j])) / 2
            if (i + j) % 2: v = -v
            G[i][j] = v; G[j][i] = v
    return G

def matrice_impaire(X, N, noeuds=40):
    """Même formule explicite que weil_hp.weil_matrix ; pour une onde impaire, le terme des pôles vaut −2 (∫ φ sh(t/2))²."""
    a = D(X).ln() / 2; P = W.pi()
    K = [D(m) * P / a for m in range(1, N + 1)]
    e = (a / 2).exp(); sh = (e - 1 / e) / 2
    B = [(1 if m % 2 else -1) * 2 * K[m - 1] * sh / (K[m - 1] ** 2 + D("0.25")) for m in range(1, N + 1)]
    M = [[-2 * B[i] * B[j] for j in range(N)] for i in range(N)]
    const = a * (P.ln() + W.euler_gamma() + (1 - (-4 * a).exp()).ln())
    L = 2 * a; panneaux = max(8, int(float(K[-1]) * float(L) / 5) + 1); h = L / panneaux
    for ip in range(panneaux):
        mid = h * ip + h / 2
        for xg, wg in W.gauss_legendre(noeuds):
            u = mid + h / 2 * xg; w = h / 2 * wg
            e2 = (-2 * u).exp(); eh = (-u / 2).exp(); f1 = w / (1 - e2)
            G = G_impair(u, a, K)
            for i in range(N):
                M[i][i] += f1 * (2 * a * e2 - eh * 2 * G[i][i])
                for j in range(i + 1, N):
                    v = -f1 * eh * 2 * G[i][j]; M[i][j] += v; M[j][i] += v
    for n, p in W.prime_powers_below(D(X)):
        u = D(n).ln()
        if u >= 2 * a: continue
        G = G_impair(u, a, K); coef = 2 * D(p).ln() / D(n).sqrt()
        for i in range(N):
            for j in range(N): M[i][j] -= coef * G[i][j]
    for i in range(N): M[i][i] -= const
    return M

# ---------------------------------------------------------------- ondes propres en haute précision
def ondes_propres(M, k=2):
    Mf = np.array([[float(v) for v in r] for r in M]); V = np.linalg.eigh(Mf)[1]
    out = []
    for j in range(k):
        v = [D(repr(float(x))) for x in V[:, j]]
        for _ in range(16):
            for _, u in out:
                c = sum(a * b for a, b in zip(v, u)); v = [a - c * b for a, b in zip(v, u)]
            v = W.solve(M, v)
            for _, u in out:
                c = sum(a * b for a, b in zip(v, u)); v = [a - c * b for a, b in zip(v, u)]
            nrm = sum(x * x for x in v).sqrt(); v = [x / nrm for x in v]
        out.append((W.rayleigh(M, v), v))
    return out

def changements_de_signe(v, K, a, impaire, npts=600):
    prec, n = 0, 0
    for i in range(1, npts):
        t = -a + 2 * a * D(i) / npts
        f = sum(v[m] * (W.sincos(K[m] * t)[0] if impaire else W.sincos(K[m] * t)[1]) for m in range(len(v)))
        s = 1 if f > 0 else (-1 if f < 0 else 0)
        if s and prec and s != prec: n += 1
        if s: prec = s
    return n

# ---------------------------------------------------------------- zéros de la transformée de Fourier : tous réels ?
def _mul(p, q):
    r = [D(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q): r[i + j] += x * y
    return r
def _rem(a, b):
    a = a[:]
    while len(a) >= len(b):
        f = a[-1] / b[-1]; s = len(a) - len(b)
        for i in range(len(b)): a[s + i] -= f * b[i]
        a = a[:-1]
    return a
def zeros_reels(v, K):
    """φ̂(z) = cos(za) · Σ c_m/(K_m² − z²) ; le numérateur P(w), w = z², est de degré N − 1. Suite de Sturm : racines réelles > 0."""
    N = len(v); k2 = [k * k for k in K]; c = [v[m] * (1 if m % 2 == 0 else -1) * 2 * K[m] for m in range(N)]
    P = [D(0)] * N
    for m in range(N):
        t = [c[m]]
        for j in range(N):
            if j != m: t = _mul(t, [k2[j], D(-1)])
        P = [x + y for x, y in zip(P, t)]
    sc = max(abs(x) for x in P); P = [x / sc for x in P]
    eps = D(10) ** (-(W._prec() - 40))
    suite = [P, [i * P[i] for i in range(1, len(P))]]
    while len(suite[-1]) > 1:
        r = [-x for x in _rem(suite[-2], suite[-1])]
        while len(r) > 1 and abs(r[-1]) <= eps: r = r[:-1]
        if len(r) == 1 and abs(r[0]) <= eps: break
        suite.append(r)
    def V(signes):
        s = [x for x in signes if x != 0]; return sum(1 for i in range(len(s) - 1) if s[i] != s[i + 1])
    a0 = [(1 if p[0] > 0 else (-1 if p[0] < 0 else 0)) for p in suite]; ainf = [(1 if p[-1] > 0 else -1) for p in suite]
    return V(a0) - V(ainf), len(P) - 1

# ---------------------------------------------------------------- Φ de Riemann (Ξ en est la transformée de Fourier)
def Phi(u, nmax=8):
    u = np.abs(np.asarray(u, float))
    return 2 * sum((2 * np.pi ** 2 * n ** 4 * np.exp(4.5 * u) - 3 * np.pi * n ** 2 * np.exp(2.5 * u)) * np.exp(-np.pi * n ** 2 * np.exp(2 * u)) for n in range(1, nmax + 1))

if __name__ == "__main__":
    X = sys.argv[1] if len(sys.argv) > 1 else "8"; N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    W.set_precision(int(sys.argv[3]) if len(sys.argv) > 3 else 160)
    a = D(X).ln() / 2; P = W.pi()
    Kp = [(D(m) - D("0.5")) * P / a for m in range(1, N + 1)]; Ki = [D(m) * P / a for m in range(1, N + 1)]
    paires = ondes_propres(W.weil_matrix(D(X), N), 2); impaires = ondes_propres(matrice_impaire(D(X), N), 2)
    modes = sorted([(float(l), "paire", changements_de_signe(v, Kp, a, False)) for l, v in paires] +
                   [(float(l), "impaire", changements_de_signe(v, Ki, a, True)) for l, v in impaires])
    print(f"x = {X}, {N} ondes de chaque parité : énergies par ordre croissant")
    for l, p, s in modes: print(f"   {l:.3e}  onde {p}, {s} changement(s) de signe")
    nr, deg = zeros_reels(paires[0][1], Kp)
    print(f"zéros libres de la transformée de Fourier de l'onde la plus fragile : {nr} réels sur {deg}")
    af = float(a); t = np.linspace(-af, af, 2001); vf = np.array([float(x) for x in paires[0][1]])
    f = np.cos(np.outer(t, [float(k) for k in Kp])) @ vf; f = f if f[1000] > 0 else -f
    f /= np.sqrt(np.trapezoid(f ** 2, t)); ph = Phi(t); ph /= np.sqrt(np.trapezoid(ph ** 2, t))
    print(f"distance à Φ de Riemann (normalisées) : {100 * np.sqrt(np.trapezoid((f - ph) ** 2, t)):.2f} %")
