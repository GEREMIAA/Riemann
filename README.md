# Où en est l'hypothèse de Riemann ? (novembre 2026)

Ce dossier complète la page *La musique des nombres premiers*. Il résume où en est la recherche, explique pourquoi l'hypothèse résiste, et propose une expérience à refaire soi-même dans Colab.

> **À lire d'abord.** Rien ici ne démontre l'hypothèse de Riemann. Elle reste ouverte.

[![Ouvrir dans Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/GEREMIAA/Musique-Des-Premiers/blob/main/exploration/weil_haute_precision.ipynb) Le carnet `weil_haute_precision.ipynb` refait l'expérience en haute précision, en moins d'une minute.

## Ce qui a bougé en 2026

- **Août, Claude (Anthropic).** Une version de recherche de Claude a trouvé et rédigé une preuve que plus des deux tiers des zéros (67,25 %) sont simples et sur la droite critique. Le record précédent était 5/12, soit 41,7 %. Levent Alpöge et Ralph Furman ont vérifié la preuve, puis Youness Lamzouri (Université de Lorraine) l'a redémontrée autrement, plus simplement.
- **Octobre, OpenAI.** OpenAI a annoncé une preuve de l'« hypothèse de quasi-Riemann » : tous les zéros auraient une partie réelle comprise entre 1/12 et 11/12, au lieu de 0 et 1. Une version plus forte, entre 1/8 et 7/8, a été vérifiée par ordinateur avec le logiciel Lean. Selon *Quanta Magazine*, les spécialistes pensent que c'est juste, mais ils n'ont pas fini de vérifier.

Ni l'une ni l'autre n'est l'hypothèse. Même 100 % des zéros « en proportion » laisserait la place à une infinité de zéros hors de la droite, s'ils sont assez rares. Et la bande doit encore se réduire à la seule droite ½.

## Dans ce monde-là, l'hypothèse est démontrée

![Pour la courbe y² = x³ + x + 1, la valeur a_p/(2√p) reste entre −1 et 1 pour les 1 958 premiers p jusqu'à 17 000](monde_demontre.png)

Pour la courbe y² = x³ + x + 1, on compte ses points modulo chaque nombre premier p, ce qui donne un nombre a_p. Dans ce monde, l'hypothèse de Riemann dit |a_p| ≤ 2√p : les deux zéros de la fonction zêta de la courbe sont pile sur la droite Re s = ½. Sur les 1 958 premiers jusqu'à 17 000, aucun point ne sort de la bande ; le plus proche du bord est p = 14 051, à 0,9997.

Le calcul ne prouve rien : c'est un théorème qui le garantit pour tous les p (Hasse dans les années 1930, Weil pour toutes les courbes en 1948, Deligne en 1974). La preuve repose sur deux ingrédients :
- le « Frobenius », une symétrie qui élève chaque coordonnée à la puissance p ;
- une inégalité de positivité sur la surface « courbe × courbe ».

Pour les nombres entiers, personne ne sait ce qui joue le rôle de la courbe, de la surface ou du Frobenius. C'est ce que cherche le programme d'Alain Connes.

## Les nombres premiers « connaissent » les zéros

On prend une onde qui ne vit qu'entre 1/√x et √x. Son *énergie de Weil* se calcule de deux façons, qui donnent le même nombre :
- avec les seuls nombres premiers inférieurs à x (et leurs puissances), plus quelques constantes comme π ;
- ou comme la somme, sur tous les zéros, du carré du « son » de l'onde à chaque fréquence γ.

Si l'hypothèse est vraie, c'est une somme de carrés, donc jamais négative. Weil a montré la réciproque : si l'énergie est positive pour toutes les ondes, l'hypothèse est vraie.

On cherche alors l'onde d'énergie la plus petite, calculée **sans aucun zéro**. Pour être la plus discrète possible, elle doit se taire à chaque zéro de ζ, et ses creux tombent dessus.

![La meilleure onde construite avec 2, 3 et 4 : ses creux tombent sur les zéros de ζ](weil_zeros.png)

En haute précision (150 chiffres, 60 ondes de base), on va beaucoup plus loin :

![Décimales justes retrouvées et plus petite énergie, selon les nombres premiers utilisés](haute_precision.png)

| x | Premiers et puissances utilisés | Plus petite énergie | Décimales justes de γ₁ | de γ₁₀ |
|---|---|---|---|---|
| 2 | aucun | 5·10⁻⁴ | 0 | 0 |
| 3 | 2 | 3·10⁻⁸ | 4 | 0 |
| 5 | 2, 3, 4 | 8·10⁻¹⁸ | 13 | 1 |
| 7 | 2, 3, 4, 5 | 8·10⁻²⁸ | 23 | 8 |
| 11 | jusqu'à 9 | 2·10⁻⁴⁸ | 44 | 26 |
| 13 | jusqu'à 11 | 9·10⁻⁵⁹ | 54 | 36 |
| 17 | jusqu'à 16 | 1·10⁻⁷³ | 69 | 49 |
| 19 | jusqu'à 17 | 3·10⁻⁷⁹ | 74 | 54 |
| 23 | jusqu'à 19 | 8·10⁻⁸⁸ | 83 | 62 |
| 29 | jusqu'à 27 | 5·10⁻⁹⁷ | 92 | 70 |
| 31 | jusqu'à 29 | 2·10⁻⁹⁹ | 94 | 72 |

À chaque fois, la matrice de l'énergie est définie positive (factorisation de Cholesky) : la positivité de Weil tient pour ces ondes. Avec les nombres premiers jusqu'à 29, le premier zéro sort avec 94 décimales justes, γ₁ = 14,134725141734693790457251983562470270784257115699… Pour x = 11, notre plus petite énergie est du même ordre que celle mesurée par Connes et Consani (2,4·10⁻⁴⁸).

Ce n'est pas une découverte : le phénomène a été mis au jour par Alain Connes et Caterina Consani en 2021, et nous le refaisons en petit.

## Pourquoi on ne peut pas aller plus loin

1. **L'infini.** Le critère de Weil exige la positivité pour des ondes aussi longues qu'on veut, donc pour x aussi grand qu'on veut. Or la marge fond à toute vitesse : 2·10⁻⁹⁹ dès x = 31, et environ 10⁻⁵³⁵ vers x = 100 selon l'estimation de Groskin. Aucun calcul n'atteint l'infini : il faut une *raison* pour laquelle c'est positif.
2. **Le cercle vicieux.** Dans l'énergie, chaque nombre premier n pèse 1/√n. C'est exactement l'échelle √x où se jouent les irrégularités des premiers, celle que l'hypothèse contrôle. Pour démontrer la positivité, il faudrait donc déjà savoir ce que l'hypothèse affirme.
3. **La symétrie ne suffit pas.** Davenport et Heilbronn ont construit une fonction qui a la même symétrie miroir que ζ, mais des zéros hors de la droite. Une preuve doit donc utiliser ce qui rend ζ unique : son produit d'Euler, c'est-à-dire les nombres premiers comme briques de base. Personne ne sait transformer ce produit en positivité.

S'y ajoute un piège : il n'y a aucune marge. Vers la hauteur 7005, deux zéros consécutifs ne sont séparés que de 0,038 (la « paire de Lehmer », 7005,06266… et 7005,10056…). Rodgers et Tao ont montré que si l'hypothèse est vraie, elle l'est de justesse. Les méthodes par approximation, qui ont besoin d'un peu de jeu, n'ont donc aucune chance : il faut une raison exacte.

## Cristal ou quasi-cristal

![Un seul nombre premier donne une onde périodique ; une courbe modulo 5 a des zéros rangés en cristal ; les zéros de ζ forment un quasi-cristal](cristal_quasicristal.png)

- **A. Un seul nombre premier, c'est un cristal.** Le long de la droite critique, le facteur du seul nombre 2 se répète avec une période parfaite, 2π/ln 2 ≈ 9,06. Il oscille entre 2 − √2 et 2 + √2, et le rapport entre les deux vaut exactement (1 + √2)².
- **B et C. Dans le monde où l'hypothèse est démontrée, les zéros forment un cristal.** Pour la courbe modulo 5, un motif de deux zéros se répète tous les 2π/ln 5 ≈ 3,90. Sa « diffraction » donne des taches régulières aux multiples de ln 5, comme un réseau cristallin. La hauteur de chaque tache est fixée par le nombre de points de la courbe dans les corps à 5, 25 et 125 éléments.
- **D. Les zéros de ζ forment un quasi-cristal.** Ils ne se répètent jamais, mais leur diffraction est faite de taches nettes : une en ln p pour chaque nombre premier p, de hauteur ln p, et d'autres pour ses puissances. C'est exactement la définition d'un quasi-cristal que Freeman Dyson a proposée en 2009 : ordonné sans être périodique, comme les cristaux de Shechtman (prix Nobel de chimie 2011).

Ce que ça éclaire : pour une courbe donnée, tout se répète, donc vérifier une seule « maille » de quelques zéros suffit. Le tour de force de Weil a été de le démontrer pour toutes les courbes à la fois. Pour ζ, les fréquences ln 2, ln 3, ln 5… sont incommensurables : il n'y a pas de maille à vérifier. C'est le mur de l'infini, vu par un cristallographe.

Dyson proposait justement de classer tous les quasi-cristaux à une dimension, en espérant y retrouver les zéros de ζ, ce qui démontrerait l'hypothèse. Il jugeait lui-même ce programme très difficile. Ces « quasi-cristaux de Fourier » sont aujourd'hui un sujet de recherche actif. Le carnet refait cette figure (bonus 2).

## π, le nombre d'or et 1 + √2

![π sort du produit sur tous les premiers ; le nombre d'or est une somme de Gauss ; les sommes de Gauss restent à l'échelle √p](pi_or_argent.png)

- **π sort de tous les nombres premiers à la fois.** Le produit de (1 − 1/p²) sur tous les premiers vaut exactement 6/π² ≈ 0,6079. C'est aussi la probabilité que deux entiers pris au hasard n'aient aucun diviseur commun ; jusqu'à un million, on trouve 0,607927 par les deux calculs. π est aussi dans la symétrie miroir de ζ, où il joue le rôle d'un « nombre premier à l'infini ». Dans l'expérience de Weil, avec x = 2, ce premier à l'infini agit seul et donne déjà γ₁ à 0,2 près. Enfin, les zéros se comptent en demi-tours d'une phase qui tourne.
- **Le nombre d'or et 1 + √2 sont des nombres de polygones.** φ = 2 cos(π/5) vient du pentagone, 1 + √2 = 1/tan(π/8) de l'octogone, 2 + √3 = 1/tan(π/12) du dodécagone. Ils apparaissent dans ζ par les facteurs des premiers 5, 2 et 3 : sur la droite critique, le rapport entre leurs valeurs extrêmes vaut φ², (1 + √2)² et 2 + √3.
- **Le lien le plus profond : √5 est une « somme de Gauss ».** En additionnant les sommets du pentagone dans l'ordre a² modulo 5, on passe par φ à mi-chemin et on arrive pile à √5. Pour chaque nombre premier p, ces sommes ont une taille exactement √p (Gauss ; vérifié ici pour les 429 premiers impairs sous 3 000), et les sommes cubiques restent sous 2√p (Weil). C'est l'hypothèse de Riemann dans le monde des nombres modulo p, déjà démontrée.

Pour ζ elle-même, on ne connaît aucun lien entre ces nombres et la position des zéros : π vient des rotations et du premier à l'infini, et le nombre d'or et 1 + √2 apparaissent parce que √5 et √2 y sont. Le carnet refait ces calculs (bonus 3).

## Le photon : aucune onde ne vieillit

![Sur la droite, l'onde d'un zéro divisée par √x tourne sur un cercle ; hors de la droite, elle part en spirale](photon_ondes.png)

Pour un photon, le temps ne s'écoule pas : son « temps propre » reste nul. On retrouve une image proche avec les zéros. Divisée par √x, la croissance commune à toutes les ondes, l'onde d'un zéro situé sur la droite critique ne grandit ni ne s'éteint : elle ne fait que tourner, sur un cercle. Si un zéro quittait la droite, il viendrait avec un jumeau symétrique : l'onde de l'un enflerait comme x^(σ − ½), celle de l'autre s'éteindrait.

L'hypothèse de Riemann revient donc à dire qu'aucune onde ne vieillit. C'est le langage de l'idée de Hilbert et Pólya. En physique quantique, un état d'énergie réelle évolue par pure rotation et reste stable, alors qu'un état d'énergie complexe se désintègre, comme une particule instable. Trouver un système dont les zéros seraient les énergies, toutes réelles, démontrerait l'hypothèse.

Berry et Keating ont remarqué que le « temps » de ces ondes, ln x, est celui des changements d'échelle, engendrés par le hamiltonien classique H = xp. Les opérateurs de Connes, Consani et Moscovici sont construits pour que leurs notes ne vieillissent pas. Personne n'a encore trouvé le bon. Le carnet refait cette figure (bonus 4).

## Ce qu'il faudrait ajouter

- **Une géométrie** qui écrive l'énergie comme une somme de carrés, comme la surface « courbe × courbe » le fait pour les courbes modulo p. C'est le rêve du « corps à un élément » et le programme d'Alain Connes.
- **Un instrument** : un opérateur dont les fréquences propres seraient exactement les γ, ce qui les mettrait forcément sur la droite (idée de Hilbert et Pólya). Connes, Consani et Moscovici (2025) en construisent des approximations à partir des seuls nombres premiers ≤ x. Avec les premiers jusqu'à 13, ils retrouvent déjà le premier zéro à 10⁻⁵⁵ près. Ils écrivent qu'une preuve rigoureuse que leur construction converge établirait l'hypothèse.
- **Une idée analytique nouvelle.** 2026 rappelle que les murs tombent parfois : si la « quasi-Riemann » est confirmée, une barrière vieille de plus d'un siècle est tombée.

## La carte des pistes

| Piste | L'idée | Où on en est | Ce qui bloque |
|---|---|---|---|
| Compter les zéros sur la droite | Une part toujours plus grande des notes est « accordée » | Plus des 2/3 (2026) | Une proportion, même 100 %, ne suffit pas |
| Rétrécir la bande | Interdire aux zéros de trop s'éloigner | Bande 1/12–11/12 annoncée (2026) ; Guth et Maynard (2024) : les zéros hors de la droite, s'il y en a, sont plus rares qu'on ne savait le montrer | Réduire la bande à la droite elle-même |
| Vérifier par calcul | Contrôler les notes une à une | Tous les zéros jusqu'à la hauteur 3·10¹² sont sur la droite, soit plus de 10 000 milliards | Il en restera toujours une infinité |
| La « chaleur » (de Bruijn–Newman) | On fait diffuser la fonction comme de la chaleur ; ses zéros deviennent réels à partir d'un instant Λ | 0 ≤ Λ ≤ 0,2 ; l'hypothèse revient à Λ = 0 | Faire descendre 0,2 jusqu'à 0 |
| La positivité (Weil) | Une énergie toujours positive | Équivalent exact ; vérifiée ici jusqu'à x = 31 | Il faut toutes les ondes, x → ∞ |
| L'instrument caché (Hilbert–Pólya, Connes) | Les zéros comme fréquences propres | Écarts entre zéros semblables aux niveaux d'énergie des noyaux lourds (Montgomery, Odlyzko) | Personne n'a trouvé l'opérateur |
| Les quasi-cristaux (Dyson) | Des zéros ordonnés sans être périodiques, dont la « diffraction » tombe sur les ln p | Programme proposé en 2009 ; « quasi-cristaux de Fourier » étudiés activement | Classer tous les quasi-cristaux à une dimension |
| Les courbes modulo p (Hasse, Weil, Deligne) | Le même énoncé dans un autre monde | **Démontré** | Aucun équivalent connu pour les entiers |

## Projets pour continuer

1. **Pousser Weil plus loin** avec le carnet : augmenter la précision, le nombre d'ondes et x, essayer d'autres familles d'ondes.
2. **Voir pourquoi la symétrie ne suffit pas** : calculer la fonction de Davenport–Heilbronn, traquer ses zéros hors de la droite, et regarder son « énergie » devenir négative.
3. **Là où l'hypothèse a failli tomber** : zoomer sur la paire de Lehmer, à la hauteur 7005.
4. **Lire** : *La Symphonie des nombres premiers* de Marcus du Sautoy, et *Prime Numbers and the Riemann Hypothesis* de Barry Mazur et William Stein (en anglais).

## Sources

- *Quanta Magazine*, 19 octobre 2026 : [l'hypothèse de quasi-Riemann](https://quantamagazine.org/ai-proved-the-quasi-riemann-hypothesis-what-happens-now-20261019)
- L. Alpöge, R. Furman : [arXiv 2608.13637](https://arxiv.org/pdf/2608.13637) ; Y. Lamzouri : [arXiv 2609.02882](https://arxiv.org/pdf/2609.02882)
- A. Connes, C. Consani : [arXiv 2106.01715](https://arxiv.org/abs/2106.01715) ; A. Connes, C. Consani, H. Moscovici : [arXiv 2511.22755](https://arxiv.org/abs/2511.22755)
- A. Groskin : [arXiv 2605.20224](https://arxiv.org/abs/2605.20224)
- D. Platt, T. Trudgian : [arXiv 2004.09765](https://arxiv.org/abs/2004.09765) ; L. Guth, J. Maynard : [Annals of Mathematics](https://annals.math.princeton.edu/2026/203-2/p06)
- F. Dyson, *Birds and Frogs* (2009) : [les zéros comme quasi-cristal](https://empslocal.ex.ac.uk/people/staff/mrwatkin/zeta/dyson-quasicrystal.htm)
- [Paire de Lehmer](https://en.wikipedia.org/wiki/Lehmer_pair) ; [fonction de Davenport–Heilbronn](https://arxiv.org/pdf/1602.06328)

Réalisé avec l'aide de Claude (Anthropic).
