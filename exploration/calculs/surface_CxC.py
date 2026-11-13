# La surface C × C, en vrai : la preuve de Weil (1948) rejouée sur de vraies courbes (figure surface_CxC.png).
#
# Une courbe C : y² = f(x) sur le corps à q éléments (f de degré impair 2g + 1, sans facteur carré) a N_n points sur
# le corps à qⁿ éléments, et N_n = qⁿ + 1 − a_n avec a_n = Σ_j α_jⁿ, où les 2g nombres α_j sont les « zéros » de sa
# fonction zêta. L'hypothèse de Riemann de la courbe dit |α_j| = √q (théorème de Weil).
#
# Sur la surface C × C, on prend les deux fibres f₁ = C × {pt}, f₂ = {pt} × C, la diagonale Δ et le graphe Γ_n du
# Frobenius puissance n. Leurs nombres d'intersection ne demandent que des comptages de points :
#   f₁·f₂ = 1, f₁² = f₂² = 0, Γ_n·f₁ = qⁿ, Γ_n·f₂ = 1, Δ² = 2 − 2g, Γ_n² = qⁿ(2 − 2g), Δ·Γ_n = N_n,
#   et Γ_m·Γ_n = q^m · N_{n−m} pour m < n.
# Le théorème de l'indice de Hodge (Castelnuovo–Severi) dit que la forme d'intersection n'a qu'une direction positive.
# Après avoir retiré les fibres, les classes Δ′ et Γ′_n vivent dans une partie où la forme est négative : c'est un
# vrai produit scalaire (au signe près), et l'inégalité de Cauchy–Schwarz y donne |a_n| ≤ 2g·q^(n/2), c'est-à-dire
# l'hypothèse de Riemann de la courbe. En normalisant, la matrice de Gram des Γ′_n vaut −T avec
# T_mn = t_|m−n|, t_k = a_k / q^(k/2), t_0 = 2g : elle doit être de signe constant, et de rang au plus 2g.
#
# Le calcul compte les points avec courbes_rapide.c, en déduit la fonction zêta (identités de Newton, en entiers exacts),
# vérifie les comptages au-delà, construit les matrices, et fabrique un « monde imaginaire » où deux zéros quittent la droite.
#
# Et pour ζ : on construit la même matrice avec les seuls nombres premiers (la matrice de Weil de weil_entree_2.py, ondes
# paires vivant entre 1/√x et √x, x = 1 024), et on compte ses grandes directions quand on ajoute des ondes plus aiguës.
# Usage : python3 surface_CxC.py ./courbes_rapide ../../zeros150.json        (une à deux minutes)
import sys, json, math, subprocess
from fractions import Fraction
import numpy as np

EXE = sys.argv[1] if len(sys.argv) > 1 else "./courbes_rapide"
COURBES = [  # nom, p, coefficients de f (c0, c1, …), plus grand n compté directement
    ("E : y² = x³ + x + 1 sur F_5", 5, [1, 1, 0, 1], 9),
    ("genre 2 sur F_7", 7, [2, 1, 0, 3, 0, 1], 8),
    ("genre 6 sur F_3", 3, [2, 1, 0, 2, 1, 0, 0, 1, 2, 0, 1, 1, 0, 1], 15),
    ("genre 10 sur F_3", 3, [1, 2, 0, 1, 2, 2, 0, 1, 0, 0, 2, 1, 1, 0, 2, 0, 1, 2, 0, 0, 0, 1], 14),
]
NMAX = 60

def sans_facteur_carre(f, p):
    def norm(a):
        a = [c % p for c in a]
        while a and a[-1] == 0: a.pop()
        return a
    def reste(a, b):
        a = norm(a); b = norm(b); inv = pow(b[-1], p - 2, p)
        while len(a) >= len(b):
            c = a[-1] * inv % p; s = len(a) - len(b)
            for i in range(len(b)): a[s + i] = (a[s + i] - c * b[i]) % p
            a = norm(a)
        return a
    a, b = norm(f), norm([i * c for i, c in enumerate(f)][1:])
    while b: a, b = b, reste(a, b)
    return len(a) == 1

def zeta(p, g, a):
    """coefficients b_0..b_2g de P(T) = Π (1 − α_j T), à partir de a_1..a_g (identités de Newton, exactes)"""
    b = [Fraction(1)] + [Fraction(0)] * (2 * g)
    for k in range(1, g + 1):
        b[k] = -sum(Fraction(a[i]) * b[k - i] for i in range(1, k + 1)) / k
    for k in range(g + 1, 2 * g + 1): b[k] = b[2 * g - k] * Fraction(p) ** (k - g)     # équation fonctionnelle
    assert all(x.denominator == 1 for x in b), "coefficients non entiers : comptage faux ?"
    return [int(x) for x in b]

def traces(b, g, nmax):
    """a_n = Σ α_jⁿ pour n = 1..nmax, en entiers exacts (récurrence de Newton)"""
    s = [0] * (nmax + 1)
    for n in range(1, nmax + 1):
        s[n] = -sum(b[i] * s[n - i] for i in range(1, min(n, 2 * g + 1))) - (n * b[n] if n <= 2 * g else 0)
    return s

def gram(t, K):
    """T_mn = t_|m−n|, m, n = 0..K−1 (opposée de la matrice d'intersection normalisée des Δ′ = Γ′_0, Γ′_1, …)"""
    i = np.arange(K); return np.asarray(t, float)[np.abs(i[:, None] - i[None, :])]

res = {"courbes": []}
for nom, p, f, ndir in COURBES:
    d = len(f) - 1; g = (d - 1) // 2
    assert d % 2 == 1 and sans_facteur_carre(f, p)
    S = {}
    for n in range(1, ndir + 1):
        out = subprocess.run([EXE, str(p), str(n)] + [str(c) for c in f], capture_output=True, text=True, check=True).stdout.split()
        S[n] = int(out[3])
    acomp = {n: -S[n] for n in S}                                  # a_n = q^n + 1 − N_n = −S
    b = zeta(p, g, [0] + [acomp[n] for n in range(1, g + 1)])
    a = traces(b, g, NMAX)
    verif = {n: (a[n] == acomp[n]) for n in range(g + 1, ndir + 1)}
    assert all(verif.values()), f"{nom} : la fonction zêta ne prédit pas les comptages"
    # zéros : racines de Σ b_k q^(−k/2) z^(2g−k), sur le cercle unité si l'hypothèse de Riemann est vraie
    z = np.roots([b[k] / p ** (k / 2) for k in range(2 * g + 1)])
    th = np.sort(np.angle(z))
    t = [2 * g] + [a[n] / p ** (n / 2) for n in range(1, NMAX + 1)]
    T = gram([2 * g] + [acomp[n] / p ** (n / 2) for n in range(1, ndir + 1)], ndir + 1)      # comptages directs seuls
    ev_dir = np.linalg.eigvalsh(T); ev60 = np.linalg.eigvalsh(gram(t, NMAX + 1))
    tol = 1e-9 * ev60.max()
    M1 = np.array([[0, 1, 1, p], [1, 0, 1, 1], [1, 1, 2 - 2 * g, p + 1 - a[1]], [p, 1, p + 1 - a[1], p * (2 - 2 * g)]], float)
    r = dict(nom=nom, p=p, g=g, f=f, N=[p ** n + 1 - acomp[n] for n in range(1, ndir + 1)], b=b,
             verifie_jusqua=ndir, module_zeros=[float(abs(x)) for x in z], angles=th.tolist(),
             t=t, cos=[x / (2 * g) for x in t[1:]], cos_max=float(max(abs(x) for x in t[1:])) / (2 * g),
             vp_directs=ev_dir.tolist(), rang_directs=int(np.sum(ev_dir > 1e-9 * ev_dir.max())),
             vp_60=ev60.tolist(), rang_60=int(np.sum(ev60 > tol)), vp_negatives_60=int(np.sum(ev60 < -tol)),
             intersection_n1=M1.tolist(), positives_n1=int(np.sum(np.linalg.eigvalsh(M1) > 1e-9)))
    res["courbes"].append(r)
    print(f"{nom} : g = {g} ; N_1..N_{min(ndir, 6)} = {r['N'][:6]} ; zêta prédit les comptages jusqu'à n = {ndir} ; "
          f"|α|/√q ∈ [{min(r['module_zeros']):.12f}, {max(r['module_zeros']):.12f}] ; max |cos θ_n| (n ≤ {NMAX}) = {r['cos_max']:.4f}")
    print(f"   matrice des comptages directs ({ndir + 1} × {ndir + 1}) : rang {r['rang_directs']} (2g = {2 * g}), "
          f"plus petite valeur propre {ev_dir.min():+.2e} ; matrice 61 × 61 : rang {r['rang_60']}, négatives {r['vp_negatives_60']} ; "
          f"matrice 4 × 4 (n = 1) : {r['positives_n1']} direction positive")

# le monde imaginaire : sur la courbe de genre 10, les deux paires de zéros les plus proches fusionnent et quittent la droite
C = res["courbes"][-1]; g, p = C["g"], C["p"]; th = np.array(C["angles"]); pos = np.sort(th[th > 0])
k = int(np.argmin(np.diff(pos))); t1, t2 = pos[k], pos[k + 1]; tm = (t1 + t2) / 2
garde = [x for x in th if min(abs(abs(x) - t1), abs(abs(x) - t2)) > 1e-9]
assert len(garde) == 2 * g - 4
res["imaginaire"] = []
for delta in (0.0, 0.03, 0.06):
    rr = p ** delta
    zs = [complex(math.cos(x), math.sin(x)) for x in garde] + [rr * complex(math.cos(s * tm), math.sin(s * tm)) for s in (1, -1)] \
         + [complex(math.cos(s * tm), math.sin(s * tm)) / rr for s in (1, -1)]
    t = [float(2 * g)] + [float(sum(zz ** n for zz in zs).real) for n in range(1, NMAX + 1)]
    cosn = [x / (2 * g) for x in t[1:]]
    casse_angle = next((n for n in range(1, NMAX + 1) if abs(cosn[n - 1]) > 1), None)
    casse_matrice = next((K for K in range(2, NMAX + 2) if np.linalg.eigvalsh(gram(t, K)).min() < -1e-9 * K * 2 * g), None)
    res["imaginaire"].append(dict(delta=delta, cos=cosn, zeros=[[zz.real, zz.imag] for zz in zs], n_angle=casse_angle,
                                  K_matrice=casse_matrice, vp_60=np.linalg.eigvalsh(gram(t, NMAX + 1)).tolist()))
    print(f"monde imaginaire δ = {delta} (|α|/√q = {rr:.4f} et {1 / rr:.4f}, angle {tm:.4f}) : l'angle devient imaginaire à n = {casse_angle} ; "
          f"la matrice de Gram perd son signe dès K = {casse_matrice}")
res["paires_fusionnees"] = [float(t1), float(t2)]

# le rang de la matrice de Gram de la courbe de genre 10, quand on ajoute des graphes
tC = C["t"]; res["rang_courbe"] = [[K, int(np.sum(np.linalg.eigvalsh(gram(tC, K)) > 1e-9 * K * 2 * g))] for K in range(1, NMAX + 2)]

# et pour ζ : la matrice de Weil, sans aucun zéro ; ses grandes directions, comparées au nombre de zéros sous la fréquence k_N
from weil_entree_2 import weil_parts
zeros = np.array(json.load(open(sys.argv[2] if len(sys.argv) > 2 else "../../zeros150.json")), float)
X = 1024.0; a = 0.5 * math.log(X); res["zeta"] = []
for N in range(10, 181, 10):
    A, P = weil_parts(N, X); ev = np.sort(np.linalg.eigvalsh(A + P))[::-1]; kN = (N - 0.5) * math.pi / a
    grandes = int(np.sum(ev > 5.0)); suivante = float(ev[grandes]) if grandes < N else None
    res["zeta"].append(dict(N=N, frequence_max=kN, directions=grandes, zeros_sous=int(np.sum(zeros < kN)), plus_petite_grande=float(ev[grandes - 1]) if grandes else None,
                            suivante=suivante, plus_petite=float(ev.min()), vp=ev.tolist()))
    print(f"ζ, x = 1 024, {N} ondes (fréquences ≤ {kN:.1f}) : {grandes} grandes directions (> 5 ; la suivante vaut {suivante:.2e}), "
          f"{int(np.sum(zeros < kN))} zéros sous {kN:.1f} ; plus petite valeur propre {ev.min():+.1e}", flush=True)
json.dump(res, open("surface_CxC.json", "w"), indent=1)
