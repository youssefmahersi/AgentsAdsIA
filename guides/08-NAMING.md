# 08 · Naming convention (campagnes, ensembles, pubs, fichiers)

Une seule façon de nommer toutes tes pubs. En lisant un nom, on sait ce qui est testé, pour qui et sous quelle forme, sans ouvrir la pub. Les agents l'appliquent à chaque fichier livré et à chaque pub créée sur Meta.

## Le nom d'une pub : 7 morceaux, toujours dans le même ordre
```
B0124_01_BackPain_OfficeWorkers_MOFU_Static_Headline
```
| # | Morceau | Ce qu'il dit | Exemples |
|---|---|---|---|
| 1 | **Lot** | Le numéro du test : B suivi de 4 chiffres. Un lot = une idée testée. | B0124 |
| 2 | **N° de pub** | La place de la pub dans le lot, sur 2 chiffres | 01, 02, 03 |
| 3 | **Sous-angle** | L'argument précis de la pub, à l'intérieur d'un angle | BackPain, NoBitterTaste |
| 4 | **Avatar** | La personne à qui la pub parle | OfficeWorkers, Moms40 |
| 5 | **Stage** | Où en est le prospect | TOFU, MOFU, BOFU |
| 6 | **Format** | La famille de la créa | Static, UGC, Native, Motion, IA |
| 7 | **Concept** | Le type précis de créa dans ce format | Headline, Testimonial, Podcast, TierList, StreetInterview |

Pour une vidéo avec plusieurs hooks, on ajoute le hook : `…_UGC_Testimonial_H1`, `_H2`, `_H3`. Chaque hook est une pub séparée.

## Les 3 étages sur Meta
| Étage | Nom | Exemple |
|---|---|---|
| **Campagne** | Pays_Budget_Marque_Produit_Rôle_Date | `US_ABO_MARQUE_SeatCushion_Testing_13-10-2026` |
| **Ensemble** | Le lot et ce qu'il teste | `B0124_BackPain_OfficeWorkers_MOFU_Static_Headline` |
| **Pub** | Le nom complet, avec le numéro | `B0124_01_BackPain_OfficeWorkers_MOFU_Static_Headline` |

- **Budget** : ABO (budget par ensemble) ou CBO (budget par campagne).
- **Rôle** : Testing (tests) ou Scaling (gagnantes).
- **Une pub gagnante garde exactement son nom** quand elle passe en Scaling. On ne renomme jamais une pub.

## Le nom des fichiers livrés
Le monteur, humain ou agent, recopie le nom de la pub et ajoute seulement :
- **la taille** : `_1x1`, `_4x5`, `_9x16` ;
- **la version** en cas de correction : `_v2`.

```
livraisons/2026-11-02/<produit>/TOFU/B0124_01_BackPain_OfficeWorkers_TOFU_UGC_Testimonial_H1_9x16.mp4
livraisons/2026-11-02/<produit>/MOFU/B0125_01_NoBitterTaste_Moms40_MOFU_Static_Headline_1x1_v2.png
```

## Les 4 règles d'écriture
1. Un tiret bas `_` entre les morceaux. Pas d'espace, pas d'accent.
2. Les codes s'écrivent exactement comme dans ta liste, majuscules comprises.
3. L'ordre des morceaux ne change jamais.
4. Un mot qui n'est pas dans ta liste n'existe pas : on l'ajoute d'abord à la liste.

## Ta liste (à créer une fois par marque)
Crée `produits/<marque>/NAMING.md` avec tes codes et une phrase de définition pour chacun :
```
ANGLES / SOUS-ANGLES
- Pain / BackPain : le mal de dos après une journée assise
AVATARS
- OfficeWorkers : salariés de bureau 30-50 ans, 8 h assis par jour
CONCEPTS (par format)
- Static : Headline, BeforeAfter, UsVsThem, Testimonial, Listicle
- UGC : Testimonial, Podcast, StreetInterview, TierList, Unboxing
```
Avant chaque lot, dis à l'agent : « nouveau lot B0125, sous-angle X, avatar Y, stage MOFU ». Il nommera tout seul.

## Lire les résultats
Dans le Gestionnaire de publicités, filtre sur « le nom contient `_BackPain_` » (ou `_TOFU_`, ou `_UGC_`) pour comparer les angles, les avatars, les stages et les formats entre eux.
