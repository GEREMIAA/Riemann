# Le bouton de Feynman (figure bouton_de_feynman.png). Crible segmenté jusqu'à NMAX, qui garde sur une grille en u = ln x :
#   N_k(x) = nombre d'entiers n ≤ x ayant exactement k facteurs premiers comptés avec multiplicité (Ω(n) = k).
#   Avec eux, on a pour tout nombre complexe z la somme S(z, x) = Σ_{n ≤ x} z^Ω(n) = Σ_k N_k(x) z^k ;
#   z = −1 donne la fonction de Liouville L(x) (l'hypothèse de Riemann : L(x) reste de l'ordre de √x).
#   M(x) = Σ μ(n), et les mêmes sommes pour des « fonctions de Möbius au hasard » : f(n) = Π_{p | n} ε_p sur les entiers
#   sans facteur carré, avec des signes ε_p = ±1 tirés à pile ou face (Wintner, 1944 : leur somme reste presque sûrement
#   de l'ordre de x^(½ + ε), c'est-à-dire que l'analogue de l'hypothèse de Riemann y est un théorème).
# Les signes au hasard viennent d'un mélange de bits (splitmix64) de p et du numéro du tirage : reproductibles.
# Usage : python3 liouville_hasard.py 1e9      (quelques minutes)
import sys, math, time
import numpy as np

NMAX = int(float(sys.argv[1])); SEG = 10_000_000; KMAX = 40; TIRAGES = 6
R = math.isqrt(NMAX) + 1
sv = np.ones(R + 1, bool); sv[:2] = False
for i in range(2, math.isqrt(R) + 1):
    if sv[i]: sv[i * i::i] = False
premiers = np.nonzero(sv)[0]
U = np.arange(math.log(1e3), math.log(NMAX), 0.0005); XG = np.exp(U).astype(np.int64); G = len(U)
Nk = np.zeros((G, KMAX), np.int64); MG = np.zeros(G, np.int64); FG = np.zeros((TIRAGES, G), np.int64)

def signe(p, s):
    """±1 « au hasard » pour le nombre premier p et le tirage s (mélange splitmix64)"""
    with np.errstate(over="ignore"):                    # les débordements font partie du mélange
        z = (np.asarray(p, np.uint64) * np.uint64(0x9E3779B97F4A7C15) + np.uint64(s + 1) * np.uint64(0xD1B54A32D192ED03))
        z ^= z >> np.uint64(30); z *= np.uint64(0xBF58476D1CE4E5B9); z ^= z >> np.uint64(27); z *= np.uint64(0x94D049BB133111EB); z ^= z >> np.uint64(31)
    return 1 - 2 * (z & np.uint64(1)).astype(np.int8)

EPS = np.array([signe(premiers, s) for s in range(TIRAGES)])          # signes des petits premiers
t0 = time.time(); lo = 1
with np.errstate(over="ignore"):
    while lo <= NMAX:
        hi = min(lo + SEG, NMAX + 1); n = hi - lo; ns = np.arange(lo, hi, dtype=np.int64)
        om = np.zeros(n, np.int8); prod = np.ones(n, np.int64); sqf = np.ones(n, bool); f = np.ones((TIRAGES, n), np.int8)
        for i, p in enumerate(premiers.tolist()):
            if p >= hi: break
            st = (-lo) % p; om[st::p] += 1; prod[st::p] *= p; f[:, st::p] *= EPS[:, i:i + 1]
            q = p * p
            if q < hi:
                sqf[(-lo) % q::q] = False
                while q < hi:
                    st = (-lo) % q; om[st::q] += 1; prod[st::q] *= p
                    if q > NMAX // p: break
                    q *= p
        cof = ns // prod; grand = cof > 1                                  # un facteur premier > √NMAX
        om[grand] += 1
        if grand.any():
            sg = np.array([signe(cof[grand], s) for s in range(TIRAGES)]); f[:, grand] *= sg
        mu = np.where(sqf, 1 - 2 * (om & 1).astype(np.int64), 0)
        g = np.searchsorted(XG, ns, side="left")                          # n compte pour les points X_j ≥ n
        ok = g < G
        cnt = np.bincount(g[ok] * KMAX + om[ok], minlength=G * KMAX).reshape(G, KMAX)
        Nk += np.cumsum(cnt, axis=0)                                       # les points au-delà du segment reçoivent tout
        # sommes de μ et des fonctions au hasard aux points de la grille
        bm = np.bincount(g[ok], weights=mu[ok], minlength=G).astype(np.int64)
        MG += np.cumsum(bm)
        for s in range(TIRAGES):
            FG[s] += np.cumsum(np.bincount(g[ok], weights=(f[s] * sqf)[ok], minlength=G).astype(np.int64))
        lo = hi
        if (hi - 1) % 100_000_000 == 0 or hi > NMAX:
            print(f"{hi - 1:.2e}  L(x) = {int(np.sum(Nk[-1] * (1 - 2 * (np.arange(KMAX) % 2))))}  M(x) = {MG[-1]}  {time.time() - t0:.0f} s", flush=True)
np.savez_compressed(f"liouville_{NMAX:.0e}.npz", U=U, X=XG, Nk=Nk, M=MG, F=FG)
print("fini", round(time.time() - t0), "s")
