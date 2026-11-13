# Ce que la retenue change : analyse des deux cribles (figure sans_retenue.png).
#
# Un entier écrit en binaire est aussi un polynôme à coefficients 0 ou 1 ; ces polynômes se multiplient comme les
# entiers, mais sans retenue. Le programme sans_retenue.c crible les deux mondes jusqu'à 2^40 et compte, pour les
# nombres de n+1 chiffres binaires (le « bloc » n) : A premiers ordinaires, I premiers sans retenue, B premiers dans
# les deux mondes. Ce script en tire quatre choses.
#
# 1. Le compte sans retenue est exact : I = (1/n) Σ_{d|n} μ(d) 2^(n/d) (Gauss), et Σ_{d|n} d·I_d = 2^n. Cette
#    deuxième égalité est la « somme de von Mangoldt » du monde sans retenue : elle tombe juste, sans aucune erreur.
#    Avec retenue, la même somme, ψ, s'écarte de 2^n d'une quantité de l'ordre de √(2^n) : c'est la musique des zéros.
# 2. Un monde sans retenue à une note : la courbe y² + xy = x³ + 1 (monde_a_une_note.c).
# 3. Les deux mondes sont-ils indépendants ? Si oui, B vaudrait 2·A·I/2^n (le facteur 2 : dans les deux mondes un
#    premier est impair). On mesure R = B / (2·A·I/2^n).
# 4. Les fuites. Être divisible par 3 (avec retenue) et par 11 (sans retenue) ne sont pas indépendants : la première
#    condition ne regarde que (nombre de 1 aux rangs pairs) − (nombre de 1 aux rangs impairs), la seconde que la
#    parité du nombre de 1 (Newman, 1969). C'est une « preuve par neuf » : le reste modulo 2^d − 1 s'obtient en
#    découpant l'écriture en tranches de d chiffres qu'on additionne, et le reste sans retenue modulo x^d − 1 en les
#    additionnant sans retenue. Les deux ne dépendent que du nombre de 1 à chaque rang modulo d. De même 7 et 111
#    (d = 3), 31, 33 et 11111 (d = 5)… On calcule exactement, par une matrice de transfert, la part de R que ces
#    fuites expliquent : on suit, chiffre après chiffre, le couple (m modulo M, polynôme modulo Q).
#    Modèle : parmi les nombres sans petit facteur dans aucun des deux mondes, les deux primalités sont indépendantes.
#
# Usage : python3 sans_retenue.py sans_retenue_2e40.txt monde_a_une_note.txt zeros_precis.npy      (une minute)
#         Le troisième fichier donne les zéros de ζ : le tableau des 138 069 zéros fabriqué par zeros_precis.py, ou, à défaut,
#         la liste ../../zeros150.json (150 zéros : la prédiction des écarts de ψ est alors moins précise, à 0,2 près).
import sys, json, math
import numpy as np

# ---------------------------------------------------------------- arithmétique sans retenue (entiers Python)
def pmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        a <<= 1; b >>= 1
    return r
def pmod(a, P):
    d = P.bit_length() - 1
    while a.bit_length() - 1 >= d: a ^= P << (a.bit_length() - 1 - d)
    return a
def premiers_sans_retenue(dmax):
    """tous les premiers sans retenue de degré ≤ dmax (crible)"""
    N = 2 << dmax; red = bytearray(N); out = []
    for P in range(2, N):
        if red[P]: continue
        out.append(P); d = P.bit_length() - 1
        if 2 * d <= dmax:
            for q in range(2, 1 << (dmax - d + 1)): red[pmul(P, q)] = 1
    return out
def mobius(n):
    m, k, p = 1, n, 2
    while p * p <= k:
        if k % p == 0:
            k //= p
            if k % p == 0: return 0
            m = -m
        p += 1
    return -m if k > 1 else m
def gauss(n): return sum(mobius(d) * 2 ** (n // d) for d in range(1, n + 1) if n % d == 0) // n
def premiers(n):
    c = np.ones(n + 1, bool); c[:2] = False
    for p in range(2, int(n ** 0.5) + 1):
        if c[p]: c[p * p::p] = False
    return np.nonzero(c)[0]

# ---------------------------------------------------------------- la matrice de transfert
def modele(S, T, nmax):
    """Pour chaque bloc n : U = nombre d'impairs du bloc sans facteur dans S (avec retenue) ni dans T (sans retenue),
    CS = sans facteur dans S, CT = sans facteur dans T. Renvoie R(n) = U·2^(n−1)/(CS·CT) : 1 si indépendants."""
    M = math.prod(S); Q = 1
    for P in T: Q = pmul(Q, P)
    NQ = 1 << (Q.bit_length() - 1); idx = np.arange(NQ)
    okA = np.ones(M, np.int64)
    for p in S: okA[::p] = 0
    okB = np.array([all(pmod(b, P) for P in T) for b in range(NQ)], np.int64)
    cnt = np.zeros((M, NQ), np.int64); cnt[1 % M, pmod(1, Q)] = 1; buf = np.empty_like(cnt)   # le chiffre de rang 0 vaut 1
    p2, xq, R = 2 % M, pmod(2, Q), {}
    for n in range(1, nmax + 1):
        okb, oka = okB[idx ^ xq], np.roll(okA, -p2)                 # le chiffre de rang n vaut 1
        U, CS, CT = int((cnt @ okb) @ oka), int(cnt.sum(axis=1) @ oka), int(cnt.sum(axis=0) @ okb)
        R[n] = U * 2 ** (n - 1) / (CS * CT) if CS * CT else float("nan")
        np.take(cnt, idx ^ xq, axis=1, out=buf)                     # puis le chiffre de rang n devient libre
        if p2: cnt[p2:] += buf[:M - p2]; cnt[:p2] += buf[M - p2:]
        else: cnt += buf
        p2 = 2 * p2 % M; xq = pmod(xq << 1, Q)
    return R
def force_brute(S, T, n):
    """le même R(n), en regardant tous les impairs du bloc un par un (contrôle de la matrice de transfert)"""
    m = np.arange(2 ** n + 1, 2 ** (n + 1), 2, dtype=np.int64)
    a = np.ones(len(m), bool); b = np.ones(len(m), bool)
    for p in S: a &= m % p != 0
    for P in T:
        r = np.zeros(len(m), np.int64)
        for i in range(n, -1, -1):                                  # reste modulo P, chiffre par chiffre (Horner)
            r = (r << 1) | ((m >> i) & 1); d = P.bit_length() - 1
            r ^= np.where((r >> d) & 1, P, 0)
        b &= r != 0
    return int((a & b).sum()) * 2 ** (n - 1) / (int(a.sum()) * int(b.sum()))

if __name__ == "__main__":
    L = {}
    for l in open(sys.argv[1]):
        v = l.split()
        L[int(v[0])] = dict(A=int(v[1]), I=int(v[2]), B=int(v[3]), Aimp=int(v[4]), A2=int(v[5]), J=int(v[6]),
                            I3=[int(x) for x in v[7:10]], I7=[int(x) for x in v[10:17]], th=float(v[17]))
    NMAX = max(L) + 1; ns = list(range(1, NMAX)); res = {"nmax": NMAX}
    # ------------------------------------------------------------ 1. le compte exact
    assert all(L[n]["I"] == gauss(n) for n in ns), "la formule de Gauss"
    assert all(sum(d * L[d]["I"] for d in ns if n % d == 0) == 2 ** n for n in ns), "la somme de von Mangoldt"
    print(f"Sans retenue : le crible retrouve la formule de Gauss pour les {NMAX - 1} blocs, et Σ d·I_d = 2^n exactement.")
    totA, totI, totB = (sum(L[n][k] for n in ns) for k in "AIB")
    print(f"Jusqu'à 2^{NMAX} : {totA} nombres premiers, {totI} premiers sans retenue, {totB} premiers dans les deux mondes.")
    res["total"] = dict(A=totA, I=totI, B=totB)
    # ψ par bloc : θ + les puissances de nombres premiers
    pp = np.zeros(NMAX + 2)
    for p in premiers(int(2 ** (NMAX / 2)) + 1):
        q = int(p) * int(p)
        while q < 2 ** NMAX: pp[q.bit_length() - 1] += math.log(p); q *= int(p)
    D = {n: (L[n]["th"] + pp[n] - 2 ** n) / 2 ** (n / 2) for n in ns}
    g = np.array([])
    if len(sys.argv) > 3: g = np.load(sys.argv[3]) if sys.argv[3].endswith(".npy") else np.array(json.load(open(sys.argv[3])))
    def par_les_zeros(n):
        x1, x2 = 2 ** n - 0.5, 2 ** (n + 1) - 0.5; rho = 0.5 + 1j * g
        return float(-2 * np.sum(((x2 ** rho - x1 ** rho) / rho).real) / 2 ** (n / 2))
    Dz = {n: par_les_zeros(n) for n in range(1, 61)} if len(g) else {}
    res["blocs"] = [dict(n=n, **{k: L[n][k] for k in ("A", "I", "B", "Aimp", "A2", "J")}, D=D[n]) for n in ns]
    res["Dz"] = [Dz.get(n) for n in range(1, 61)]
    print("\n n   premiers A  sans retenue I   A/I    écart de ψ/√(2^n)   par les zéros")
    for n in ns:
        if n >= 4 and (n % 4 == 0 or n >= NMAX - 3):
            print(f"{n:2d} {L[n]['A']:12d} {L[n]['I']:12d}  {L[n]['A'] / L[n]['I']:.4f}   {D[n]:+.4f}            {Dz.get(n, float('nan')):+.3f}")
    print(f"1/ln 2 = {1 / math.log(2):.4f} : la limite de A/I. Plus grand écart de ψ : {max(abs(D[n]) for n in ns if n >= 8):.3f}·√(2^n).")
    # ------------------------------------------------------------ 2. le monde à une note
    if len(sys.argv) > 2:
        K = [l.split() for l in open(sys.argv[2])]
        assert all(k[3] == k[4] for k in K), "la récurrence a_n = −a_(n−1) − 2 a_(n−2)"
        res["note"] = [dict(n=int(k[0]), N=int(k[2]), a=int(k[3])) for k in K]
        theta = math.atan2(math.sqrt(7), -1); res["theta"] = theta
        print(f"\nMonde à une note : {len(K)} corps, points comptés un par un ; a_n = 2·√(2^n)·cos(nθ), θ = {math.degrees(theta):.2f}°, "
              f"|a_n|/√(2^n) ≤ {max(abs(int(k[3])) / 2 ** (int(k[0]) / 2) for k in K):.5f} ≤ 2.")
    # ------------------------------------------------------------ 3. et 4. l'indépendance et les fuites
    N60 = 60
    R1 = modele([3], [0b11], N60)                                   # la fuite entre 3 et 11, seule
    for S, T, n in (([3, 7], [0b11, 0b111], 14), ([3, 11, 31], [0b11, 0b11111], 16), ([3, 5, 17], [0b11], 18)):
        assert abs(modele(S, T, n)[n] - force_brute(S, T, n)) < 1e-12, (S, T)      # contrôle de la matrice de transfert
    # Le modèle complet, famille par famille.
    # (a) Le premier sans retenue 11 (la parité du nombre de 1) avec les entiers : les nombres premiers qui comptent
    #     sont ceux qui divisent un 2^K − 1 avec K petit (3 ; 5 ; 7 ; 5 et 13, car 5·13 = 2^6 + 1 ; 17 ; 3 et 11…).
    #     R_K = fuite avec tous les diviseurs premiers de 2^K − 1 à la fois ; la part propre à K s'en déduit par
    #     l'inversion de Möbius, et on multiplie les parts.
    def diviseurs_premiers(m):
        out, p = [], 3
        while p * p <= m:
            if m % p == 0:
                out.append(p)
                while m % p == 0: m //= p
            p += 2
        return out + ([m] if m > 1 else [])
    KMAX = 24
    RK = {K: modele(diviseurs_premiers(2 ** K - 1), [0b11], N60) for K in range(2, KMAX + 1)}
    def part_propre(n):                                             # sans objet pour les tout petits blocs
        v = [(RK[K // d][n], mobius(d)) for K in range(2, KMAX + 1) for d in range(1, K) if K % d == 0]
        return math.prod(r ** m for r, m in v) if all(r > 0 for r, _ in v) else float("nan")
    F = {1: {n: part_propre(n) for n in range(1, N60 + 1)}}
    def ordre(p):
        d = 1
        while pow(2, d, p) != 1: d += 1
        return d
    autres = {n: 1.0 for n in range(1, N60 + 1)}                    # les autres nombres premiers < 3000, un par un
    for p in premiers(3000):
        if p == 2 or ordre(int(p)) <= KMAX: continue
        Rp = modele([int(p)], [0b11], N60)
        for n in autres: autres[n] *= Rp[n]
    # (b) Les premiers sans retenue qui divisent x^e − 1 (e impair) ne regardent que les chiffres rang par rang
    #     modulo e ; les entiers qui font de même sont les diviseurs de 2^(2e) − 1 = (2^e − 1)(2^e + 1). Pour chaque e,
    #     on calcule la fuite avec tous ces diviseurs à la fois, divisée par celle des périodes plus courtes.
    def pure(S, T, Tsous):
        a, b = modele(S, T, N60), modele(S, Tsous, N60); return {n: a[n] / b[n] for n in a}
    F[3] = pure([3, 5, 7, 13], [0b11, 0b111], [0b11])                               # 111 ; les premiers de 2^12 − 1
    F[5] = pure([3, 5, 11, 31, 41], [0b11, 0b11111], [0b11])                        # 11111 ; ceux de 2^20 − 1
    F[7] = pure([3, 43, 127], [0b11, 0b1011, 0b1101], [0b11])                       # 1011 et 1101 ; ceux de 2^14 − 1
    F[9] = pure([3, 7, 19, 73], [0b11, 0b111, 0b1001001], [0b11, 0b111])            # 1001001 ; ceux de 2^18 − 1
    Rtot = {n: F[1][n] * F[3][n] * F[5][n] * F[7][n] * F[9][n] * autres[n] for n in range(1, N60 + 1)}
    print("\n n   doubles premiers B   R = B/(2AI/2^n)   bruit     fuite 3–11 seule   modèle complet   écart/bruit")
    lignes = []
    for n in ns:
        if L[n]["B"] < 30: continue
        A, I, B = L[n]["A"], L[n]["I"], L[n]["B"]
        R = B * 2 ** n / (2 * A * I); s = R / math.sqrt(B)
        l1 = 2 * L[n]["Aimp"] / A                                    # la même chose pour 11 seul : parité du nombre de 1
        lignes.append(dict(n=n, R=R, s=s, R1=R1[n], Rm=Rtot[n], z=(R - Rtot[n]) / s, familles=[F[e][n] for e in (1, 3, 5, 7, 9)],
                           l1=l1, l1m=F[1][n] * autres[n], zl1=(l1 - F[1][n] * autres[n]) * math.sqrt(A), i3=L[n]["I3"][0] / I))
        if n >= 12: print(f"{n:2d} {B:14d}       {R:.6f}        {s:.6f}   {R1[n]:.6f}           {Rtot[n]:.6f}         {(R - Rtot[n]) / s:+.2f}")
    res["fuites"] = lignes; res["modele60"] = [Rtot[n] for n in range(1, N60 + 1)]; res["R1_60"] = [R1[n] for n in range(1, N60 + 1)]
    zz = [l["z"] for l in lignes if l["n"] >= 14]
    res["z_moyenne"], res["z_ecart_type"] = float(np.mean(zz)), float(np.std(zz))
    print(f"Blocs 14 à {NMAX - 1} : écart moyen au modèle {np.mean(zz):+.2f} bruit, écart-type {np.std(zz):.2f} (attendu : 0 et 1).")
    print(f"D'après le modèle, R − 1 vaut {Rtot[50] - 1:+.1e} au bloc 50 et {Rtot[60] - 1:+.1e} au bloc 60.")
    print("La parité du nombre de 1 chez les nombres premiers (2·Aimp/A), mesurée et modélisée :")
    for l in lignes[-6:]: print(f"   bloc {l['n']} : {l['l1']:.6f} et {l['l1m']:.6f} ({l['zl1']:+.1f} bruit)")
    # la parité du nombre de 1 chez les nombres premiers, et les multiples de 3 chez les premiers sans retenue
    n = NMAX - 1
    print(f"\nBloc {n} : {100 * L[n]['Aimp'] / L[n]['A']:.3f} % des nombres premiers ont un nombre impair de 1 ; "
          f"{100 * L[n]['I3'][0] / L[n]['I']:.3f} % des premiers sans retenue sont multiples de 3 (un tiers = 33,333 %).")
    # ------------------------------------------------------------ 5. les jumeaux sans retenue : P et P ^ 110
    S2 = 4.0
    for d in range(2, 60): S2 *= (1 - 1 / (2 ** d - 1) ** 2) ** gauss(d)
    res["S2"] = S2; res["jumeaux"] = [dict(n=n, J=L[n]["J"], pred=2 ** (n - 1) * S2 * (L[n]["I"] / 2 ** n) ** 2) for n in ns if n >= 3]
    print(f"\nJumeaux sans retenue (P et P ^ 110) : constante de Hardy–Littlewood sans retenue = {S2:.6f}")
    for n in sorted({min(20, NMAX - 1), min(30, NMAX - 1), NMAX - 1}): print(f"   bloc {n} : {L[n]['J']} paires ; prédit {2 ** (n - 1) * S2 * (L[n]['I'] / 2 ** n) ** 2:.0f} "
                                       f"(rapport {L[n]['J'] / (2 ** (n - 1) * S2 * (L[n]['I'] / 2 ** n) ** 2):.5f})")
    json.dump(res, open("sans_retenue.json", "w"))
