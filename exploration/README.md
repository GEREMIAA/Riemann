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

## Peut-on raisonner par récurrence ?

L'idée est tentante : si c'est vrai sur une partie, des « harmoniques » et une symétrie suffiraient-elles à le rendre vrai jusqu'à l'infini ? C'est exactement ainsi qu'on a démontré l'hypothèse pour les courbes. Pour ζ, la même idée bute sur trois obstacles, vérifiés ici par le calcul.

### Pour les courbes, ça marche

![Les 60 premières harmoniques de la courbe restent dans la bande ±2 ; un monde imaginaire décalé de 1 % ne se distingue du vrai qu'après m = 60](recurrence_courbe.png)

La courbe y² = x³ + x + 1 se compte sur les corps à 5, 25, 125… éléments : ce sont ses « harmoniques » m = 1, 2, 3… Elle y a 5ᵐ + 1 − (αᵐ + βᵐ) points : deux nombres seulement, α et β, pilotent une infinité d'harmoniques. En comptant les points un par un, on trouve 9, 27 et 108, exactement ce que prévoient α et β. La preuve tient en trois temps :

1. **Une borne pour toutes les harmoniques à la fois.** L'écart reste sous C·5^(m/2) pour tout m (Weil, 1948 ; méthode élémentaire de Stepanov et Bombieri, 1969–1973). Elle est démontrée par l'algèbre, pas vérifiée cas par cas.
2. **L'amplification.** Si |α| dépassait √5, même de 1 %, αᵐ finirait par dépasser n'importe quelle borne de ce type. Donc |α| ≤ √5.
3. **La symétrie α ↔ 5/α** (l'équation fonctionnelle) donne l'inverse, |α| ≥ √5. Donc |α| = √5 : les zéros sont sur la droite.

Même ici, vérifier une partie ne suffit pas : un monde imaginaire décalé de 1 % reste indiscernable du vrai jusqu'à m = 60 (3,6 contre 2). C'est la borne démontrée pour toutes les harmoniques d'un coup qui fait la preuve.

### Pour ζ, trois obstacles

**Pas d'harmoniques communes.** Chaque nombre premier a les siennes (p, p², p³…, le cristal de la section « Cristal ou quasi-cristal »), mais ζ en mélange une infinité, et ln 2, ln 3, ln 5… n'ont aucune note commune. Il n'y a pas de liste finie de « α », et les zéros n'ont pas de période. Pour la courbe, ils se répètent tous les 3,904 en hauteur.

**La symétrie ne suffit pas.**

![En haut, les 82 zéros de ζ sous la hauteur 205, tous sur la droite ; en bas, la fonction de Davenport–Heilbronn : 125 zéros sur la droite et 8 en dehors](symetrie_davenport.png)

La fonction de Davenport et Heilbronn, f(s) = 1 + τ/2ˢ − τ/3ˢ − 1/4ˢ + 1/6ˢ + … avec τ ≈ 0,284, a exactement la symétrie de ζ : l'équation Λ(s) = Λ(1 − s) est vérifiée ici à 10⁻¹³ près. Sous la hauteur 205, elle a 133 zéros : 125 sur la droite et 8 en dehors, par paires symétriques, dont 0,808517 + 85,699348 i. Ce sont ceux que Spira avait trouvés en 1994, et on sait qu'il y en a une infinité. Sa seule différence avec ζ : pas de produit d'Euler, puisque a(6) = 1 alors que a(2) × a(3) = −0,08. Une preuve doit donc utiliser la règle de multiplication des nombres premiers.

**« Vrai sur une partie » ne suffit pas.**

![L(x)/√x reste sous 0 jusqu'à 906 150 256, puis passe au-dessus ; M(x)/√x reste loin de ±1](vrai_puis_faux.png)

On a passé au crible tous les entiers jusqu'à un milliard :

- **Pólya (1919)** affirme L(x) ≤ 0 pour tout x ≥ 2. C'est vrai pour tous les n de 2 à 906 150 256. En n = 906 150 257 = 10 039 × 90 263, L vaut +1 : la conjecture est fausse (Tanaka, 1980). L est positif 305 426 fois, par moments, jusqu'à 906 488 079 (maximum 829), puis ne dépasse plus 0, au moins jusqu'au milliard ; plus loin, il repasse au-dessus de 0 une infinité de fois (Borwein, Ferguson et Mossinghoff, 2008). Un énoncé « pour tout » tombe avec un seul contre-exemple : « fausse » ne veut pas dire « fausse pour tous les nombres suivants ». Si Pólya avait eu raison, l'hypothèse de Riemann aurait été vraie.
- **Mertens (1897)** affirme |M(x)| < √x. Entre 10⁵ et 10⁹, |M(x)|/√x ne dépasse pas 0,47. C'est pourtant faux (Odlyzko et te Riele, 1985). Personne n'a jamais vu de contre-exemple : le premier se trouve quelque part avant e^(1,96·10¹⁹).
- **π(x) < li(x)** est vérifié jusqu'à 10¹⁹ (Büthe, 2018), et faux avant 1,3971·10³¹⁶.

**Vérifie toi-même.** La page [`polya.html`](https://geremiaa.github.io/Musique-Des-Premiers/exploration/polya.html) refait tout le calcul de Pólya dans le navigateur, sur ton propre appareil : une demi-minute environ sur un ordinateur, un peu plus sur un téléphone (sans GitHub Pages, télécharge [`polya.html`](polya.html) et ouvre-le dans ton navigateur). Elle utilise une autre méthode que les programmes Python du dossier [`calculs/`](calculs/), et retrouve les mêmes nombres.

### Ce qu'on peut en tirer

- **La récurrence de Weil.** Appelons P(x) l'énoncé « l'énergie de Weil est positive pour toutes les ondes vivant entre 1/√x et √x ». L'hypothèse revient à « P(x) pour tout x ». Le premier cas, où aucun nombre premier n'entre dans la fenêtre, est démontré (Connes et Consani, 2020) ; on l'a vérifié numériquement jusqu'à x = 31, avec 60 ondes de base. Il manque le pas de récurrence : montrer qu'un nouveau nombre premier ne casse pas la positivité. Personne ne sait le faire, et la marge fond, de 5·10⁻⁴ à 2·10⁻⁹⁹ (voir le tableau plus haut).
- **Une récurrence « fini + infini » existe déjà.** Pour la constante de de Bruijn–Newman Λ, Polymath15 a montré Λ ≤ 0,22 en 2019, avec un calcul fini, un argument pour l'infini et une « barrière » entre les deux ; le record est 0,2 (Platt et Trudgian, 2021). L'hypothèse revient à Λ = 0, mais la méthode ne peut pas atteindre 0 : elle a besoin de la marge que donne la chaleur quand t > 0.
- **Les harmoniques qui manquent.** C'est le programme d'Alain Connes. Une sorte de Frobenius continu existe (les dilatations, où chaque nombre premier apparaît comme une boucle de longueur ln p), la symétrie aussi ; il manque la borne pour toutes les harmoniques, c'est-à-dire une positivité.
- **Un filtre contre les fausses preuves.** Si un raisonnement marcherait aussi pour Davenport–Heilbronn, ou s'il repose sur « vrai jusqu'à N », il est faux.

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
2. **Le contre-essai de Weil** : les zéros hors de la droite de la fonction de Davenport–Heilbronn sont maintenant calculés (section « Peut-on raisonner par récurrence ? ») ; reste à lui faire passer le test de Weil et à regarder son « énergie » devenir négative.
3. **Là où l'hypothèse a failli tomber** : zoomer sur la paire de Lehmer, à la hauteur 7005.
4. **Lire** : *La Symphonie des nombres premiers* de Marcus du Sautoy, et *Prime Numbers and the Riemann Hypothesis* de Barry Mazur et William Stein (en anglais).

## Sources

- *Quanta Magazine*, 19 octobre 2026 : [l'hypothèse de quasi-Riemann](https://quantamagazine.org/ai-proved-the-quasi-riemann-hypothesis-what-happens-now-20261019)
- L. Alpöge, R. Furman : [arXiv 2608.13637](https://arxiv.org/pdf/2608.13637) ; Y. Lamzouri : [arXiv 2609.02882](https://arxiv.org/pdf/2609.02882)
- A. Connes, C. Consani : [arXiv 2106.01715](https://arxiv.org/abs/2106.01715) ; A. Connes, C. Consani, H. Moscovici : [arXiv 2511.22755](https://arxiv.org/abs/2511.22755)
- A. Groskin : [arXiv 2605.20224](https://arxiv.org/abs/2605.20224)
- D. Platt, T. Trudgian : [arXiv 2004.09765](https://arxiv.org/abs/2004.09765) ; L. Guth, J. Maynard : [Annals of Mathematics](https://annals.math.princeton.edu/2026/203-2/p06)
- F. Dyson, *Birds and Frogs* (2009) : [les zéros comme quasi-cristal](https://empslocal.ex.ac.uk/people/staff/mrwatkin/zeta/dyson-quasicrystal.htm)
- [Paire de Lehmer](https://en.wikipedia.org/wiki/Lehmer_pair) ; [fonction de Davenport–Heilbronn](https://arxiv.org/pdf/1602.06328) ; E. Saias, A. Weingartner, une infinité de zéros hors de la droite : [arXiv 0807.0783](https://arxiv.org/abs/0807.0783)
- R. Schoof, [la preuve de Stepanov et Bombieri pour les courbes](https://www.mat.uniroma2.it/~schoof/RHcurves.pdf)
- [Conjecture de Pólya](https://en.wikipedia.org/wiki/P%C3%B3lya_conjecture) ; S. Kim, P. Q. Nguyen, conjecture de Mertens : [arXiv 2502.21021](https://arxiv.org/pdf/2502.21021) ; P. Borwein, R. Ferguson, M. Mossinghoff, changements de signe de L(n) : [Mathematics of Computation, 2008](https://www.ams.org/mcom/2008-77-263/S0025-5718-08-02036-X/)
- J. Büthe, π(x) < li(x) jusqu'à 10¹⁹ : [Mathematics of Computation, 2018](https://www.ams.org/journals/mcom/2018-87-312/S0025-5718-2017-03264-6) ; D. Platt, T. Trudgian, premier changement de signe : [arXiv 1407.1914](https://arxiv.org/pdf/1407.1914)
- A. Connes, C. Consani, positivité de Weil à la place archimédienne : [arXiv 2006.13771](https://arxiv.org/abs/2006.13771) ; Polymath15, Λ ≤ 0,22 : [arXiv 1904.12438](https://arxiv.org/abs/1904.12438)

Réalisé avec l'aide de Claude (Anthropic).
