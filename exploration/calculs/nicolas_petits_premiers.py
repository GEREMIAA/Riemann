# La partie « calcul fini » du théorème sur la marge de Nicolas (note demontre.pdf, théorème 9, point (a)).
# La marge F_k décroît à chaque pas tant que p_(k+1) ≤ 10¹⁹ : pour p_(k+1) ≥ 11 835, cela découle de la borne de Büthe
# x − θ(x) > 0,05·√x et du critère exact (lemme 8) ; pour les 1 436 pas restants, ce programme le vérifie directement, en
# 60 chiffres. Il contrôle aussi le lemme 8 sur tous les pas jusqu'à 10⁶ (δ ≥ ½ ln p + ¾ entraîne la baisse).
# Usage : python3 nicolas_petits_premiers.py        (une minute)
from decimal import Decimal as D, getcontext
import math
getcontext().prec = 60
N = 1_000_000
cr = bytearray([1]) * (N + 1); cr[0] = cr[1] = 0
for i in range(2, 1001):
    if cr[i]: cr[i * i::i] = bytearray(len(cr[i * i::i]))
ps = [i for i in range(2, N + 1) if cr[i]]
theta = D(2).ln() + D(3).ln()                                # θ(p_2) = ln 6
pire = None; nmarches = 0; min_ecart = None; viol = 0
for k in range(2, len(ps)):                                   # marche de p_k = ps[k-1] à p_{k+1} = ps[k]
    p = ps[k]; lp = D(p).ln()
    dF = -(1 - D(1) / p).ln() - ((theta + lp).ln() / theta.ln()).ln()
    delta = D(p) - theta; seuil = lp / 2 + D("0.75")
    if delta >= seuil and dF >= 0: viol += 1                  # contredirait le lemme N1
    if p < 12000:
        nmarches += 1
        if dF >= 0: print("REMONTÉE en", p)
        if pire is None or dF > pire[0]: pire = (dF, p)
    r = float(delta - seuil)
    if min_ecart is None or r < min_ecart[0]: min_ecart = (r, p, float(delta), float(seuil))
    theta += lp
print(f"marches avec p_(k+1) < 12 000 : {nmarches}, toutes en baisse ; la moins nette : ΔF = {float(pire[0]):.3e} en p = {pire[1]}")
print(f"lemme N1 contredit : {viol} fois sur {len(ps) - 2} marches (p < 10⁶)")
print(f"plus petit écart δ − (½ ln p + ¾) : {min_ecart[0]:.3f} en p = {min_ecart[1]} (δ = {min_ecart[2]:.3f}, seuil = {min_ecart[3]:.3f})")
# le seuil de Büthe : 0,05 √p ≥ ½ ln p + ¾ dès que p ≥ ?
p = 2
while 0.05 * math.sqrt(p) < 0.5 * math.log(p) + 0.75: p += 1
print("0,05·√p ≥ ½·ln p + ¾ pour tout p ≥", p)
