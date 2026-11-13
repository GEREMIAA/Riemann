# Combien de tours de suite du même côté ? La trajectoire qui sort de l'origine (sa « variété instable ») fait un grand tour
# à droite, puis 25 tours à gauche avant de changer de côté : aucune trajectoire de l'attracteur n'en fait davantage, et les
# mots qui contiennent une série de plus de 25 lettres identiques n'ont pas d'orbite périodique. (Jusqu'à 20 lettres, tous
# les mots en ont une : Viswanath, 2003.) Le résultat ne dépend pas du point de départ choisi sur la variété instable.
# Usage : python3 papillon_serie_maximale.py
import numpy as np, math
from scipy.integrate import solve_ivp
import papillon_premiers as P
lam = (-(P.SIG + 1) + math.sqrt((P.SIG - 1) ** 2 + 4 * P.SIG * P.RHO)) / 2
for eps in (1e-8, 1e-10, 1e-12):
    u0 = eps * np.array([1.0, 1 + lam / P.SIG, 0.0])
    s = solve_ivp(P.champ, (0, 60), u0, method="DOP853", rtol=1e-13, atol=1e-16, events=P.zmax)
    Pm = s.y_events[0]; zs = Pm[:, 2]; ailes = "".join("R" if x > 0 else "L" for x in Pm[:, 0])
    k = 1
    while k < len(ailes) and ailes[k] == ailes[1]: k += 1
    print(f"eps = {eps:.0e} : maxima de z le long de la variété instable de l'origine : {zs[0]:.5f}, {zs[1]:.5f}, {zs[2]:.5f} … ; mot : {ailes[:34]} ; série après la première boucle : {k - 1}")
