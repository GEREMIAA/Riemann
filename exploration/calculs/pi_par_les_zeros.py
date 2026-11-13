# Compter exactement les nombres premiers avec les zéros de ζ : la formule explicite de Riemann, rendue praticable.
#
# Riemann (1859), démontré par von Mangoldt (1895) : Π(x) = Σ_{p^k ≤ x} 1/k s'écrit li(x) − Σ_ρ li(x^ρ) + petits termes.
# Telle quelle, la somme sur les zéros converge trop lentement. Méthode analytique (Lagarias–Odlyzko 1987, Galway, Platt) :
# on remplace la marche 1[t ≤ x] par une marche lissée, K((ln t − ln x)) avec K(v) = ½ erfc(v/(√2 λ)) ; alors
#   Π(x) = [partie lisse, donnée EXACTEMENT par la formule explicite, où les zéros n'interviennent que jusqu'à γ ≈ 7/λ]
#        + [correction locale : les seules puissances de premiers à moins de 9λ de x en échelle logarithmique].
# Partie lisse, pour le poids w(t) = C(ln t)·K(ln t − L)/ln t (C : une marche lisse qui coupe sous t = 2) :
#   Σ_n Λ(n) w(n) = w̃(1) − Σ_ρ w̃(ρ) − ∫ w(t) dt/(t(t² − 1)),   w̃(s) = ∫ w(t) t^(s−1) dt   (formule explicite de Weil),
#   w̃(ρ) = U(ρ) − D(ρ),  U(ρ) = ∫_0^∞ e^{(ρ−τ)L + (ρ−τ)²λ²/2}/(ρ − τ) dτ  (série de Watson en 1/L),  D(ρ) = ∫ C′(u) Ei(ρu) du.
# Puis π(x) = Π(x) − Σ_{k≥2} π(x^{1/k})/k. Le résultat doit tomber à moins de 10⁻³ d'un entier.
# Usage : python3 pi_par_les_zeros.py zeros_precis.npy ./crible_fenetre 1e6 1e7 … 1e14
import sys, math, subprocess, json, time
from decimal import Decimal, getcontext
import numpy as np
from scipy.special import erfc, exp1

LAM = 6.0e-5                 # largeur de la marche lissée (en ln x) : les zéros comptent jusqu'à γ ≈ 7/λ ≈ 117 000
UA, UB = 0.05, 0.65          # la marche C monte de 0 à 1 entre t = e^0,05 et t = e^0,65 (sous 2 : aucun premier n'y est)
FEN = 9.0                    # la correction locale porte sur |ln n − L| ≤ 9λ
GX, GW = np.polynomial.legendre.leggauss(32)

def quad(f, a, b, panels):
    e = np.linspace(a, b, panels + 1); A, B = e[:-1, None], e[1:, None]
    u = ((A + B) / 2 + (B - A) / 2 * GX[None, :]).ravel(); w = ((B - A) / 2 * GW[None, :]).ravel()
    return u, w

def step_C(u):
    y = np.clip((u - UA) / (UB - UA), 0.0, 1.0)
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        f0 = np.where(y > 0, np.exp(-1 / np.where(y > 0, y, 1)), 0.0); f1 = np.where(y < 1, np.exp(-1 / np.where(y < 1, 1 - y, 1)), 0.0)
        S = f0 / (f0 + f1)
        df0 = np.where(y > 0, f0 / np.where(y > 0, y, 1) ** 2, 0.0); df1 = np.where(y < 1, f1 / np.where(y < 1, 1 - y, 1) ** 2, 0.0)
        dS = (df0 * f1 + f0 * df1) / (f0 + f1) ** 2
    return np.nan_to_num(S), np.nan_to_num(dS) / (UB - UA)

def ei_dec(z, prec=60):
    """Ei(z), z réel > 0, en haute précision (série convergente)"""
    getcontext().prec = prec; z = Decimal(z)
    EULER = Decimal("0.5772156649015328606065120900824024310421593359399235988057672348848677")
    s, term, k = Decimal(0), Decimal(1), 0
    while True:
        k += 1; term = term * z / k; add = term / k; s += add
        if k > z and add < s * Decimal(10) ** (-(prec - 4)): break
    return EULER + z.ln() + s

# ---------------------------------------------------------------- les morceaux indépendants de x (calculés une fois)
def morceaux_fixes(gam):
    u, w = quad(lambda u: u, UA, UB, 64); C, dC = step_C(u)
    I1 = float(np.sum(w * C * np.exp(u) / u))                                    # ∫ C(u) e^u/u du entre UA et UB
    u2, w2 = quad(lambda u: u, UA, 40.0, 800); C2, _ = step_C(u2)
    J = float(np.sum(w2 * C2 / (u2 * np.expm1(2 * u2))))                         # zéros triviaux
    # D(ρ) = −∫ C′(u) E1(−ρu) du : décroît très vite avec γ (C′ est une bosse infiniment lisse)
    sel = gam < 3000.0; uD, wD = quad(lambda u: u, UA, UB, 160); _, dCD = step_C(uD)
    rho = 0.5 + 1j * gam[sel]; D = np.zeros(len(gam), complex)
    for i0 in range(0, sel.sum(), 200):
        r = rho[i0:i0 + 200, None]
        D[np.nonzero(sel)[0][i0:i0 + 200]] = -np.sum((wD * dCD)[None, :] * exp1(-r * uD[None, :]), axis=1)
    return I1, J, D

def somme_U(gam, L, lam, mmax=12):
    """Σ_ρ U(ρ) (ρ et ρ̄) : U(ρ) = e^{ρL + ρ²λ²/2} Σ_m c_m m!/L^{m+1}, c_m coefficients de Taylor de e^{−ρλ²τ + λ²τ²/2}/(ρ − τ)"""
    rho = 0.5 + 1j * gam
    e = [np.ones_like(rho)]; p1, p2 = -rho * lam ** 2, lam ** 2 / 2
    for j in range(1, mmax + 1):
        e.append((p1 * e[j - 1] + (2 * p2 * e[j - 2] if j >= 2 else 0)) / j)
    tot = np.zeros_like(rho)
    for m in range(mmax + 1):
        cm = sum(e[j] / rho ** (m - j + 1) for j in range(m + 1))
        tot += cm * math.factorial(m) / L ** (m + 1)
    U = np.exp(rho * L + rho ** 2 * lam ** 2 / 2) * tot
    return U

def pi_petits(N):
    s = np.ones(N + 1, bool); s[:2] = False
    for i in range(2, int(N ** 0.5) + 1):
        if s[i]: s[i * i::i] = False
    return s

def est_premier(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        y = pow(a, d, n)
        if y in (1, n - 1): continue
        for _ in range(r - 1):
            y = y * y % n
            if y == n - 1: break
        else: return False
    return True

def iroot(n, k):
    r = int(round(n ** (1.0 / k)))
    while r ** k > n: r -= 1
    while (r + 1) ** k <= n: r += 1
    return r

def pi_de(x, gam, fixes, crible, lam=LAM, verbose=True):
    t0 = time.time(); getcontext().prec = 60
    Lx = Decimal(x).ln(); L = float(Lx); dL = float(Lx - Decimal(L))
    I1, J, D = fixes
    # partie lisse : w̃(1) = I1 + [Ei(b) − Ei(UB)] + ∫_b^∞ K(u − L) e^u/u du, b = L − 12λ (pris exactement en double)
    b = L - 12 * lam
    I2d = ei_dec(Decimal(b)) - ei_dec(Decimal(UB)); N0 = int(I2d); I2 = float(I2d - N0)       # partie entière à part : précision ~10⁻⁸
    u, w = quad(lambda u: u, b, L + 12 * lam, 40)
    I3 = float(np.sum(w * 0.5 * erfc((u - L) / (math.sqrt(2) * lam)) * np.exp(u) / u))
    U = somme_U(gam, L, lam)
    SZ = 2 * math.fsum(np.real(U - D))
    lisse_frac = I1 + I2 + I3 - SZ - J; lisse = N0 + lisse_frac
    # correction locale : les premiers de la fenêtre (crible en C), puis les puissances p^k, k ≥ 2
    lo = int((Decimal(x) * (Decimal(-FEN * lam)).exp()).to_integral_value(rounding="ROUND_FLOOR"))
    hi = int((Decimal(x) * (Decimal(FEN * lam)).exp()).to_integral_value(rounding="ROUND_CEILING"))
    out = subprocess.run([crible, str(x), repr(lam), repr(dL), str(lo), str(hi)], capture_output=True, text=True, check=True)
    corr1, avant, apres = out.stdout.split(); corr1 = float(corr1)
    corrk = 0.0
    for k in range(2, int(math.log2(hi)) + 1):
        for p in range(max(2, iroot(lo, k)), iroot(hi, k) + 1):
            n = p ** k
            if lo <= n <= hi and est_premier(p):
                v = math.log1p((n - x) / x) + dL
                corrk += (0.5 * erfc(-v / (math.sqrt(2) * lam)) if n <= x else -0.5 * erfc(v / (math.sqrt(2) * lam))) / k
    Pi_frac = lisse_frac + corr1 + corrk
    # π(x) = Π(x) − Σ_{k≥2} π(x^{1/k})/k
    r2 = iroot(x, 2); crib = pi_petits(r2); cum = np.cumsum(crib)
    sous = math.fsum(cum[iroot(x, k)] / k for k in range(2, int(math.log2(x)) + 1))
    val_frac = Pi_frac - sous; n = N0 + round(val_frac); val = N0 + val_frac; ecart = val_frac - round(val_frac)
    if verbose:
        print(f"x = {x:.0e} : partie lisse {lisse:,.6f} (zéros : {-SZ:+,.6f}) ; correction locale {corr1 + corrk:+,.6f} "
              f"({int(avant) + int(apres):,} premiers dans la fenêtre [{lo:,}, {hi:,}]) ; π(x) ≈ {val:,.6f} → {n:,}  "
              f"(écart à l'entier {ecart:+.2e} ; {time.time() - t0:.0f} s)", flush=True)
    return dict(x=x, lam=lam, lisse=lisse, zeros=-SZ, correction=corr1 + corrk, fenetre=[lo, hi], premiers_fenetre=int(avant) + int(apres),
                pi_reel=val, pi=n, ecart=ecart, secondes=time.time() - t0)

if __name__ == "__main__":
    gam = np.load(sys.argv[1]); crible = sys.argv[2]
    fixes = morceaux_fixes(gam)
    print(f"morceaux fixes : I1 = {fixes[0]:.12f}, J = {fixes[1]:.12f}, |D| max = {np.abs(fixes[2]).max():.3e}, "
          f"|D(γ > 1000)| max = {np.abs(fixes[2][gam > 1000]).max():.1e}")
    res = [pi_de(int(float(a)), gam, fixes, crible) for a in sys.argv[3:]]
    json.dump(res, open("pi_par_les_zeros.json", "w"), indent=1)
