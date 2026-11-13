# Les « nombres premiers » du papillon : les orbites périodiques de l'attracteur de Lorenz (figure papillon.png).
#
# Lorenz (1963) : dx/dt = σ(y − x), dy/dt = x(ρ − z) − y, dz/dt = xy − βz, avec σ = 10, ρ = 28, β = 8/3.
# Une trajectoire tourne autour de deux « ailes » sans jamais se répéter. Chaque boucle a un maximum de z ; on note L
# ou R l'aile où il a lieu (x < 0 ou x > 0). Une orbite périodique est un mot cyclique en L et R, et, comme pour les
# nombres premiers, toute trajectoire se décompose (s'ombre) sur ces orbites. Leurs « tailles » sont leurs périodes T_p,
# des nombres réels quelconques : ce sont des nombres premiers qui ne sont pas des entiers.
#
# Méthode : (1) une longue trajectoire donne l'application de Lorenz z_k → z_{k+1} entre maxima successifs, à deux
# branches (« rester sur la même aile » ou « changer d'aile ») ; (2) pour chaque mot de Lyndon (mot cyclique primitif)
# on obtient un point périodique de cette application par itération inverse (contractante), d'où un point de départ ;
# (3) on l'affine par la méthode de Newton sur le flot complet (équations variationnelles), avec la condition « maximum
# de z » ; (4) on vérifie le mot de l'orbite obtenue, et on garde sa période T_p et son multiplicateur instable Λ_p.
# Si le départ échoue, on recommence depuis un autre point du même mot (rotation). Deux cœurs en parallèle.
# Viswanath (2003) a trouvé une orbite pour chacun des mots de longueur 2 à 20 (111 011 orbites) : on doit tous les
# retrouver ; le programme affiche ceux qui manqueraient.
# Usage : python3 papillon_premiers.py 13        (mots jusqu'à 13 lettres ; une dizaine de minutes sur deux cœurs)
import sys, math, json, time
import numpy as np
from scipy.integrate import solve_ivp
from multiprocessing import Pool

SIG, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
def champ(t, u):
    x, y, z = u[0], u[1], u[2]
    return np.array([SIG * (y - x), x * (RHO - z) - y, x * y - BETA * z])
def jac(u):
    x, y, z = u[0], u[1], u[2]
    return np.array([[-SIG, SIG, 0.0], [RHO - z, -1.0, -x], [y, x, -BETA]])
def champ_var(t, U):
    M = U[3:].reshape(3, 3)
    return np.concatenate([champ(t, U[:3]), (jac(U) @ M).ravel()])
def zmax(t, u): return u[0] * u[1] - BETA * u[2]
zmax.direction = -1

def maxima(u0, T, rtol=1e-10):
    s = solve_ivp(champ, (0, T), u0, method="DOP853", rtol=rtol, atol=1e-12, events=zmax)
    return s.t_events[0], s.y_events[0]

def lyndon(n):
    """mots de Lyndon de longueur n sur {0 = L, 1 = R} (algorithme de Duval)"""
    out, w = [], [-1]
    while w:
        w[-1] += 1; m = len(w)
        if m == n: out.append(tuple(w))
        while len(w) < n: w.append(w[len(w) - m])
        while w and w[-1] == 1: w.pop()
    return out

def canon(m):
    n = len(m); return min(tuple(m[i:] + m[:i]) for i in range(n))

def application(u0, T):
    """les maxima successifs d'une longue trajectoire : z_k, aile, et (x, y) en fonction de z sur chaque aile"""
    tt, P = maxima(u0, T)
    P = P[50:]; z = P[:, 2]; aile = (P[:, 0] > 0).astype(int)
    chg = aile[1:] != aile[:-1]
    br = {}
    for e in (0, 1):
        m = chg == e; a, b = z[:-1][m], z[1:][m]; o = np.argsort(b); b, a = b[o], a[o]
        bas = np.polyfit(b[:40], a[:40], 1)                  # prolongement linéaire sous le plus petit point vu
        br[e] = (b, a, bas)                                  # branche inverse : z_{k+1} ↦ z_k
    xy = {}
    for w in (0, 1):
        m = aile == w; o = np.argsort(z[m]); xy[w] = (z[m][o], P[m][o, 0], P[m][o, 1])
    dt = np.diff(tt[50:]); o = np.argsort(z[:-1])                 # durée d'une boucle en fonction de z
    return dict(br=br, xy=xy, tau=(z[:-1][o], dt[o]), zmin=float(z.min()), zmax=float(z.max()), z=z, aile=aile)

def inverse(zz, e, A, marge=2.5):
    b, a, bas = A["br"][e]
    if zz < b[0]:
        return None if zz < b[0] - marge else float(np.polyval(bas, zz))
    if zz > b[-1]: return float(a[-1])                       # au sommet : la pointe (le passage près de l'origine)
    return float(np.interp(zz, b, a))

def orbite_1d(mot, A, iters=80):
    """l'orbite périodique de l'application de Lorenz qui suit le mot : les z des n maxima successifs"""
    n = len(mot); e = [int(mot[(k + 1) % n] != mot[k]) for k in range(n)]
    zz = 0.5 * (A["zmin"] + A["zmax"]); traj = [0.0] * n
    for _ in range(iters):
        for k in range(n - 1, -1, -1):                       # z_k = g_{e_k}(z_{k+1})
            zz = inverse(zz, e[k], A)
            if zz is None: return None
            traj[k] = zz
    return traj

def point3d(aile, z, A):
    zs, xs, ys = A["xy"][aile]
    return np.array([np.interp(z, zs, xs), np.interp(z, zs, ys), z])

def tir_multiple(mot, traj, A, tol=1e-11, it=25):
    """méthode de Newton sur toute l'orbite à la fois : un point par maximum de z, un temps par boucle (4n inconnues)"""
    n = len(mot)
    U = np.array([point3d(mot[k], traj[k], A) for k in range(n)])
    tau = np.array([np.interp(traj[k], *A["tau"]) for k in range(n)])
    for _ in range(it):
        F = np.zeros(4 * n); J = np.zeros((4 * n, 4 * n)); Ms = []
        for k in range(n):
            s = solve_ivp(champ_var, (0, tau[k]), np.concatenate([U[k], np.eye(3).ravel()]), method="DOP853", rtol=1e-12, atol=1e-13)
            fin = s.y[:3, -1]; M = s.y[3:, -1].reshape(3, 3); Ms.append(M); k1 = (k + 1) % n
            F[3 * k:3 * k + 3] = fin - U[k1]
            J[3 * k:3 * k + 3, 3 * k:3 * k + 3] += M; J[3 * k:3 * k + 3, 3 * k1:3 * k1 + 3] -= np.eye(3)
            J[3 * k:3 * k + 3, 3 * n + k] = champ(0, fin)
            F[3 * n + k] = zmax(0, U[k]); J[3 * n + k, 3 * k:3 * k + 3] = [U[k][1], U[k][0], -BETA]
        if np.max(np.abs(F)) < tol:
            Mt = np.eye(3)
            for M in Ms: Mt = M @ Mt
            return U[0].copy(), float(tau.sum()), Mt
        d = np.linalg.solve(J, -F); U = U + d[:3 * n].reshape(n, 3); tau = tau + d[3 * n:]
        if np.any(tau < 0.2) or np.any(tau > 25): return None
    return None

def newton(u0, n, tol=1e-11, it=14):
    tt, P = maxima(u0, 2.5 * n + 10)
    if len(tt) <= n: return None
    u, T = P[0].copy(), tt[n] - tt[0]
    for _ in range(it):
        s = solve_ivp(champ_var, (0, T), np.concatenate([u, np.eye(3).ravel()]), method="DOP853", rtol=1e-12, atol=1e-13)
        uT = s.y[:3, -1]; M = s.y[3:, -1].reshape(3, 3)
        F = np.concatenate([uT - u, [zmax(0, u)]])
        if np.max(np.abs(F)) < tol: return u, T, M
        J = np.zeros((4, 4)); J[:3, :3] = M - np.eye(3); J[:3, 3] = champ(0, uT); J[3, :3] = [u[1], u[0], -BETA]
        d = np.linalg.solve(J, -F); u = u + d[:3]; T = T + d[3]
        if not (0.3 < T < 4 * n + 4): return None
    return None

def mot_de(u, T):
    """le mot de l'orbite : les ailes des maxima de z rencontrés en un tour (le dernier, en t ≈ T, est le retour au départ)"""
    tt, P = maxima(u, T + 0.05, rtol=1e-12)
    sel = (tt > 0.05) & (tt < T + 0.02)
    return tuple(int(x > 0) for x in P[sel, 0])

A_GLOBAL = None
def init(A):
    global A_GLOBAL; A_GLOBAL = A

def chercher(m):
    """une orbite pour le mot de Lyndon m : tir simple depuis deux points du mot, puis, si besoin, tir multiple"""
    A = A_GLOBAL; n = len(m); trouves = []
    def garder(u, T, M):
        mm = mot_de(u, T)
        if len(mm) != n or len(set(mm)) == 1: return False
        ev = np.linalg.eigvals(M); o = np.argsort(-np.abs(ev))
        trouves.append(dict(mot=canon(mm), T=float(T), Lambda=float(ev[o[0]].real), stable=float(ev[o[2]].real), u=u.tolist()))
        return canon(mm) == m
    for i in (0, n // 2):
        mr = m[i:] + m[:i]; traj = orbite_1d(mr, A)
        if traj is None: continue
        r = newton(point3d(mr[0], traj[0], A), n)
        if r is not None and garder(*r): return trouves
    traj = orbite_1d(m, A)
    if traj is not None:
        r = tir_multiple(m, traj, A)
        if r is not None and garder(*r): return trouves
    return trouves

def lyapunov(u0, T=3000.0, pas=1.0):
    """le plus grand exposant de Lyapunov : un vecteur tangent, renormalisé à chaque unité de temps"""
    u = np.array(u0, float); v = np.array([1.0, 0.0, 0.0]); somme = 0.0
    def f(t, U): return np.concatenate([champ(t, U[:3]), jac(U) @ U[3:]])
    for k in range(int(T / pas)):
        s = solve_ivp(f, (0, pas), np.concatenate([u, v]), method="DOP853", rtol=1e-10, atol=1e-12)
        u, v = s.y[:3, -1], s.y[3:, -1]; nv = np.linalg.norm(v); somme += math.log(nv); v = v / nv
    return somme / T

if __name__ == "__main__":
    NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 12; t0 = time.time()
    u0 = solve_ivp(champ, (0, 50), [1.0, 1.0, 1.0], method="DOP853", rtol=1e-10, atol=1e-12).y[:, -1]
    A = application(u0, 16000.0)
    print(f"application de Lorenz : {len(A['z'])} maxima ; z entre {A['zmin']:.4f} et {A['zmax']:.4f} ; {time.time() - t0:.0f} s", flush=True)
    # l'effet papillon : deux départs à 10⁻¹⁰ l'un de l'autre
    s1 = solve_ivp(champ, (0, 40), u0, method="DOP853", rtol=1e-12, atol=1e-13, dense_output=True)
    s2 = solve_ivp(champ, (0, 40), u0 + np.array([1e-10, 0, 0]), method="DOP853", rtol=1e-12, atol=1e-13, dense_output=True)
    tg = np.linspace(0, 40, 2001); ecart = np.linalg.norm(s1.sol(tg) - s2.sol(tg), axis=0)
    orbites = {}
    with Pool(2, initializer=init, initargs=(A,)) as pool:
        for n in range(2, NMAX + 1):
            mots = [m for m in lyndon(n) if len(set(m)) > 1]
            a_chercher = []
            for m in mots:                                   # un seul mot par paire miroir (L ↔ R)
                mir = canon(tuple(1 - c for c in m))
                if m <= mir and m not in orbites: a_chercher.append(m)
            for res in pool.imap_unordered(chercher, a_chercher, chunksize=2):
                for o in res:
                    m = o["mot"]; uu = np.array(o["u"])
                    for mot, u in ((m, uu), (canon(tuple(1 - c for c in m)), uu * np.array([-1, -1, 1]))):
                        if mot not in orbites:
                            orbites[mot] = dict(mot="".join("LR"[c] for c in mot), n=len(mot), T=o["T"], Lambda=o["Lambda"],
                                                stable=o["stable"], u=u.tolist())
            manque = [m for m in mots if m not in orbites]
            print(f"longueur {n:2d} : {sum(1 for m in mots if m in orbites):4d} orbites sur {len(mots)} mots de Lyndon"
                  + (f" ; manquent : {' '.join(''.join('LR'[c] for c in m) for m in manque[:8])}" if manque else "")
                  + f" ; {time.time() - t0:.0f} s", flush=True)
    lam = lyapunov(u0)
    print(f"exposant de Lyapunov (vecteur tangent sur 3 000 unités de temps) : {lam:.4f} ; {time.time() - t0:.0f} s")
    L = sorted(orbites.values(), key=lambda o: (o["n"], o["mot"]))
    json.dump(dict(orbites=L, ecart_t=tg.tolist(), ecart=ecart.tolist(), lyapunov=lam,
                   application=dict(z=A["z"][:6000].tolist(), aile=A["aile"][:6000].tolist())),
              open("papillon_premiers.json", "w"))
    for o in L[:8]: print(o["mot"], f"T = {o['T']:.10f}", f"Λ = {o['Lambda']:.6f}")
