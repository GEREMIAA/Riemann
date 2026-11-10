# La « signature » des zéros : avec les seuls zéros de ζ, chercher où L(x) = λ(1) + … + λ(x) peut passer au-dessus de 0
# (méthode de Haselgrove, 1958, et de Borwein–Ferguson–Mossinghoff, 2008 ; figures pourquoi_906.png et signature_zeros.png).
# Usage : python3 signature_zeros.py 5000    (zéros jusqu'à la hauteur 5000, environ une minute ; 1000 : quelques secondes)
import sys, math, numpy as np
from scipy.optimize import brentq
from scipy.special import loggamma
from dh_lib import hurwitz

T = float(sys.argv[1]) if len(sys.argv) > 1 else 1000.0
N1, N2 = max(400, int(T / 3)), max(900, int(2 * T / 3))           # termes d'Euler–Maclaurin

def theta(t):
    t = np.asarray(t, float)
    return loggamma(0.25 + 0.5j * t).imag - 0.5 * t * math.log(math.pi)

def Z(t):                                                          # fonction Z de Hardy, réelle sur la droite
    t = np.asarray(t, float)
    return (np.exp(1j * theta(t)) * hurwitz(0.5 + 1j * t, 1.0, N=N1, M=24, chunk=4000)).real

# 1) les zéros ρ = ½ + iγ avec 0 < γ < T (changements de signe de Z)
g = []
for a in np.arange(10.0, T, 250.0):
    t = np.arange(a, min(a + 250.0, T) + 1e-9, 0.01); z = Z(t)
    g += [brentq(lambda u: float(Z(u)), t[i], t[i + 1], xtol=1e-12) for i in np.nonzero(np.sign(z[:-1]) * np.sign(z[1:]) < 0)[0]]
g = np.unique(np.round(g, 10))
print(f"{len(g)} zéros sous la hauteur {T:g} (formule de Riemann–von Mangoldt : ≈ {theta(T) / math.pi + 1:.1f})")

# 2) l'amplitude de chaque onde : c = ζ(2ρ) / (ρ ζ'(ρ))
rho = 0.5 + 1j * g; h = 1e-6
dz = (hurwitz(rho + h, 1.0, N=N1, M=24, chunk=2000) - hurwitz(rho - h, 1.0, N=N1, M=24, chunk=2000)) / (2 * h)
c = hurwitz(2 * rho, 1.0, N=N2, M=24, chunk=1000) / (rho * dz)
b0 = 1 / hurwitz(np.array([0.5 + 0j]), 1.0)[0].real               # 1/ζ(½) ≈ −0,6848

# 3) A*(u) ≈ L(eᵘ)/√eᵘ : la somme des ondes, lissée par k(t) = (1 − t) cos πt + sin πt / π
k = (1 - g / T) * np.cos(np.pi * g / T) + np.sin(np.pi * g / T) / np.pi
def A(u):
    out = np.empty(len(u))
    for i in range(0, len(u), 4000):
        out[i:i + 4000] = b0 + np.real(np.exp(1j * np.outer(u[i:i + 4000], g)) @ (2 * k * c))
    return out

# 4) les plus hauts pics entre 10⁶ et 10²⁰
u = np.arange(math.log(1e6), math.log(1e20), 0.0002); a = A(u)
pk = [i for i in range(1, len(a) - 1) if a[i] >= a[i - 1] and a[i] >= a[i + 1]]
print("Les 6 plus hauts pics de la somme des ondes :")
for i in sorted(sorted(pk, key=lambda i: -a[i])[:6]):
    print(f"  x ≈ {math.exp(u[i]):.4g}   (ln x = {u[i]:.4f})   somme = {a[i]:+.4f}")
