# Une fleur de nombres premiers : un graphe quantique (figure fleur_de_fourier.png).
# Un seul sommet, M boucles (« pétales ») de longueurs ln 2, ln 3, ln 5, …, ln p_M. Une onde qui arrive au sommet
# repart dans les 2M directions selon une transformée de Fourier discrète : σ_jk = e^{2iπjk/2M}/√(2M)
# (chaque direction a la même chance). Option : un flux magnétique aléatoire sur chaque pétale (brise le renversement du temps).
# Les niveaux k_n sont les zéros réels de Z(k) = det(I − U(k)) e^{−ikL}/√det Σ, avec U(k) = Σ·diag(e^{i(k ℓ_b + A_b)}).
# On mesure :
#   - la statistique des écarts : rapport moyen ⟨r⟩ de deux écarts successifs (Atas et al., 2013 :
#     Poisson 0,386 ; GOE 0,531 ; GUE 0,600) et la proportion de petits écarts ;
#   - la « diffraction » D(x) = Σ_n w(k_n) e^{i k_n x} : des pics aux longueurs des orbites périodiques.
#     Pour la fleur : ln n pour tout produit n de premiers ≤ p_M ; pour ζ, la formule explicite ne donne que des creux
#     en ln pᵏ, de hauteur −ln p / p^{k/2}.
# Usage : python3 fleur_de_fourier.py 16 1500 zeros_100000.npy     (M pétales, niveaux jusqu'à k = 1500 ; deux minutes)
import sys, math, time, json
import numpy as np

def premiers(m):
    out, n = [], 2
    while len(out) < m:
        if all(n % q for q in out if q * q <= n): out.append(n)
        n += 1
    return out

def fleur(M):
    """matrice Σ de la fleur : liaison 2e parcourt le pétale e dans un sens (demi-arête 2e → 2e + 1), 2e + 1 dans l'autre"""
    d = 2 * M; j = np.arange(d); sig = np.exp(2j * np.pi * np.outer(j, j) / d) / np.sqrt(d)
    depart = np.array([2 * (b // 2) + (b % 2) for b in range(d)]); arrivee = np.array([2 * (b // 2) + 1 - (b % 2) for b in range(d)])
    return sig[np.ix_(depart, arrivee)]                  # Σ[b', b] : de la liaison b (qui arrive) à la liaison b' (qui part)

def Z(ks, Sig, lb, A, L, c):
    ph = np.exp(1j * (np.outer(ks, lb) + A[None, :]))
    return (np.linalg.det(np.eye(len(lb))[None] - Sig[None] * ph[:, None, :]) * np.exp(-1j * ks * L) * c).real

def niveaux(M, kmax, flux, graine=1):
    Sig = fleur(M); ell = np.log(np.array(premiers(M), float)); L = ell.sum()
    a = np.random.default_rng(graine).uniform(0, 2 * np.pi, M) if flux else np.zeros(M)
    lb = np.repeat(ell, 2); A = np.ravel(np.column_stack([a, -a])); c = 1 / np.sqrt(np.linalg.det(Sig) + 0j)
    ks = np.arange(1e-6, kmax, np.pi / (40 * L))
    f = np.concatenate([Z(ks[i:i + 4000], Sig, lb, A, L, c) for i in range(0, len(ks), 4000)])
    i = np.nonzero(np.sign(f[1:]) != np.sign(f[:-1]))[0]; lo, hi, flo = ks[i], ks[i + 1], f[i]
    for _ in range(40):                                  # dichotomie
        mid = (lo + hi) / 2; fm = Z(mid, Sig, lb, A, L, c); gauche = np.sign(fm) == np.sign(flo)
        lo = np.where(gauche, mid, lo); flo = np.where(gauche, fm, flo); hi = np.where(gauche, hi, mid)
    return (lo + hi) / 2, L

def statistiques(x):
    """x : niveaux dépliés (écart moyen 1)"""
    s = np.diff(x); s = s / s.mean(); r = np.minimum(s[1:], s[:-1]) / np.maximum(s[1:], s[:-1])
    return s, float(r.mean()), float(np.mean(s < 0.25))

def diffraction(niv, x, kmax):
    lv = niv[niv < kmax]; w = 0.5 * (1 + np.cos(np.pi * lv / kmax)); out = np.zeros(len(x), complex)
    for i in range(0, len(x), 400): out[i:i + 400] = np.exp(1j * np.outer(x[i:i + 400], lv)) @ w
    return out / w.sum()

if __name__ == "__main__":
    M, kmax = int(sys.argv[1]), float(sys.argv[2]); zeros = np.load(sys.argv[3]); res = {}; t0 = time.time()
    th = lambda t: t / 2 * np.log(t / (2 * np.pi)) - t / 2 - np.pi / 8 + 1 / (48 * t)
    for flux in (True, False):
        k, L = niveaux(M, kmax, flux); s, r, petits = statistiques(L / np.pi * k[k > 20])
        nom = "avec flux" if flux else "sans flux"
        res[nom] = dict(niveaux=len(k), weyl=L / np.pi * kmax, r=r, petits=petits, hist=np.histogram(s, np.linspace(0, 3.5, 36), density=True)[0].tolist())
        print(f"fleur à {M} pétales, {nom} : {len(k)} niveaux (loi de Weyl : {L / np.pi * kmax:.0f}) ; ⟨r⟩ = {r:.4f} ; écarts < 0,25 : {100 * petits:.2f} % ({time.time() - t0:.0f} s)")
        if flux: kf = k
    s, r, petits = statistiques(th(zeros[zeros > 1000]) / np.pi)
    res["zeros"] = dict(r=r, petits=petits, hist=np.histogram(s, np.linspace(0, 3.5, 36), density=True)[0].tolist())
    print(f"zéros de ζ entre 10³ et 10⁵ : ⟨r⟩ = {r:.4f} ; écarts < 0,25 : {100 * petits:.2f} %   (Poisson 0,386 ; GOE 0,531 ; GUE 0,600)")
    x = np.arange(0.3, 4.2, 0.0002); Dg = diffraction(kf, x, kmax); Dz = diffraction(zeros, x, 3000.0)
    for n in (2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15):
        i = np.argmin(abs(x - math.log(n))); sl = slice(i - 5, i + 6)
        print(f"  x = ln {n:>2} : fleur |D| = {abs(Dg[sl]).max():.4f} ; ζ, Re D = {Dz[sl].real[np.argmax(abs(Dz[sl].real))]:+.4f}")
    np.savez_compressed("fleur_de_fourier.npz", x=x, Dg=Dg, Dz=Dz, kf=kf)
    json.dump(res, open("fleur_de_fourier.json", "w"))
