# Le crible du « grand détour par Fourier » (figures musique_des_paires.png, zeros_et_jumeaux.png et musique_des_jumeaux.png).
# Crible segmenté jusqu'à NMAX ; sur une grille régulière en u = ln x (pas 0,0005) on garde :
#   ψ(x) = Σ_{n ≤ x} Λ(n), et π(x) ;
#   pour chaque écart h = 2, 4, …, 60 : C_h(x) = nombre de p ≤ x avec p et p + h premiers,
#                                       W_h(x) = Σ ln p · ln(p + h) sur ces p  (Hardy–Littlewood : W_h(x) ≈ S(h)·x).
#   pour quelques caractères de Dirichlet χ : ψ(x, χ) = Σ_{n ≤ x} χ(n) Λ(n)  (les « notes » des fonctions L(s, χ)).
# Et la variance de ψ(n + H) − ψ(n) − H pour n dans [X0, X0 + 10⁸] (premiers dans les petits intervalles,
# à comparer à Montgomery–Soundararajan : H·(ln(x/H) + B), B = 1 − γ − ln 2π).
# Usage : python3 crible_paires.py 1e10 1e9      (NMAX, X0 ; dix à quinze minutes, environ 1 Go de mémoire)
#         python3 crible_paires.py 1e8 1e7       (quelques secondes, pour essayer)
import numpy as np, math, json, time, sys
NMAX = int(float(sys.argv[1])); X0 = int(float(sys.argv[2])) if len(sys.argv) > 2 else 1_000_000_000
S = 10_000_000; HS = list(range(2, 61, 2)); HMAX = 64
VAR_LEN = 100_000_000; VAR_H = [10, 30, 100, 300, 1000, 3000, 10_000, 30_000, 100_000]; VMAX = max(VAR_H)
W3 = complex(-0.5, math.sqrt(3) / 2)                 # racine cubique de l'unité
CARACTERES = {                                        # caractère : (module, valeurs sur les classes premières au module)
    "chi3": (3, {1: 1, 2: -1}), "chi4": (4, {1: 1, 3: -1}), "chi5": (5, {1: 1, 2: -1, 3: -1, 4: 1}),
    "chi5i": (5, {1: 1, 2: 1j, 4: -1, 3: -1j}), "chi7c": (7, {1: 1, 3: W3, 2: W3 ** 2, 6: 1, 4: W3, 5: W3 ** 2}),
    "chi8": (8, {1: 1, 3: -1, 5: -1, 7: 1}), "chi12": (12, {1: 1, 5: -1, 7: -1, 11: 1}),
    "chi13": (13, {a: (1 if a in (1, 3, 4, 9, 10, 12) else -1) for a in range(1, 13)})}
QQ = math.lcm(*[q for q, _ in CARACTERES.values()])                 # un seul reste n mod QQ sert à tous les caractères
TABR = {nom: np.array([complex(v.get(a % q, 0)).real for a in range(QQ)]) for nom, (q, v) in CARACTERES.items()}
TABI = {nom: np.array([complex(v.get(a % q, 0)).imag for a in range(QQ)]) for nom, (q, v) in CARACTERES.items()}
R = math.isqrt(NMAX + VMAX + HMAX) + 1
sv = np.ones(R + 1, bool); sv[:2] = False
for i in range(2, math.isqrt(R) + 1):
    if sv[i]: sv[i * i::i] = False
base = np.nonzero(sv)[0]
ppow = []                                            # puissances p^k, k ≥ 2, avec leur poids ln p (pour ψ)
for p in base.tolist():
    q = p * p
    while q <= NMAX + VMAX + HMAX: ppow.append((q, math.log(p))); q *= p
ppow.sort(); ppq = np.array([q for q, _ in ppow], np.int64); ppl = np.array([l for _, l in ppow])
U = np.arange(math.log(1e3), math.log(NMAX), 0.0005); XG = np.exp(U).astype(np.int64)
psiG = np.zeros(len(U)); piG = np.zeros(len(U), np.int64)
chiG = np.zeros((len(CARACTERES), len(U)), complex); chiacc = np.zeros(len(CARACTERES), complex)
C = np.zeros((len(HS), len(U)), np.int64); W = np.zeros((len(HS), len(U)))
cnt = np.zeros(len(HS), np.int64); wsum = np.zeros(len(HS))
var_sum = np.zeros(len(VAR_H)); var_n = 0; psi = 0.0; npi = 0

def segment(lo, hi):
    """booléens « premier » sur [lo, hi)"""
    n = hi - lo; isp = np.ones(n, bool)
    if lo <= 1: isp[:2 - lo] = False
    for p in base.tolist():
        if p * p >= hi: break
        st = max(p * p, ((lo + p - 1) // p) * p)
        isp[st - lo::p] = False
    return isp

t0 = time.time(); lo = 0
while lo <= NMAX:
    hi = min(lo + S, NMAX + 1); n = hi - lo
    ext = VMAX + HMAX if X0 <= lo < X0 + VAR_LEN else HMAX
    isp = segment(lo, hi + ext)
    ns = np.arange(lo, hi + ext, dtype=np.int64)
    lam = np.where(isp, np.log(np.maximum(ns, 2).astype(np.float64)), 0.0)
    sel = (ppq >= lo) & (ppq < hi + ext); lam[ppq[sel] - lo] += ppl[sel]
    cs = np.cumsum(lam); pc = np.cumsum(isp[:n])
    g = np.nonzero((XG >= lo) & (XG < hi))[0]; j = XG[g] - lo
    psiG[g] = psi + cs[j]; piG[g] = npi + pc[j]
    rq = ns[:n] % QQ; nz = np.nonzero(lam[:n])[0]; lz = lam[:n][nz]; rz = rq[nz]      # seuls les n = pᵏ comptent
    jj = np.searchsorted(nz, j, side="right")                                          # nombre de pᵏ ≤ x dans le segment
    for c, nom in enumerate(CARACTERES):
        cr = np.concatenate([[0.0], np.cumsum(lz * TABR[nom][rz])])
        ci = np.concatenate([[0.0], np.cumsum(lz * TABI[nom][rz])]) if TABI[nom].any() else np.zeros(len(nz) + 1)
        chiG[c, g] = chiacc[c] + cr[jj] + 1j * ci[jj]; chiacc[c] += cr[-1] + 1j * ci[-1]
    for k, h in enumerate(HS):
        idx = np.nonzero(isp[:n] & isp[h:n + h])[0]               # p = lo + idx, p et p + h premiers
        w = np.cumsum(np.log((lo + idx).astype(float)) * np.log((lo + idx + h).astype(float))) if len(idx) else np.zeros(0)
        if len(g):
            r = np.searchsorted(idx, j, side="right")
            C[k, g] = cnt[k] + r
            W[k, g] = wsum[k] + (np.where(r > 0, w[np.maximum(r - 1, 0)], 0.0) if len(idx) else 0.0)
        if len(idx): cnt[k] += len(idx); wsum[k] += w[-1]
    if ext > HMAX:                                                 # variance dans les petits intervalles
        b = np.concatenate([[0.0], cs])
        for k, H in enumerate(VAR_H):
            dlt = b[H + 1:n + H + 1] - b[1:n + 1] - H                # ψ(x + H) − ψ(x) − H pour x = lo … hi − 1
            var_sum[k] += float(np.dot(dlt, dlt))
        var_n += n
    psi += cs[n - 1]; npi += int(pc[-1]); lo = hi
    if (hi - 1) % 1_000_000_000 == 0 or hi > NMAX:
        print(f"{hi - 1:.2e}  π = {npi}  jumeaux = {cnt[0]}  ψ − x = {psi - (hi - 1):.1f}  {time.time() - t0:.0f} s", flush=True)
np.savez_compressed(f"crible_{NMAX:.0e}.npz", U=U, X=XG, psi=psiG, pi=piG, C=C, W=W, HS=np.array(HS),
                    chi=chiG, caracteres=np.array(list(CARACTERES)))
json.dump(dict(NMAX=NMAX, pi=npi, paires={str(h): int(c) for h, c in zip(HS, cnt)}, X0=X0, longueur=var_n,
               variance={str(H): v for H, v in zip(VAR_H, (var_sum / max(var_n, 1)).tolist())}, secondes=time.time() - t0),
          open(f"crible_{NMAX:.0e}.json", "w"), indent=1)
print("fini", round(time.time() - t0), "s")
