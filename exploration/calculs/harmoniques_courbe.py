# Les « harmoniques » de la courbe y² = x³ + x + 1 sur les corps à 5, 25, 125… éléments (figure recurrence_courbe.png).
# Usage : python3 harmoniques_courbe.py   (demande numpy)
# La « récurrence » qui marche : la courbe E : y² = x³ + x + 1 sur les corps F_{5^m} (les « harmoniques »).
import json, math, itertools
import numpy as np
p = 5
# --- arithmétique dans F_{p^k} = F_p[X]/(P(X)) ---
def make_field(k, P):            # P : coefficients du polynôme unitaire de degré k, du plus bas au plus haut degré
    elems = list(itertools.product(range(p), repeat=k))
    def mul(a, b):
        r = [0] * (2 * k - 1)
        for i, ai in enumerate(a):
            if ai:
                for j, bj in enumerate(b): r[i + j] = (r[i + j] + ai * bj) % p
        for d in range(2 * k - 2, k - 1, -1):      # réduction modulo P
            c = r[d]
            if c:
                r[d] = 0
                for i in range(k): r[d - k + i] = (r[d - k + i] - c * P[i]) % p
        return tuple(r[:k])
    def add(a, b): return tuple((x + y) % p for x, y in zip(a, b))
    return elems, add, mul
def count_points(k, P):
    elems, add, mul = make_field(k, P)
    one = tuple([1] + [0] * (k - 1))
    squares = {}
    for y in elems:
        y2 = mul(y, y); squares[y2] = squares.get(y2, 0) + 1
    n = 1                                           # le point à l'infini
    for x in elems:
        rhs = add(add(mul(mul(x, x), x), x), one)
        n += squares.get(rhs, 0)
    return n
# F_5 (k=1, P = X), F_25 = F_5[X]/(X² − 2), F_125 = F_5[X]/(X³ + X + 1)
N1 = count_points(1, [0]); N2 = count_points(2, [(-2) % p, 0]); N3 = count_points(3, [1, 1, 0])
print("points par force brute : F_5 →", N1, "| F_25 →", N2, "| F_125 →", N3)
a1 = p + 1 - N1
a = [2, a1]
for m in range(1, 400): a.append(a1 * a[m] - p * a[m - 1])      # a_{m+1} = a_1 a_m − p a_{m−1}, entiers exacts
print("prévu par les harmoniques : F_25 →", p ** 2 + 1 - a[2], "| F_125 →", p ** 3 + 1 - a[3])
ratio = [a[m] / p ** (m / 2) for m in range(1, 401)]
run = np.maximum.accumulate(np.abs(ratio))
print("plus grand |a_m| / 5^(m/2) pour m ≤ 60 : %.6f ; pour m ≤ 400 : %.6f (borne : 2)" % (run[59], run[399]))
# mondes imaginaires : si |α| valait r·√5, l'écart pourrait atteindre 2·r^m
for r in (1.01, 1.1):
    print("monde imaginaire |α| = %g·√5 : 2·r^m vaut %.1f à m = 60 et %.1f à m = 400" % (r, 2 * r ** 60, 2 * r ** 400))
json.dump(dict(ratio=ratio, a=[str(x) for x in a[:401]], N=[N1, N2, N3]), open("harmoniques.json", "w"))
