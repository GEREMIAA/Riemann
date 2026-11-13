# La structure de la forme de Weil dans une fenêtre : ce qui se démontre de l'étape 2 (figure structure_de_weil.png).
#
# Dans la fenêtre [1/√x, √x], l'énergie de Weil s'écrit W = P + B, où P est le terme des pôles de ζ et B tout le reste
# (place archimédienne et nombres premiers). Sur les ondes paires, P(φ) = +2⟨φ, c⟩², c(t) = ch(t/2) ; sur les ondes
# impaires, P(φ) = −2⟨φ, s⟩², s(t) = sh(t/2) (lemme 5 du README). Ce programme vérifie numériquement trois énoncés
# démontrés dans la note demontre.pdf :
#   Lemme 6 (Perron–Frobenius) : l'onde la plus basse de B est strictement positive, paire, seule à son niveau λ₀(B).
#   Lemme 7 (entrelacement)    : la plus petite énergie paire μ_p de W est entre λ₀(B) et la deuxième énergie paire de B,
#                                elle est simple, et elle est la racine de 1 + 2⟨c, (B − μ)⁻¹c⟩ = 0.
#                                « Presque nulle » se lit donc ⟨c, B⁻¹c⟩ ≈ −½ ; de même ⟨s, B⁻¹s⟩ ≈ +½ côté impair.
#   Lemme 8 (sous l'hypothèse de Riemann) : μ_p ≤ μ_i · R/γ₁², où μ_i est la plus petite énergie impaire, ψ l'onde impaire
#                                qui la réalise, Ψ sa primitive et R = ‖ψ‖²/‖Ψ‖² : l'onde paire Ψ est γ₁² ≈ 200 fois plus
#                                silencieuse en chaque zéro.
# Ce qui reste à démontrer sans l'hypothèse : μ_p < μ_i (« la plus basse est paire »).
# Usage : python3 structure_de_weil.py 8 20 120      (x, nombre d'ondes de chaque parité, chiffres)
import sys, json, math
from decimal import Decimal as D
import numpy as np
import weil_hp as W
import copie_selberg as CS

GAMMA1 = 14.134725141734693

def mat(M): return np.array([[float(v) for v in r] for r in M])
def add(M1, M2): return [[x + y for x, y in zip(r1, r2)] for r1, r2 in zip(M1, M2)]
def dot(u, v): return sum(x * y for x, y in zip(u, v))

def analyse(X, N):
    a = D(X).ln() / 2; P = W.pi(); af = float(a)
    # ------------------------------------------------------------ secteur pair
    Mp, parts = W.weil_matrix(D(X), N, parts=True)
    Kp = parts["K"]
    Bp = add(parts["arch"], parts["prime"])
    for i in range(N): Bp[i][i] -= parts["const"]
    e = (a / 2).exp(); ch = (e + 1 / e) / 2; sh = (e - 1 / e) / 2
    c = [(1 if m % 2 else -1) * 2 * Kp[m - 1] * ch / (Kp[m - 1] ** 2 + D("0.25")) for m in range(1, N + 1)]   # ⟨cos(K_m t), ch(t/2)⟩
    # contrôle : M = B + 2 c cᵀ
    ecart = max(abs(Mp[i][j] - Bp[i][j] - 2 * c[i] * c[j]) for i in range(N) for j in range(N))
    lamB, VB = np.linalg.eigh(mat(Bp) / af)
    t = np.linspace(-af, af, 2001)[1:-1]
    f0 = np.cos(np.outer(t, [float(k) for k in Kp])) @ VB[:, 0]; f0 = f0 if f0[len(t) // 2] > 0 else -f0
    mu_p, v_p, res_p = W.smallest_eigenpair(Mp, np.linalg.eigh(mat(Mp))[1][:, 0], iterations=10)
    fp = np.cos(np.outer(t, [float(k) for k in Kp])) @ np.array([float(x) for x in v_p]); fp = fp if fp[len(t) // 2] > 0 else -fp
    S_p = dot(c, W.solve(Bp, c))                               # ⟨c, B⁻¹ c⟩
    # la deuxième énergie paire de B, minuscule : itération inverse (la valeur propre de plus petit module)
    lam1_Bp, _, _ = W.smallest_eigenpair(Bp, VB[:, 1], iterations=10)
    # ------------------------------------------------------------ secteur impair
    Mi = CS.matrice_impaire(D(X), N)
    Ki = [D(m) * P / a for m in range(1, N + 1)]
    s = [(1 if m % 2 else -1) * 2 * Ki[m - 1] * sh / (Ki[m - 1] ** 2 + D("0.25")) for m in range(1, N + 1)]      # ⟨sin(K_m t), sh(t/2)⟩ au signe près
    Bi = [[Mi[i][j] + 2 * s[i] * s[j] for j in range(N)] for i in range(N)]
    lamBi = np.linalg.eigvalsh(mat(Bi) / af)
    mu_i, v_i, res_i = W.smallest_eigenpair(Mi, np.linalg.eigh(mat(Mi))[1][:, 0], iterations=10)
    S_i = dot(s, W.solve(Bi, s))                               # ⟨s, B⁻¹ s⟩
    lam0_Bi, _, _ = W.smallest_eigenpair(Bi, np.linalg.eigh(mat(Bi))[1][:, 0], iterations=10)
    # R = ‖ψ‖²/‖Ψ‖², Ψ(t) = ∫_{−a}^t ψ = −Σ (v_m/K_m)(cos(K_m t) − (−1)^m)
    q = [v_i[m] / Ki[m] for m in range(N)]
    nPsi = a * dot(q, q) + 2 * a * sum((1 if (m + 1) % 2 == 0 else -1) * q[m] for m in range(N)) ** 2
    R = a * dot(v_i, v_i) / nPsi
    return dict(x=float(X), N=N, a=af, ecart=float(ecart),
                lamB=[float(v) for v in lamB[:4]], lamB_impair=[float(v) for v in lamBi[:3]],
                bosse_B_min=float(f0.min() / f0.max()), bosse_W_min=float(fp.min() / fp.max()),
                mu_pair=float(mu_p / a), mu_impair=float(mu_i / a), residus=[float(res_p), float(res_i)],
                lam1_B_pair=float(lam1_Bp / a), lam0_B_impair=float(lam0_Bi / a),
                regle_paire=float(1 + 2 * S_p), regle_impaire=float(1 - 2 * S_i),
                R=float(R), borne=GAMMA1 ** 2 / float(R),
                t=t[::10].tolist(), bosse_B=(f0[::10] / np.sqrt(np.trapezoid(f0 ** 2, t))).tolist(),
                bosse_W=(fp[::10] / np.sqrt(np.trapezoid(fp ** 2, t))).tolist())

if __name__ == "__main__":
    X = sys.argv[1] if len(sys.argv) > 1 else "8"; N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    W.set_precision(int(sys.argv[3]) if len(sys.argv) > 3 else 120)
    r = analyse(X, N)
    print(f"x = {X}, {N} ondes de chaque parité (contrôle M = B + 2ccᵀ : {r['ecart']:.1e})")
    print(f"  sans les pôles : énergies paires de B : {r['lamB'][0]:+.4f}, {r['lamB'][1]:+.4f}, {r['lamB'][2]:+.4f} ; impaires : {r['lamB_impair'][0]:+.4f}, {r['lamB_impair'][1]:+.4f}")
    print(f"  onde la plus basse de B : minimum/maximum = {r['bosse_B_min']:+.3e} (positive si > 0) ; de W : {r['bosse_W_min']:+.3e}")
    print(f"  avec les pôles : plus petite énergie paire μ_p = {r['mu_pair']:.3e} ; impaire μ_i = {r['mu_impair']:.3e} ; rapport {r['mu_impair'] / r['mu_pair']:.1f}")
    print(f"  entrelacement pair : λ₀(B) = {r['lamB'][0]:+.3f} < μ_p = {r['mu_pair']:.3e} < λ₁(B pair) = {r['lam1_B_pair']:.3e} : {r['lamB'][0] < r['mu_pair'] < r['lam1_B_pair']}")
    print(f"  entrelacement impair : μ_i = {r['mu_impair']:.3e} < λ₀(B impair) = {r['lam0_B_impair']:.3e} : {r['mu_impair'] < r['lam0_B_impair']}")
    print(f"  règles de somme : 1 + 2⟨c, B⁻¹c⟩ = {r['regle_paire']:+.3e} ; 1 − 2⟨s, B⁻¹s⟩ = {r['regle_impaire']:+.3e}")
    print(f"  lemme 8 : R = {r['R']:.3f}, donc μ_i/μ_p ≥ γ₁²/R = {r['borne']:.1f} si l'hypothèse est vraie (observé : {r['mu_impair'] / r['mu_pair']:.1f})")
    json.dump(r, open(f"structure_{X}_{N}.json", "w"))
