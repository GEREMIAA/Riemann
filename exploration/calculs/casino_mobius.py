# Le casino de Möbius (figure casino_mobius.png) : des parieurs misent sur la suite μ(n) = +1, −1 ou 0.
#   - le parieur constant gagne M(x) = Σ μ(n) ; l'hypothèse de Riemann : |M(x)| ≤ x^(½ + ε) ;
#   - les parieurs périodiques honnêtes suivent un caractère de Dirichlet χ fixé d'avance : Σ μ(n) χ(n) (hypothèse généralisée) ;
#   - le meilleur parieur périodique choisi après coup : Σ_a |Σ_{n ≡ a mod q} μ(n)| ;
#   - le parieur à phase linéaire : max_α |Σ μ(n) e(αn)|, par transformée de Fourier rapide ;
#   - le tricheur qui lit μ : Σ |μ(n)| ≈ 0,61·x.
# Usage : python3 casino_mobius.py 1e9     (crible jusqu'à 10⁹ en quelques minutes ; 10¹⁰ prend une demi-heure)
#         python3 casino_mobius.py phase 24 (parieur à phase linéaire jusqu'à 2^24)
import sys, math, time
import numpy as np

QS = [3, 4, 5, 6, 7, 8, 10, 12]

def crible(NMAX, S=10_000_000):
    """μ(n) par segments ; renvoie les points x (fins de segment), M(x) et les sommes par classe modulo q."""
    R = math.isqrt(NMAX) + 1
    sv = np.ones(R + 1, bool); sv[:2] = False
    for i in range(2, math.isqrt(R) + 1):
        if sv[i]: sv[i * i::i] = False
    premiers = np.nonzero(sv)[0]; lp = np.log(premiers).astype(np.float32)
    M = 0; Sq = {q: np.zeros(q, np.int64) for q in QS}
    xs, Ms, Sqs = [], [], {q: [] for q in QS}
    lo = 1
    while lo <= NMAX:
        hi = min(lo + S, NMAX + 1); n = hi - lo
        cnt = np.zeros(n, np.int8); lg = np.zeros(n, np.float32); sqf = np.ones(n, bool)
        for p, l in zip(premiers.tolist(), lp.tolist()):
            if p >= hi: break
            cnt[(-lo) % p::p] += 1; lg[(-lo) % p::p] += l
            if p * p < hi: sqf[(-lo) % (p * p)::p * p] = False
        ns = np.arange(lo, hi, dtype=np.int64)
        grand = (np.log(ns.astype(np.float64)) - lg) > 1e-3          # il reste un facteur premier > √NMAX
        mu = np.where(sqf, 1 - 2 * ((cnt + grand) & 1).astype(np.int64), 0)
        M += int(mu.sum())
        for q in QS: Sq[q] += np.bincount(ns % q, weights=mu, minlength=q).astype(np.int64)
        xs.append(hi - 1); Ms.append(M)
        for q in QS: Sqs[q].append(Sq[q].copy())
        lo = hi
    return np.array(xs), np.array(Ms), {q: np.array(v) for q, v in Sqs.items()}

# caractères de Dirichlet réels ou complexes, donnés par leurs valeurs sur les classes modulo q
CARACTERES = {
    "χ₃": (3, {1: 1, 2: -1}),
    "χ₄": (4, {1: 1, 3: -1}),
    "χ₅ (réel)": (5, {1: 1, 2: -1, 3: -1, 4: 1}),
    "χ₅ (complexe)": (5, {1: 1, 2: 1j, 3: -1j, 4: -1}),
    "χ₈": (8, {1: 1, 3: -1, 5: -1, 7: 1}),
    "χ₁₂": (12, {1: 1, 5: -1, 7: -1, 11: 1}),
}

def parieur_phase(KMAX):
    X = 2 ** KMAX
    mu = np.ones(X + 1, np.int8); mu[0] = 0
    isp = np.ones(X + 1, bool); isp[:2] = False
    for p in range(2, math.isqrt(X) + 1):
        if isp[p]: isp[p * p::p] = False
    for p in np.nonzero(isp)[0]:
        mu[p::p] *= -1
        if p * p <= X: mu[p * p::p * p] = 0
    for k in range(10, KMAX + 1):
        x = 2 ** k
        a = np.zeros(4 * x, np.complex128); a[1:x + 1] = mu[1:x + 1]
        best = float(np.abs(np.fft.fft(a)).max())
        print(f"x = 2^{k} : meilleur gain à phase linéaire {best:.0f}, soit {best / math.sqrt(x):.2f}·√x")

if __name__ == "__main__":
    if sys.argv[1] == "phase":
        parieur_phase(int(sys.argv[2])); sys.exit()
    NMAX = int(float(sys.argv[1])); t0 = time.time()
    xs, Ms, Sqs = crible(NMAX)
    racine = np.sqrt(xs.astype(float)); grand = xs >= 10 ** 8
    print(f"M({NMAX:.0e}) = {Ms[-1]} ; max |M(x)|/√x pour x ≥ 10⁸ : {np.max(np.abs(Ms[grand]) / racine[grand]):.3f} ({time.time() - t0:.0f} s)")
    for nom, (q, chi) in CARACTERES.items():
        s = sum(c * Sqs[q][:, a] for a, c in chi.items())
        print(f"{nom} : max |Σ μ(n)χ(n)|/√x = {np.max(np.abs(s[grand]) / racine[grand]):.3f}")
    g = max(np.max(np.abs(Sqs[q]).sum(1)[grand] / racine[grand]) for q in QS)
    print(f"meilleur parieur périodique choisi après coup (q ≤ 12) : max {g:.2f}·√x")
