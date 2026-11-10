# -*- coding: utf-8 -*-
"""
Positivité de Weil en haute précision — moteur sans dépendance (module standard `decimal`).

On travaille avec des ondes paires φ(t) = Σ c_m cos(K_m t) sur [−a, a], K_m = (m − ½)π/a, nulles aux bords
(t = ln x ; l'onde vit entre x = 1/λ et x = λ, avec λ² = X, a = ½ ln X).
L'énergie de Weil, calculée SANS aucun zéro de ζ, s'écrit (formule explicite de Guinand–Weil, côté « temps ») :

  W(φ) = 2 φ̂(i/2)²                                    (pôles de ζ en 0 et 1)
       − g(0) [ln π + γ_E + ln(1 − e^{−4a})]
       + 2 ∫_0^{2a} [g(0) e^{−2u} − e^{−u/2} g(u)] / (1 − e^{−2u}) du      (place archimédienne)
       − 2 Σ_{n < X} Λ(n) n^{−1/2} g(ln n)                                     (nombres premiers)

avec g(u) = ∫ φ(t) φ(t + u) dt. Si l'hypothèse de Riemann est vraie, W(φ) = Σ_γ φ̂(γ)² ≥ 0 (somme sur les zéros).
Critère de Weil : l'hypothèse est vraie si et seulement si W(φ) ≥ 0 pour toutes les ondes φ (de support aussi grand qu'on veut).

Tout est en formules fermées, sauf deux familles d'intégrales sur [0, 2a], calculées par Gauss–Legendre composite.
"""
from decimal import Decimal as D, getcontext, localcontext
import math

_cache = {}

def set_precision(digits):
    getcontext().prec = int(digits)

def _prec():
    return getcontext().prec

# ---------------------------------------------------------------- constantes et fonctions élémentaires
def pi():
    p = _prec(); key = ("pi", p)
    if key not in _cache:
        with localcontext() as ctx:
            ctx.prec = p + 10
            eps = D(10) ** (-(p + 8))
            def arctan_inv(x):                      # arctan(1/x) pour x entier ≥ 2
                x = D(x); x2 = x * x; term = 1 / x; s = term; k = 1; sign = -1
                while True:
                    term = term / x2
                    t = term / (2 * k + 1)
                    if t < eps: break
                    s += sign * t; sign = -sign; k += 1
                return s
            val = 4 * (4 * arctan_inv(5) - arctan_inv(239))        # formule de Machin
        _cache[key] = +val
    return _cache[key]

def sincos(x):
    """(sin x, cos x) en précision courante."""
    p = _prec()
    with localcontext() as ctx:
        ctx.prec = p + 12
        P = pi(); twopi = 2 * P
        x = D(x)
        x = x - twopi * (x / twopi).to_integral_value()           # ramené dans [−π, π]
        x2 = x * x; eps = D(10) ** (-(p + 10))
        c = D(1); term = D(1); k = 0
        while True:
            k += 2; term = -term * x2 / (k * (k - 1)); c += term
            if abs(term) < eps: break
        s = x; term = x; k = 1
        while True:
            k += 2; term = -term * x2 / (k * (k - 1)); s += term
            if abs(term) < eps: break
    return +s, +c

def euler_gamma():
    """Constante d'Euler γ_E par l'algorithme de Brent–McMillan (erreur ~ e^{−4n})."""
    p = _prec(); key = ("gamma", p)
    if key not in _cache:
        with localcontext() as ctx:
            ctx.prec = p + 15
            n = int(p * math.log(10) / 4) + 6
            term = D(1); H = D(0); A = D(0); B = D(0); k = 0
            eps = D(10) ** (-(p + 12))
            while True:
                if k > 0:
                    term = term * n * n / (k * k); H += D(1) / k
                A += term * H; B += term; k += 1
                if k > 3 * n and term < eps * B: break
            val = A / B - D(n).ln()
        _cache[key] = +val
    return _cache[key]

def gauss_legendre(n):
    """Nœuds et poids de Gauss–Legendre sur [−1, 1] (Newton sur P_n, en précision courante)."""
    p = _prec(); key = ("gl", n, p)
    if key in _cache: return _cache[key]
    out = []
    with localcontext() as ctx:
        ctx.prec = p + 10
        eps = D(10) ** (-(p + 6))
        def legendre(x):
            p0, p1 = D(1), x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            return p1, n * (x * p1 - p0) / (x * x - 1)
        for i in range(1, n // 2 + 1):
            x = D(repr(math.cos(math.pi * (i - 0.25) / (n + 0.5))))
            for _ in range(200):
                pn, dpn = legendre(x); dx = pn / dpn; x -= dx
                if abs(dx) < eps: break
            pn, dpn = legendre(x)
            w = 2 / ((1 - x * x) * dpn * dpn)
            out += [(x, w), (-x, w)]
        if n % 2 == 1:
            pn, dpn = legendre(D(0)); out.append((D(0), 2 / (dpn * dpn)))
    out = [(+x, +w) for x, w in out]
    _cache[key] = out
    return out

def prime_powers_below(X):
    """[(n, p)] pour les puissances de premiers n = p^k avec 2 ≤ n < X."""
    out = []
    for n in range(2, int(math.ceil(X))):
        m = n; p = 2
        while m % p: p += 1
        while m % p == 0: m //= p
        if m == 1: out.append((n, p))
    return out

# ---------------------------------------------------------------- la forme de Weil
def basis(X, N):
    a = D(X).ln() / 2
    P = pi()
    K = [(D(m) - D("0.5")) * P / a for m in range(1, N + 1)]
    return a, K

def G_matrix(u, a, K):
    """G_jk(u) = ∫ e_j(t) e_k(t+u) dt en formule fermée (matrice symétrique)."""
    N = len(K); s = []; c = []
    for k in K:
        sk, ck = sincos(k * u); s.append(sk); c.append(ck)
    G = [[D(0)] * N for _ in range(N)]
    for i in range(N):
        G[i][i] = ((2 * a - u) * c[i] + s[i] / K[i]) / 2
        for j in range(i + 1, N):
            v = ((s[j] - s[i]) / (K[i] - K[j]) + (s[i] + s[j]) / (K[i] + K[j])) / 2
            if (i + j) % 2: v = -v
            G[i][j] = v; G[j][i] = v
    return G

def weil_matrix(X, N, panels=None, nodes_per_panel=40, parts=False):
    """Matrice M de la forme de Weil sur la base {cos(K_m t)}, m = 1..N, pour des ondes vivant entre 1/√X et √X."""
    a, K = basis(X, N)
    P = pi()
    sgn = [1 if m % 2 else -1 for m in range(1, N + 1)]
    e = (a / 2).exp(); cosh_half = (e + 1 / e) / 2
    A = [sgn[i] * 2 * K[i] * cosh_half / (K[i] * K[i] + D("0.25")) for i in range(N)]
    M_pole = [[2 * A[i] * A[j] for j in range(N)] for i in range(N)]
    const = a * (P.ln() + euler_gamma() + (1 - (-4 * a).exp()).ln())
    # intégrales archimédiennes : S_m = ∫ e^{−u/2} sin(K_m u)/(1 − e^{−2u}) du ; Dg_m = ∫ [a e^{−2u} − e^{−u/2} G_mm(u)]/(1 − e^{−2u}) du
    L = 2 * a
    if panels is None:
        panels = max(8, int(float(K[-1]) * float(L) / 5) + 1)        # ~5 radians d'oscillation par panneau au plus
    base = gauss_legendre(nodes_per_panel)
    h = L / panels
    S = [D(0)] * N; Dg = [D(0)] * N
    for ip in range(panels):
        mid = h * ip + h / 2
        for xg, wg in base:
            u = mid + h / 2 * xg; w = h / 2 * wg
            e2 = (-2 * u).exp(); eh = (-u / 2).exp(); den = 1 - e2
            s1, c1 = sincos(K[0] * u)
            s2 = 2 * s1 * c1; c2 = 1 - 2 * s1 * s1                # angle 2θ, avec K_m u = (2m − 1)θ
            sm, cm = s1, c1
            f1 = w * eh / den; f2 = w / den
            for m in range(N):
                S[m] += f1 * sm
                Dg[m] += f2 * (a * e2 - eh * ((2 * a - u) * cm + sm / K[m]) / 2)
                sm, cm = sm * c2 + cm * s2, cm * c2 - sm * s2
    M_arch = [[D(0)] * N for _ in range(N)]
    for i in range(N):
        M_arch[i][i] = 2 * Dg[i]
        for j in range(i + 1, N):
            v = -((S[j] - S[i]) / (K[i] - K[j]) + (S[i] + S[j]) / (K[i] + K[j])) / 2
            if (i + j) % 2: v = -v
            M_arch[i][j] = M_arch[j][i] = 2 * v
    M_prime = [[D(0)] * N for _ in range(N)]
    for n, p in prime_powers_below(X):
        u = D(n).ln()
        if u >= 2 * a: continue
        G = G_matrix(u, a, K); coef = 2 * D(p).ln() / D(n).sqrt()
        for i in range(N):
            for j in range(N):
                M_prime[i][j] -= coef * G[i][j]
    M = [[M_pole[i][j] + M_arch[i][j] + M_prime[i][j] for j in range(N)] for i in range(N)]
    for i in range(N): M[i][i] -= const
    if parts:
        return M, dict(pole=M_pole, arch=M_arch, prime=M_prime, const=const, a=a, K=K)
    return M

# ---------------------------------------------------------------- algèbre linéaire en haute précision
def cholesky_pivots(M):
    """Pivots de la factorisation LDLᵀ ; tous > 0  ⇔  M définie positive (à la précision du calcul)."""
    N = len(M); A = [row[:] for row in M]; piv = []
    for k in range(N):
        d = A[k][k]; piv.append(d)
        if d <= 0: return piv
        for i in range(k + 1, N):
            l = A[i][k] / d
            if l != 0:
                Ai = A[i]; Ak = A[k]
                for j in range(k + 1, N): Ai[j] -= l * Ak[j]
    return piv

def solve(M, b):
    N = len(M); A = [M[i][:] + [b[i]] for i in range(N)]
    for k in range(N):
        p = max(range(k, N), key=lambda i: abs(A[i][k]))
        A[k], A[p] = A[p], A[k]
        for i in range(k + 1, N):
            l = A[i][k] / A[k][k]
            if l != 0:
                Ai = A[i]; Ak = A[k]
                for j in range(k, N + 1): Ai[j] -= l * Ak[j]
    x = [D(0)] * N
    for i in range(N - 1, -1, -1):
        x[i] = (A[i][N] - sum(A[i][j] * x[j] for j in range(i + 1, N))) / A[i][i]
    return x

def _normalize(v):
    n = sum(x * x for x in v).sqrt(); return [x / n for x in v]

def rayleigh(M, v):
    return sum(v[i] * sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(v)))

def smallest_eigenpair(M, v0, iterations=8):
    """Itération inverse : converge vers la plus petite valeur propre et son vecteur."""
    v = _normalize([D(repr(float(x))) for x in v0])
    for _ in range(iterations):
        v = _normalize(solve(M, v))
    lam = rayleigh(M, v)
    r = [sum(M[i][j] * v[j] for j in range(len(v))) - lam * v[i] for i in range(len(v))]
    res = sum(x * x for x in r).sqrt()
    return lam, v, res

# ---------------------------------------------------------------- la meilleure onde et ses zéros
def phi_hat(v, a, K, r):
    """φ̂(r) = cos(ra) Σ v_m (−1)^{m+1} 2 K_m / (K_m² − r²)."""
    r = D(r); s = D(0)
    for m, (vm, km) in enumerate(zip(v, K)):
        t = 2 * km * vm / (km * km - r * r)
        s += t if m % 2 == 0 else -t
    return sincos(r * a)[1] * s

def refine_zero(f, r0, tol_digits=None):
    """Sécante à partir d'une estimation r0 (float)."""
    p = _prec(); tol = D(10) ** (-(tol_digits or p - 8))
    x0 = D(repr(r0)); x1 = x0 + D("1e-7")
    f0, f1 = f(x0), f(x1)
    for _ in range(200):
        if f1 == f0: break
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        x0, f0, x1 = x1, f1, x2; f1 = f(x1)
        if abs(x1 - x0) < tol: break
    return x1

# ---------------------------------------------------------------- zéros de référence : ζ en haute précision (Euler–Maclaurin)
def _bernoulli_even(M):
    from fractions import Fraction
    B = [Fraction(1)]
    for m in range(1, 2 * M + 1):
        B.append(-sum(math.comb(m + 1, j) * B[j] for j in range(m)) / (m + 1))
    return [B[2 * k] for k in range(1, M + 1)]

def zeta(s_re, s_im, terms=150, M=40):
    """ζ(s) pour s = s_re + i s_im (Decimal), par Euler–Maclaurin. Renvoie (Re, Im)."""
    key = ("bern", M)
    if key not in _cache: _cache[key] = _bernoulli_even(M)
    Bs = _cache[key]
    sr, si = D(s_re), D(s_im)
    tot_r = D(0); tot_i = D(0)
    for n in range(1, terms):
        ln = D(n).ln(); mag = (-sr * ln).exp(); sn, cn = sincos(si * ln)
        tot_r += mag * cn; tot_i -= mag * sn                       # n^{−s} = n^{−σ} (cos(t ln n) − i sin(t ln n))
    Nn = D(terms); lnN = Nn.ln(); mag = (-sr * lnN).exp(); sN, cN = sincos(si * lnN)
    Ns_r, Ns_i = mag * cN, -mag * sN                               # N^{−s}
    # N^{1−s}/(s − 1)
    num_r, num_i = Nn * Ns_r, Nn * Ns_i; dr, di = sr - 1, si; den = dr * dr + di * di
    tot_r += (num_r * dr + num_i * di) / den; tot_i += (num_i * dr - num_r * di) / den
    tot_r += Ns_r / 2; tot_i += Ns_i / 2
    # Σ B_{2k}/(2k)! s(s+1)…(s+2k−2) N^{−s−2k+1}
    pr, pi_ = sr, si                      # produit s(s+1)…(s+2k−2), commence à s
    powr, powi = Ns_r / Nn, Ns_i / Nn     # N^{−s−1}
    fact = D(1)
    for k in range(1, M + 1):
        fact = fact * (2 * k) * (2 * k - 1) if k > 1 else D(2)
        b = D(Bs[k - 1].numerator) / D(Bs[k - 1].denominator)
        cr, ci = b / fact * (pr * powr - pi_ * powi), b / fact * (pr * powi + pi_ * powr)
        tot_r += cr; tot_i += ci
        # prochain : produit × (s + 2k − 1)(s + 2k), puissance × N^{−2}
        for add in (2 * k - 1, 2 * k):
            ar, ai = sr + add, si
            pr, pi_ = pr * ar - pi_ * ai, pr * ai + pi_ * ar
        powr, powi = powr / (Nn * Nn), powi / (Nn * Nn)
    return tot_r, tot_i

def zeta_zero(gamma_estimate, terms=150, M=40):
    """Zéro de ζ près de ½ + i·γ (sécante complexe en 2D, sans supposer qu'il est sur la droite)."""
    p = _prec(); tol = D(10) ** (-(p - 10))
    s0 = (D("0.5"), D(repr(gamma_estimate))); s1 = (D("0.5"), s0[1] + D("1e-6"))
    f0 = zeta(*s0, terms=terms, M=M); f1 = zeta(*s1, terms=terms, M=M)
    for _ in range(100):
        # s2 = s1 − f1 (s1 − s0)/(f1 − f0)   (complexes)
        dr, di = s1[0] - s0[0], s1[1] - s0[1]; gr, gi = f1[0] - f0[0], f1[1] - f0[1]
        den = gr * gr + gi * gi
        if den == 0: break
        qr, qi = (dr * gr + di * gi) / den, (di * gr - dr * gi) / den   # (s1 − s0)/(f1 − f0)
        stepr, stepi = f1[0] * qr - f1[1] * qi, f1[0] * qi + f1[1] * qr
        s2 = (s1[0] - stepr, s1[1] - stepi)
        s0, f0, s1 = s1, f1, s2; f1 = zeta(*s1, terms=terms, M=M)
        if abs(stepr) + abs(stepi) < tol: break
    return s1                                                       # (partie réelle, γ)
