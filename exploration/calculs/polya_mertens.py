# Sommes de Liouville L(n) et de Mertens M(n) jusqu'à un milliard, par crible segmenté (figure vrai_puis_faux.png).
# Usage : python3 polya_mertens.py 1000000000   (demande numpy ; environ une minute)
# L(n) = Σ λ(k) (Liouville, conjecture de Pólya : L(n) ≤ 0 pour n ≥ 2) et M(n) = Σ μ(k) (Mertens),
# pour n ≤ NMAX, par crible segmenté. λ(k) = (−1)^Ω(k), μ(k) = λ(k) si k sans facteur carré, 0 sinon.
import numpy as np, math, json, time, sys
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000_000
S, B, BZ = 10_000_000, 10_000, 1_000            # segment, bloc (courbes), bloc du zoom
ZOOM = (905_900_000, 906_700_000)               # fenêtre autour du contre-exemple attendu
R = math.isqrt(NMAX) + 1
sv = np.ones(R + 1, bool); sv[:2] = False
for i in range(2, math.isqrt(R) + 1):
    if sv[i]: sv[i * i::i] = False
primes = np.nonzero(sv)[0].tolist()
powers = []                                      # (q = p^k, log p, est-ce p² ?)
for p in primes:
    q, k = p, 1
    while q <= NMAX:
        powers.append((q, math.log(p), k == 2)); q *= p; k += 1
L = M = 0
blocks, zoom, pos_runs, checks = [], [], [], {}
first_pos = None
t0 = time.time()
lo = 1
while lo <= NMAX:
    hi = min(lo + S, NMAX + 1); n = hi - lo
    cnt = np.zeros(n, np.int8); lg = np.zeros(n, np.float32); sqf = np.ones(n, bool)
    for q, lp, is_sq in powers:
        if q >= hi: continue
        st = (-lo) % q
        cnt[st::q] += 1; lg[st::q] += lp
        if is_sq: sqf[st::q] = False
    big = (np.log(np.arange(lo, hi, dtype=np.float64)) - lg) > 1.0      # un facteur premier > √NMAX reste
    odd = (cnt + big) & 1
    lam = (1 - 2 * odd.astype(np.int64))
    Ls = L + np.cumsum(lam); Ms = M + np.cumsum(lam * sqf)
    ns = np.arange(lo, hi, dtype=np.int64)
    # où L > 0 (n ≥ 2)
    pos = (Ls > 0) & (ns >= 2)
    if pos.any():
        d = np.diff(np.concatenate([[0], pos.astype(np.int8), [0]]))
        for a, b in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            j = a + int(np.argmax(Ls[a:b]))
            pos_runs.append([int(ns[a]), int(ns[b - 1]), int(Ls[j]), int(ns[j])])
            if first_pos is None: first_pos = int(ns[a])
    for k in range(1, 10):
        if lo <= 10 ** k < hi: checks[str(10 ** k)] = [int(Ls[10 ** k - lo]), int(Ms[10 ** k - lo])]
    Lb = Ls.reshape(-1, B); Mb = Ms.reshape(-1, B)
    ends = ns[B - 1::B]
    blocks.append(np.stack([ends, Lb[:, -1], Lb.max(1), Lb.min(1), Mb[:, -1], Mb.max(1), Mb.min(1)], 1))
    a, b = max(lo, ZOOM[0]), min(hi, ZOOM[1])
    if a < b:
        sl = slice(a - lo, b - lo)
        Lz = Ls[sl].reshape(-1, BZ); nz = ns[sl][BZ - 1::BZ]
        zoom.append(np.stack([nz, Lz[:, -1], Lz.max(1), Lz.min(1)], 1))
    L, M = int(Ls[-1]), int(Ms[-1])
    lo = hi
    if (lo - 1) % 100_000_000 == 0: print(f"{lo - 1:>13,}  L={L:>8}  M={M:>8}  {time.time() - t0:6.1f} s", flush=True)
blocks = np.concatenate(blocks); zoom = np.concatenate(zoom) if zoom else np.zeros((0, 4))
np.savez_compressed("polya_mertens.npz", blocks=blocks, zoom=zoom)
x = blocks[:, 0].astype(float); big = x >= 1e5; x0 = x - B + 1   # début du bloc
res = dict(NMAX=NMAX, first_positive_L=first_pos, positive_runs=pos_runs[:20], n_runs=len(pos_runs), checks=checks,
           max_M_over_sqrt=float(np.max(np.maximum(blocks[big, 5], -blocks[big, 6]) / np.sqrt(x0[big]))),
           L_over_sqrt_range=[float(np.min(blocks[big, 3] / np.sqrt(x[big]))), float(np.max(blocks[big, 2] / np.sqrt(x0[big])))],
           seconds=round(time.time() - t0, 1))
json.dump(res, open("polya_mertens.json", "w"), indent=1)
print(json.dumps(res, indent=1))
