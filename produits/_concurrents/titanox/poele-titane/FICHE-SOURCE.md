# TITANOX (titanoxfrance.com) — Poêle 100% Titane Pur — fiche source

> Fiche remplie par karim. Elle décrit **ce que fait le site source, tel quel**. Ce n'est pas `PRODUIT.md`.
> Provenance : `[PAGE]` page rendue · `[JSON]` `.json` Shopify · `[IMG]` texte lu dans une image de la galerie ou de la page ·
> `[PUB]` bibliothèque publicitaire Meta · `[AVIS]` avis · `[LÉGAL]` pages légales du site · `[DÉDUIT]` déduit par karim · `[À VÉRIFIER]` non confirmé.
> Repères : ✅ OK · ⚠️ à prouver ou à nuancer · ❌ à éviter (règle en cause indiquée).
> **Textes recopiés mot pour mot, sans réécriture. On souligne seulement.**

---

## 0. La source

- **Type de source** : **concurrent** (confirmé par l'utilisateur le 2026-11-22). Les textes, images et claims ci-dessous servent à l'analyse ; ils ne se reprennent pas dans nos créas.
- **URL de la page produit** : https://titanoxfrance.com/products/titanox-poele-en-titane-pur-sans-pfas
- **Date du relevé** : 21-22/11/2026 (lecture seule : curl sur les JSON publics + Chrome DevTools, contexte isolé ; aucun ajout au panier, aucun formulaire).
- **Marché** : France (+ Belgique, Suisse cités dans les avis), langue fr, devise EUR `[JSON]` `[PAGE]`.
- **Boutique** : Shopify, shop id 99259810138 (`4db5n1-9p.myshopify.com`) `[PAGE]`. Même gabarit que l'aiguiseur (voir `../ANALYSE.md`).
- **Fichiers bruts** (ce dossier) :
  - `titanox-poele-en-titane-pur-sans-pfas.json`, `products.json` (catalogue, 14 fiches)
  - `page.html` (HTML servi) et `page-texte.txt` (texte extrait, base de la section 3)
  - `images/01.jpg` à `images/11.png` : les 11 images de la galerie en HD ; `images/page/` : visuels de sections (logos médias, bannière « fondateur », bloc « Dernière chance »)
  - `legal/` : mentions légales, politique de retour, CGV, FAQ (HTML)
  - `pubs/meta-106977935010411-actives.json` (327 cartes de pubs relevées, texte complet), `pubs/meta-106977935010411-texte-brut.json`, `pubs/bibliotheque-106977935010411.png`
- **Captures** : `390-hero.png`, `390-pleine-page.jpeg` (13 606 px), `1440-hero-buybox.png`, `1440-pleine-page.jpeg`. Aucun défilement horizontal (scrollWidth = 390).

## 1. Le produit

- **Nom affiché** : « Poêle 100% Titane Pur — TITANOX® » `[JSON]`
- **Ce que c'est, en une phrase** : une poêle martelée « sans revêtement » vendue comme 100 % titane, en 26 / 28 / 30 cm, avec manche amovible, positionnée « cuisine saine sans PFAS ». `[PAGE]` `[IMG]`
- **Niche** : ustensiles de cuisson « non toxiques » / anti-PFAS (cuisine saine, famille). `[DÉDUIT]`
- **Niveau de conscience du marché** : problème conscient → solution consciente. Les pubs éduquent sur le danger des revêtements (PFAS) avant de vendre ; le titane est encore peu connu. `[DÉDUIT]` `[PUB]`

| Caractéristique | Valeur exacte | Provenance |
|---|---|---|
| Matière / composition | **Contradiction.** Titre, puces, pubs : « 100 % titane pur ». Infographie de la galerie (`images/08.png`) : « Surface Titane Pur » + « Noyau Aluminium » + « Base acier Inoxydable ». FAQ : « La base inox ferritique assure une compatibilité totale. » Composition réelle (alliage, grade du titane, épaisseur de chaque couche, titane massif ou couche) : **[À VÉRIFIER]** | `[PAGE]` `[IMG]` `[PUB]` |
| Surface | « Relief martelé », « TITANOX RELIEF 2.0™ », « *Texture titane martelée brevetée TITANOX » | `[PAGE]` `[IMG]` |
| Coloris / variantes | Option « Choisissez votre Taille » : 26 cm (SKU P-26cm), 28 cm (P-28cm), 30 cm (P-30cm). Un seul coloris (acier brossé / martelé) | `[JSON]` |
| Dimensions / poids | Diamètres 26 / 28 / 30 cm. Poids : `grams: 0` dans le JSON → **[À VÉRIFIER]**. Hauteur, épaisseur, diamètre du fond : **[À VÉRIFIER]** | `[JSON]` |
| Capacité affichée | 26 cm « 3 œufs · 1-2 portions » ; 28 cm « 5 œufs · 2-3 portions » (« LE PLUS CHOISI ») ; 30 cm « 8 œufs · 3-4 portions ». FAQ : 28 cm « 2 à 4 personnes » | `[PAGE]` |
| Manche | « MANCHE TITANOX AMOVIBLE & PRATIQUE », « Montage et démontage en 15 secondes », vis visibles sur l'image | `[IMG]` |
| Compatibilité | « induction, gaz, électrique, vitrocéramique » ; four « jusqu'à 260°C » (page) **mais** « jusqu'à 548°C » (page FAQ du site) ; lave-vaisselle | `[PAGE]` `[LÉGAL]` |
| Contenu du colis | Non indiqué. Le bloc « Dernière chance » montre une boîte noire TITANOX + carte. Couvercle non inclus (vendu à part, 24,99 €) | `[IMG]` `[JSON]` ; contenu exact **[À VÉRIFIER]** |
| Fabrication / origine | Non indiquée. Drapeau français sur le badge « Élu poêle santé 2026 » et « POÊLE SANTÉ N°1 EN FRANCE » : n'indique pas une origine. Fabricant, pays de fabrication, responsable UE : **[À VÉRIFIER]** | `[IMG]` |
| Éditeur | « Titanox France SAS », 9 rue des Colonnes, 75002 Paris. Aucun SIREN / RCS / capital / directeur de publication affiché | `[LÉGAL]` |
| Date de mise en ligne | Fiche créée le 04/04/2026 (2 doublons : `poele-100-titane-pur-titanox-offre` 24/05/2026, `titanox-poele-en-titane-pur-sans-pfas-2` 09/09/2026) | `[JSON]` |

## 2. Prix et offre

| Élément | Valeur exacte | Provenance | Réglementation |
|---|---|---|---|
| Prix de vente | 26 cm 59,99 € · 28 cm 64,99 € · 30 cm 69,99 € | `[JSON]` | ✅ (,99 conforme à nos règles) |
| Prix barré | 120,00 € · 130,00 € · 140,00 € (`compare_at_price`), affiché « -50% » | `[JSON]` `[PAGE]` | ❌ Omnibus (art. 6 bis dir. 98/6, L112-1-1 C. conso.) : le prix de référence doit être le prix le plus bas pratiqué dans les 30 jours précédents. Le prix barré existe depuis la création (04/04/2026) ; aucune trace d'une vente à 120 €. Prix ronds (non conformes à notre règle ,95/,99) |
| Bundles | « 1x Poêle Titanox® » -50% 59,99 € barré 120,00 € « Économisez 60,01€ » · « Set 2 Poêles Titanox® » « -60% • MEILLEURE VENTE » 99,98 € barré 240,00 € « Économisez 140,02€ » · « Set 3 Poêles Titanox® » « -70% • MEILLEURE OFFRE » 134,97 € barré 360,00 € « Économisez 225,03€ ». Taille choisie par poêle | `[PAGE]` | ❌ Pourcentages faux : 99,98/240 = **-58,3 %** (affiché -60%) ; 134,97/360 = **-62,5 %** (affiché -70%). Pratique trompeuse sur le prix (dir. 2005/29 art. 6 §1 d). Totaux en ,98 / ,97 (hors règle maison ,95/,99) |
| Bandeau promo | « OFFRE DE SAISON : JUSQU'À -70% » (barre d'annonce + au-dessus des paliers) ; bannière « ANNIVERSAIRE : LE FONDATEUR DE TITANOX CÉLÈBRE L'ÉVÉNEMENT AVEC VOUS ! -50 % SUR TOUT LE SITE. » | `[PAGE]` `[IMG]` | ❌ « -70% » non atteint ; « -50 % sur tout le site » faux (accessoires sans remise) ; deux promos contradictoires sur la même page |
| Remise, roue, pop-up | Pop-up Klaviyo « UN TOUR, UNE RECOMPENSE GARANTIE » (roue : Surprise / -10% / -15%), couvre le premier écran mobile | `[PAGE]` | ⚠️ Conditions du jeu non affichées |
| Cadeau panier | « LIVRAISON PREMIUM OFFERTE : » + minuteur panier « 05:00 » ; bloc « DERNIÈRE CHANCE — Livraison Premium OFFERTE d'une valeur de 20€ — Express · Protégée · Garantie » ; produit `livraison-premium-offerte` 0,00 € barré 20,00 € | `[PAGE]` `[IMG]` `[JSON]` | ❌ La livraison est déjà « gratuite à domicile » partout : valeur de 20 € non réelle si aucun client ne la paie (dir. 2005/29 annexe I pt 20, « gratuit ») ; « Dernière chance » + minuteur 5 min = fausse urgence |
| Garantie | Page : « Garantie à vie, sans conditions — au moindre défaut, nous vous renvoyons un produit neuf gratuitement » ; « Anti-adhérence garantie 25 ans » ; « 30 JOURS D'ESSAI SATISFAIT OU REMBOURSÉ ». Politique de retour : « garantie de 30 jours… couvre exclusivement » les défauts, la casse, la non-conformité | `[PAGE]` `[LÉGAL]` | ❌ Trois garanties contradictoires (à vie / 25 ans / 30 jours). Garantie commerciale sans écrit de conditions (L217-21 C. conso.). Garantie légale de conformité de 2 ans (dir. 2019/771) jamais mentionnée |
| Livraison | « Commande expédiée sous 24h — livraison gratuite à domicile » (page) ; « 3 à 5 jours pour l'Europe et 5 à7 jours pour l'internationale » (FAQ page) ; « expédiée sous 24/48h et livrée en 3 à 5 jours ouvrés » (page FAQ) | `[PAGE]` `[LÉGAL]` | ⚠️ Délais incohérents entre les pages |
| Retours | Page : « 30 jours pour l'essayer chez vous — si elle ne vous convainc pas, vous êtes remboursé intégralement ». Politique : poêles utilisées « ne peuvent être ni retournées, ni échangées, ni remboursées » (L221-28 invoqué), articles en promotion « ne sont pas éligibles à un remboursement », annulation avec « frais de gestion forfaitaires de 10 € » | `[PAGE]` `[LÉGAL]` | ❌ Dir. 2011/83 (L221-18) : 14 jours de rétractation, y compris sur les produits en promo ; l'exception hygiène (L221-28 5°) vise les biens scellés descellés, pas une poêle (interprétation très contestable) ; frais d'annulation non prévus par la loi. « Satisfait ou remboursé 30 jours » contredit par la politique, alors que tout le catalogue poêle est « en promo » |
| Urgence affichée | « Plus que 4 poêles en stock. » (×2) ; « Aujourd'hui, il ne reste que 4 poêles à ce prix » ; badge « STOCK FAIBLE ! » ; compte à rebours « 00 : 00 : 25 : 00 » | `[PAGE]` | ❌ Code lu : le compte à rebours dure 25 min et **repart automatiquement à 25 min** à l'expiration (`DUREE_MINUTES = 25`, clé `tnx_countdown_v2`). « 4 » identique sur 3 chargements, servi en dur dans le HTML (origine Liquid ou texte fixe : **[À VÉRIFIER]**). Dir. 2005/29 annexe I pt 7 (fausse disponibilité limitée) : pratique interdite en toutes circonstances |
| Paiement | Mastercard, Visa, PayPal, Google Pay, Apple Pay, Shop Pay, Amex | `[PAGE]` | ✅ |

Apps observées (rappel `../ANALYSE.md`) : bundle maison `tnx-kb` (Kaching en fond), Intelligems (test A/B de prix en cours, classe `test-prix-b` sur la section produit), Klaviyo, ParcelWill, WeTracked, pixels Meta / TikTok / Google.

## 3. Les textes de la page, recopiés tels quels

> Ordre de la page mobile. Texte exact. Repère et note à côté, **texte non modifié**.

| # | Emplacement | Texte exact | Repère | Note réglementaire |
|---|---|---|---|---|
| T01 | Barre d'annonce (défilante) | « • GARANTIE À VIE — SANS CONDITIONS • » / « • OFFRE DE SAISON : JUSQU'À -70% • » | ❌ | Garantie contredite par la politique (30 j) ; -70 % non atteint (max réel -62,5 %) |
| T02 | Galerie `images/01.jpg` (badges) | « Best Seller » · « ÉLU POÊLE SANTÉ 2026 » (médaille, drapeau FR) · « 100% TITANE PUR » · « CERTIFIÉ CE » · « SANS PFOA » · « GARANTIE À VIE » · « ★★★★★ +100 000 CLIENTS SATISFAITS » | ❌ | « Élu… » = faux prix/label sans organisme (2005/29 annexe I pt 2 et 4) ; **le marquage CE ne s'applique pas à une poêle** (règl. 765/2008 art. 30 : apposer le CE hors champ est interdit) ; « sans PFOA » = interdit dans l'UE depuis 2020 (règl. 2019/1021), présenter une obligation légale comme un atout (annexe I pt 10) ; « 100 % titane pur » contredit par `images/08.png` |
| T03 | Galerie `images/02.png`, panneau gauche | « POÊLES CLASSIQUES » « REVÊTEMENT TOXIQUE » « +10.000 composés nocifs au contact de vos aliments » | ❌ | Chiffre sans source ; dénigrement collectif des poêles revêtues (L121-2 C. conso.) |
| T04 | Galerie `images/02.png`, panneau droit | « TITANOX TITANE PUR » « 100% TITANE PUR » « Matière la plus saine et sûre pour votre santé » | ❌ | Superlatif santé non prouvé ; composition contredite |
| T05 | Galerie `images/03.png` | « TECHNOLOGIE TITANOX RELIEF 2.0™ » « -75 % de contact avec les aliments » « Réduit naturellement l'accroche » « 3x moins de matière grasse » « *Texture titane martelée brevetée TITANOX » | ⚠️ | -75 % et 3x : essai à fournir ; « brevetée » : numéro de brevet à fournir, sinon ❌ |
| T06 | Galerie `images/04.png` | « MANCHE TITANOX AMOVIBLE & PRATIQUE » « Système de fixation ultra-solide » « Montage et démontage en 15 secondes » « Vos poêles s'empilent parfaitement » | ✅ | Vérifiable sur le produit ; « ultra-solide » à garder sobre |
| T07 | Galerie `images/05.png` | « CONÇUE POUR DURER TOUTE UNE VIE » « POÊLE CLASSIQUE » / « TITANOX TITANE PUR » + médaille « TITANOX ∞ GARANTIE À VIE » | ⚠️ | Durabilité à prouver (dir. 2024/825, allégation de durabilité) ; garantie à vie contredite |
| T08 | Galerie `images/06.png`, panneau haut | « POÊLES CLASSIQUES 29,99 € tous les 2 ans = 149,95 € sur 10 ans » « DURE 2 ANS » | ⚠️ | Comparaison de prix hypothétique : prix et durée de vie de référence à sourcer |
| T09 | Galerie `images/06.png`, panneau bas | « DURE 25 ANS » « TITANOX TITANE PUR 59,99 € une seule fois + GARANTIE À VIE » | ⚠️ | 25 ans à prouver ; « garantie à vie » contredite |
| T10 | Galerie `images/07.png` | « + de 100.000 clients satisfaits » « ★★★★★ Excellent 4,8 sur 5 noté sur Trustpilot » « POÊLE SANTÉ N°1 EN FRANCE » + 3 portraits (chef, femme, senior) | ❌ | **Trustpilot réel : 3,7/5, 391 avis, profil non revendiqué** (relevé 22/11/2026) ; « N°1 en France » sans preuve ; portraits d'apparence IA présentés comme clients (annexe I pt 22-23 : faux avis / faux consommateurs) |
| T11 | Galerie `images/08.png` (coupe) | « ZÉRO REVÊTEMENT. ZÉRO CHIMIQUE. 100% TITANE PUR. » « Surface Titane Pur — Anti-adhérente — Sans toxine à vie » « Noyau Aluminium — Chaleur rapide — Cuisson homogène » « Base acier Inoxydable — Compatible induction — Résistance maximale » | ❌ | **L'image elle-même montre 3 matériaux : « 100 % titane pur » est faux** (2005/29 art. 6 §1 b, composition). « Zéro chimique » : tout matériau est chimique, allégation vide |
| T12 | Galerie `images/09.png` à `11.png` (+ 2 vidéos dans la galerie rendue) | « 26 CM » · « 28 CM » · « 30 CM » | ✅ | |
| T13 | Preuve sociale (au-dessus du titre) | « Claire , Julien et +46 842 foyers ont choisi une cuisine plus saine pour leur famille. » | ❌ | Chiffre incompatible avec « 100,000+ » deux lignes plus bas ; à prouver par les commandes |
| T14 | Sur-titre | « #1 POÊLE SANTÉ 2026 » | ❌ | Classement inexistant (2005/29 annexe I pt 4) |
| T15 | Titre (H1 visuel) | « Poêle 100% Titane Pur Pour Une Cuisine Sans Toxines » | ❌ | Composition (voir T11) ; « sans toxines » = allégation santé absolue non prouvable |
| T16 | Sous-titre | « Le titane pur pour une cuisine plus saine et savoureuse au quotidien pour votre famille. » | ⚠️ | « plus saine » : à nuancer (pas de bénéfice santé démontré) |
| T17 | Note | « ★★★★★ 100,000+ Clients satisfaits » | ❌ | Non prouvé ; contredit T13 et les avis (3.214) |
| T18 | Puces | « Relief martelé pour une cuisson antiadhésive » · « Surface pure sans revêtement toxique » · « Fabriquée avec 100 % de titane pur » · « Conçue pour durer toute une vie » | ⚠️ / ❌ / ❌ / ⚠️ | 1 : « antiadhésive » à nuancer (avis Trustpilot : ça accroche) ; 3 : faux d'après `images/08.png` ; 4 : durabilité à prouver |
| T19 | Encart garantie | « 30 JOURS D'ESSAI SATISFAIT OU REMBOURSÉ Si vous n'êtes pas entièrement satisfait, Nous vous remboursons ! » | ❌ | Contredit par la politique de retour (utilisé ou promo = non remboursé) |
| T20 | Stock | « Plus que 4 poêles en stock. » | ❌ | Voir section 2, urgence |
| T21 | Guide des tailles | « Vous hésitez sur la taille ? Trouvez la taille qui vous correspond parfaitement du premier coup grâce à notre guide. » « QUOTIDIEN 26 cm 3 œufs · 1-2 portions Le format malin pour les cuissons rapides de tous les jours. » « LE PLUS CHOISI 28 cm 5 œufs · 2-3 portions Le format équilibré qui s'adapte à tous vos repas du quotidien sans jamais encombrer. » « FAMILLE 30 cm 8 œufs · 3-4 portions Le format généreux pour les grandes tablées et les repas en famille. » | ✅ | « Le plus choisi » : vrai si les ventes le confirment |
| T22 | Paliers | « OFFRE DE SAISON : JUSQU'À -70% » · « -50% 1x Poêle Titanox® Économisez 60,01€ 59,99€ 120,00€ » · « -60% • MEILLEURE VENTE Set 2 Poêles Titanox® Économisez 140,02€ 99,98€ 240,00€ » · « -70% • MEILLEURE OFFRE Set 3 Poêles Titanox® Économisez 225,03€ 134,97€ 360,00€ » · tailles « 26 cm Classique / 28 cm Moyenne / 30 cm Grande » | ❌ | Voir section 2 (Omnibus + pourcentages faux) |
| T23 | Bloc cadeau (image) | « DERNIÈRE CHANCE Livraison Premium OFFERTE d'une valeur de 20€ Express Protégée Garantie » | ❌ | Fausse urgence + valeur offerte fictive |
| T24 | Compte à rebours | « 00 : 00 : 25 : 00 Jours Heures Minutes Secondes » | ❌ | Minuteur qui se relance (code lu) |
| T25 | Badges + CTA | « 30J Satisfait ou remboursé » « STOCK FAIBLE ! » « ➜ AJOUTER AU PANIER » | ❌ / ❌ / ✅ | « STOCK FAIBLE ! » permanent |
| T26 | Mini-avis sous CTA | « Mes petits-enfants mangent enfin sainement. C'est tellement rassurant de pouvoir cuisiner tous leurs plats préférés sans aucun revêtement toxique. » Monique D. · « Rien n'accroche ! Je ne pensais pas que c'était possible sans revêtement et pourtant même les œufs se décollent sans le moindre effort. Agréablement surpris. » Didier B. · « Solide comme du béton ! J'ai la mienne depuis bientôt cinq ans et je l'utilise presque tous les jours pour ma famille. Elle est toujours dans un état impeccable. » Aurélie L. | ❌ | « depuis bientôt cinq ans » impossible pour un produit en ligne depuis avril 2026 (faux avis, annexe I pt 23 ter) ; origine des avis non indiquée (Omnibus : dire comment les avis sont vérifiés) |
| T27 | Accordéon 1 | « NATURELLEMENT ANTI-ADHÉSIVE Le titane martelé TITANOX® est anti-adhésif sans le moindre revêtement. Ses micro-reliefs limitent le contact avec les aliments, ce qui les empêche d'accrocher à la surface. ✓ Les aliments se détachent seuls — œufs, poisson, viande glissent sans effort ✓ Cuisinez plus léger — une noisette de matière grasse suffit ✓ Anti-adhérence garantie 25 ans — aucune couche chimique qui s'use » | ⚠️ | « se détachent seuls » contredit par plusieurs avis Trustpilot ; « garantie 25 ans » ≠ « à vie » |
| T28 | Accordéon 2 | « ZÉRO REVÊTEMENT TOXIQUE La plupart des poêles libèrent des PFAS , PTFE et PFOA pendant la cuisson. Ces substances finissent dans votre assiette, repas après repas. Le titane pur TITANOX® n'a aucun revêtement, donc aucune substance chimique à relâcher dans vos plats. ✓ Aucune substance nocive — ni PFAS, ni PTFE, ni PFOA ✓ 100% titane pur — la matière utilisée par le secteur médical ✓ Conforme aux normes alimentaires européennes — sécurité certifiée » | ❌ / ⚠️ | ❌ « La plupart des poêles libèrent… PFOA » : le PFOA est interdit dans l'UE depuis 2020 ; affirmation générale non sourcée (dénigrement). ⚠️ « ni PFAS » : rapport d'analyse de la surface à fournir. ⚠️ « Conforme aux normes alimentaires européennes » : **déclaration de conformité contact alimentaire (règl. 1935/2004 art. 16) à obtenir du fournisseur** ; « sécurité certifiée » : par qui ? ❌ « secteur médical » : grade médical non démontré |
| T29 | Accordéon 3 | « COMPATIBLE À TOUS LES USAGES La poêle TITANOX® fonctionne sur toutes vos plaques, sans exception. De la cuisson au nettoyage, elle s'adapte à votre quotidien sans la moindre contrainte. ✓ Toutes les plaques — induction, gaz, électrique, vitrocéramique ✓ Va au four jusqu'à 260°C — sans aucune déformation ✓ Passe au lave-vaisselle — ou un simple coup d'éponge » | ⚠️ | 260 °C contredit par la page FAQ (548 °C) ; induction = grâce à la base inox (donc pas 100 % titane) |
| T30 | Accordéon 4 | « FAITE POUR DURER TOUTE UNE VIE Une poêle classique s'abîme vite. Le revêtement se raye, se décolle, et au bout de deux ans vous la jetez pour en racheter une autre . Encore et encore. Le titane pur ne s'use pas, ne s'écaille pas, ne se déforme pas. Année après année, votre poêle garde les mêmes performances qu'au premier jour . Vous l'achetez une seule fois, et elle vous suit pendant plus de 25 ans . C'est sans doute le meilleur investissement que vous ferez dans votre cuisine. » | ⚠️ | Durabilité (dir. 2024/825, applicable sept. 2026) : preuve requise pour « plus de 25 ans » ; « ne s'use pas » absolu |
| T31 | Accordéon 5 | « GARANTIE & LIVRAISON ✓ Garantie à vie, sans conditions — au moindre défaut, nous vous renvoyons un produit neuf gratuitement ✓ 30 jours pour l'essayer chez vous — si elle ne vous convainc pas, vous êtes remboursé intégralement ✓ Commande expédiée sous 24h — livraison gratuite à domicile ✓ Une question ? — notre équipe vous répond 7 jours sur 7 » | ❌ | Garantie et remboursement contredits par la politique ; « 7 jours sur 7 » contredit par les mentions légales (« du lundi au vendredi, de 9h à 18h ») et la FAQ (« 6j/7 ») |
| T32 | Vidéos clients | « TITANOX® EN ACTION » Gisèle S. France · Martine P. France · Michel G. Belgique · Bernard L. Suisse · Sylvie T. Suisse | ⚠️ | Personnes réelles ou acteurs/IA ? Si joué : mention « dramatisation » (règle maison 8) |
| T33 | Bloc avis | « Ils ont retrouvé le plaisir de cuisiner plus sainement » « Excellent 4.8 / 5 basé sur +3.214 avis » + 9 avis « Acheteur vérifié » (texte en section 7) | ❌ | Note et nombre d'avis sans source ; « Acheteur vérifié » sans procédure décrite (Omnibus, annexe I pt 23 ter) ; avis « bientôt 6 ans » (Antonio D.) impossible |
| T34 | Bandeau logos | Logos « marmiton », « Cuisine Actuelle », « santé magazine », « Cuisine et Vins de France » (sans titre, en défilement) | ❌ | Laisse croire à une parution presse : à prouver par article, sinon faux média (2005/29 annexe I pt 11) + usage de marques tierces |
| T35 | 7 raisons — intro | « 7 RAISONS Pourquoi TITANOX sera la dernière poêle que vous achèterez La poêle en titane pur qui remplace toutes les autres. » | ⚠️ | Promesse de durabilité |
| T36 | Raison 1 | « UNE SURFACE QUI N'ACCROCHE JAMAIS Le titane pur est naturellement antiadhésif, et sa surface martelée crée des milliers de micro-reliefs qui réduisent le contact avec les aliments. C'est cette combinaison qui fait que rien n'accroche, sans aucun revêtement. » | ⚠️ | « jamais » absolu, contredit par des avis |
| T37 | Raison 2 | « CUISINEZ SANS TOXINES, ZÉRO PFAS, PTFE NI PFOA Aucun revêtement chimique ne finit dans votre assiette. Vous cuisinez directement sur une surface en titane pur , une matière saine qui ne libère aucun composé nocif dans vos aliments. » | ⚠️ | Preuve : rapport de migration (règl. 1935/2004) |
| T38 | Raison 3 | « DU TITANE POUR DES SAVEURS PLUS INTENSES Le titane conduit la chaleur jusqu'à trois fois mieux que l'inox. La chaleur se répartit partout de façon régulière , ce qui préserve les arômes et donne à vos plats une cuisson plus savoureuse . » | ❌ | Physiquement douteux : le titane conduit la chaleur à peu près comme l'inox (environ 15-22 W/m·K), pas 3 fois mieux. La répartition vient du noyau aluminium (`images/08.png`) |
| T39 | Raison 4 | « 3X MOINS D'HUILE Plus besoin de noyer vos aliments dans l'huile pour réussir vos plats. Un simple filet suffit pour obtenir le même résultat , en cuisinant plus léger et plus sainement. » | ⚠️ | « 3X » : essai à fournir |
| T40 | Raison 5 | « COMPATIBLE AVEC TOUTES LES CUISINES Induction , gaz, électrique, vitrocéramique ou four. La Titanox fonctionne parfaitement sur tous les types de feu et s'adapte sans effort à votre cuisine. » | ✅ | Si testé (induction confirmée par la base inox) |
| T41 | Raison 6 | « NETTOYAGE FACILE De l'eau chaude, un peu de savon, un coup d'éponge et elle est comme neuve . Elle est aussi parfaitement compatible avec le lave-vaisselle . » | ⚠️ | Avis Trustpilot « très compliqué à nettoyer » |
| T42 | Raison 7 | « TAILLÉE DANS LE MÉTAL, GARANTIE À VIE Ce n'est pas une poêle jetable avec un revêtement "effet titane". C'est une poêle taillée dans le métal , durable , et pensée pour rester dans votre cuisine pendant des années. » | ⚠️ | Garantie contredite ; « durable » à prouver |
| T43 | CTA | « JE COMMANDE MA POÊLE EN TITANE ➜ » | ✅ | |
| T44 | Le problème — intro | « LE PROBLÈME Les poêles traditionnelles ne tiennent pas leurs promesses Derrière les belles promesses, l'industrie des poêles vend des produits qui s'usent, qui polluent et qui se rachètent. » | ⚠️ | Dénigrement collectif ; « polluent » : allégation environnementale négative non sourcée |
| T45 | Problème 1 | « Tout finit par coller Le revêtement s'use à chaque cuisson. Les aliments accrochent, il faut toujours plus de gras, et le plat est quand même raté. » | ✅ | Expérience courante, formulée sans chiffre |
| T46 | Problème 2 | « Du poison dans votre assiette À chaque cuisson, le revêtement se décolle. Toute la famille avale des milliers de composés toxiques , que l'Europe veut interdire. » | ❌ | « poison », « milliers de composés toxiques » : peur non sourcée (2005/29 annexe I pt 12, exploitation de la peur) ; « que l'Europe veut interdire » : restriction PFAS de l'ECHA en cours, pas adoptée ; les ustensiles de cuisine ont été exclus de la loi française PFAS de 2025 `[À VÉRIFIER]` |
| T47 | Problème 3 | « À racheter tous les 2 ans Le revêtement s'use, la poêle part à la poubelle. Pas chères à l'achat, vos poêles vous coûtent près de 1 000 € en 10 ans. » | ❌ | « 1 000 € en 10 ans » contredit `images/06.png` (149,95 € sur 10 ans) |
| T48 | Avis clients (8 cartes) | Voir section 7 ; badge « Trustpilot 4,8/5 basé sur 3.214+ avis clients » | ❌ | **Trustpilot réel : 3,7/5, 391 avis** |
| T49 | Bannière | « ANNIVERSAIRE : LE FONDATEUR DE TITANOX CÉLÈBRE L'ÉVÉNEMENT AVEC VOUS ! -50 % SUR TOUT LE SITE. » (homme tenant une poêle dont l'étiquette porte un texte incohérent : « SARE BBILETCHENT… CAMPISTALE NEJECTION ») | ❌ | Image générée par IA présentée comme le fondateur (faux) ; anniversaire d'une marque dont la fiche date d'avril 2026 ; -50 % pas sur tout le site |
| T50 | Rappel offre | (paliers T22 répétés) + « Plus que 4 poêles en stock. » | ❌ | idem T20 / T22 |
| T51 | FAQ — accroche | « Est-ce que la Titanox accroche ? Non. C'est là toute la différence du titane 100% pur . Contrairement aux poêles en inox classiques, la Titanox n'exige aucun geste particulier, aucun préchauffage spécial, aucune technique. Vous cuisinez normalement — rien n'accroche. La surface martelée en titane pur est naturellement anti-adhérente, sans aucun revêtement chimique. » | ⚠️ | Trustpilot : « il est très difficile de maîtriser la poêle pour ne pas que les aliments accrochent » |
| T52 | FAQ — pourquoi le titane | « Pourquoi le titane et pas une poêle antiadhésive classique ? Parce que votre poêle antiadhésive vous empoisonne. Les revêtements PTFE et PFOA se dégradent à la chaleur et libèrent des microparticules toxiques directement dans vos plats. Vous les mangez. Chaque jour. Le titane pur, lui, ne contient aucun revêtement, aucune chimie, aucun risque. C'est le métal le plus sûr au monde — utilisé même en implants médicaux. » | ❌ | « vous empoisonne » ; « aucun risque » ; « le métal le plus sûr au monde » (superlatif non prouvable) |
| T53 | FAQ — feu | « C'est compatible avec mon feu ? Oui — tous les feux sans exception. Induction, gaz, électrique, vitrocéramique et même four jusqu'à 260°C. La base inox ferritique assure une compatibilité totale. Et les ustensiles métal sont autorisés — le titane ne se raye pas. » | ⚠️ | **Aveu de la base inox** (contredit « 100 % titane ») ; « ne se raye pas » absolu |
| T54 | FAQ — garantie | « C'est vraiment garanti à vie ? Oui. À vie. Sans conditions. Le titane pur ne s'use pas, ne s'écaille pas, ne se dégrade pas. Elle sera dans votre cuisine dans 10 ans, dans 20 ans — exactement comme le premier jour. Si un défaut apparaît, on remplace. Simple. » | ❌ | Contredit la politique (30 jours) |
| T55 | FAQ — nettoyage | « C'est facile à nettoyer ? Un coup d'éponge suffit. Souvent juste de l'eau chaude. Rien n'accroche, rien ne brûle — le nettoyage prend 10 secondes. Elle passe aussi au lave-vaisselle , mais vous n'en aurez probablement pas besoin. » | ⚠️ | « 10 secondes » ; « rien ne brûle » contredit par avis |
| T56 | FAQ — PFAS | « Elle contient vraiment zéro PFAS ? Zéro PFAS. Zéro PTFE. Zéro PFOA. Aucun revêtement, aucun traitement, aucun produit chimique caché. La Titanox est fabriquée en titane 100% pur — le seul matériau certifié sans toxine et biocompatible. Ce que vous cuisinez dedans, c'est de la nourriture. Rien d'autre. » | ❌ | « le seul matériau certifié sans toxine » : aucune certification de ce type n'existe ; composition contredite |
| T57 | FAQ — taille | « Quelle taille choisir ? 26 cm — idéale pour 1 à 2 personnes. Œufs, légumes, poisson. 28 cm — le format polyvalent pour 2 à 4 personnes. Le plus vendu. 30 cm — parfaite pour les familles et les grandes cuissons. Steaks, wok, plats complets. » | ✅ | (28 cm : « 2 à 4 » ici, « 2-3 » dans le guide) |
| T58 | FAQ — manche | « Le manche chauffe-t-il ? Non. Le manche Titanox est conçu pour ne pas monter en température — même après une longue cuisson. Vous pouvez le saisir à mains nues en toute sécurité. » | ❌ | **Risque de brûlure** (GPSR, règl. 2023/988) : affirmation de sécurité à prouver par un essai, et faux après passage au four à 260 °C |
| T59 | FAQ — ustensiles métal | « Puis-je utiliser des ustensiles en métal ? Oui. Le titane pur ne se raye pas. Spatules, fouets, pinces métal — aucun problème. Là où une poêle antiadhésive classique s'abîme au premier contact, la Titanox reste impeccable. » | ⚠️ | « ne se raye pas » absolu |
| T60 | FAQ — four | « La poêle est-elle adaptée à une cuisson au four ? Oui. La Titanox supporte des températures jusqu'à 260°C sans se déformer, sans libérer de fumées toxiques. Saisie sur le feu, finition au four — elle gère les deux sans aucun compromis. » | ⚠️ | 260 °C vs 548 °C (page FAQ) |
| T61 | FAQ — délais | « Quels sont les délais de livraison ? Les délais varient selon la période et le stock, mais la commande est traitée rapidement après validation. 3 à 5 jours pour l'Europe et 5 à7 jours pour l'internationale. Une fois expédiée, vous recevez une confirmation avec les informations de suivi. » | ⚠️ | « expédiée sous 24h » ailleurs |
| T62 | FAQ — suivi | « Comment suivre ma commande ? Dès l'expédition, vous recevez un e-mail avec votre numéro de suivi . Vous pouvez également suivre votre commande via la page de suivi dédiée sur notre site. » | ✅ | |
| T63 | Bloc offre limitée | « ⚠ OFFRE LIMITÉE Notre plus grosse réduction de l'année — jusqu'à -70% L'offre de saison est en ligne : la Titanox n'a jamais été proposée à ce prix — et ne le sera plus . Aujourd'hui, il ne reste que 4 poêles à ce prix . Une fois le stock épuisé, le prochain arrivage repart au prix normal — sans exception. » + CTA « JE PROFITE DES -70% ➜ » | ❌ | « jamais été proposée à ce prix » faux (même prix depuis avril) ; « ne le sera plus » ; stock fixe à 4 (annexe I pt 7) |
| T64 | Réassurance | « Livraison gratuite Livraison gratuite à domicile » · « Service client 7j/7 Pour toute demande, écrivez-nous via notre formulaire de contact ou par e-mail à contact@titanoxfrance.com . » · « Garantie 30 jours Satisfait ou remboursé » · « Paiements sécurisés Payez en toute sécurité via Carte de crédit ou PayPal. » | ⚠️ | 7j/7 contredit ; 30 jours contredit par la politique |
| T65 | Footer | « Rejoignez la communauté TITANOX Cuisinez plus proprement, découvrez nos offres exclusives et reprenez le contrôle de ce que vous mettez dans votre assiette. » · « Notre Mission Protéger votre santé et celle de votre famille — un repas à la fois. Nous croyons que cuisiner sainement ne devrait pas être un luxe. C'est pourquoi nous avons créé la seule poêle sans compromis : zéro revêtement, zéro toxine, zéro PFAS. Du titane pur. Pour toujours. » | ❌ | « Protéger votre santé » (allégation santé) ; « la seule poêle sans compromis » (superlatif exclusif) |
| T66 | Pop-up | « UN TOUR, UNE RECOMPENSE GARANTIE » « JE TOURNE LA ROUE » | ⚠️ | Règlement du jeu non affiché |
| T67 | Mentions légales | « Les informations communiquées sur notre site concernant la composition, l'utilisation, l'entretien ou les performances des produits sont fournies à titre indicatif. » | ❌ | Une mention « à titre indicatif » ne couvre pas une composition fausse ; mentions LCEN incomplètes (SIREN/RCS, capital, directeur de publication) |

## 4. Les claims (promesses)

| # | Claim exact | Où | Repère | Règle en cause | Preuve à fournir |
|---|---|---|---|---|---|
| S01 | « 100% titane pur » / « Fabriquée avec 100 % de titane pur » / « 100% titane pur certifié » | Titre, puces, galerie, FAQ, toutes les pubs | ❌ | 2005/29 art. 6 §1 b (composition) : contredit par `images/08.png` (noyau alu + base inox) et la FAQ (« base inox ferritique ») | Fiche technique fournisseur : couches, grade du titane, épaisseur |
| S02 | « Sans PFAS / ni PTFE / ni PFOA » | Page, pubs | ⚠️ | Allégation « sans » : rapport d'analyse requis ; « sans PFOA » = obligation légale UE depuis 2020 (annexe I pt 10) | Rapport de labo sur la surface (PFAS totaux) |
| S03 | « Conforme aux normes alimentaires européennes — sécurité certifiée » | Accordéon 2 | ⚠️ | Règl. 1935/2004 (contact alimentaire), déclaration de conformité | DoC + essais de migration du fournisseur |
| S04 | « Sans toxines », « zéro toxine », « une cuisine plus saine », « Protéger votre santé » | Titre, footer, pubs | ❌ | Allégation santé absolue non démontrable ; Meta (promesse santé) | Aucune preuve possible au sens strict ; nuancer |
| S05 | « Votre poêle antiadhésive vous empoisonne », « Du poison dans votre assiette », « PFAS classés cancérigènes » | FAQ, section problème, pubs | ❌ | Exploitation de la peur (annexe I pt 12), dénigrement ; Meta (contenu choquant, attribut personnel « vous empoisonnez votre famille ») | Source scientifique précise ; le PFOA (classé cancérogène CIRC groupe 1) est interdit dans l'UE ; le PTFE n'est pas classé |
| S06 | « #1 POÊLE SANTÉ 2026 », « ÉLU POÊLE SANTÉ 2026 », « POÊLE SANTÉ N°1 EN FRANCE », « La poêle la mieux notée de France » | Page, galerie, pubs | ❌ | 2005/29 annexe I pt 2 et 4 (faux label, fausse approbation) | Classement réel par un organisme |
| S07 | « CERTIFIÉ CE » | Galerie `images/01.jpg` | ❌ | Règl. 765/2008 art. 30 : CE interdit hors des produits concernés | Aucune (à retirer) |
| S08 | « 100,000+ Clients satisfaits » / « +46 842 foyers » / « 25,000+ » (aiguiseur) | Page, galerie | ❌ | Chiffres contradictoires, non prouvés | Export des commandes |
| S09 | « Excellent 4.8 / 5 basé sur +3.214 avis » / « noté sur Trustpilot » | Page, galerie | ❌ | Faux : Trustpilot = 3,7/5, 391 avis ; Omnibus (avis) | Source réelle des avis |
| S10 | Logos marmiton / Cuisine Actuelle / santé magazine / Cuisine et Vins de France | Bandeau | ❌ | Faux média si pas de parution (annexe I pt 11) | Articles publiés |
| S11 | « Garantie à vie, sans conditions » / « Anti-adhérence garantie 25 ans » | Page, pubs | ❌ | Contredit la politique écrite (30 jours) ; garantie commerciale sans conditions écrites (L217-21) | Contrat de garantie écrit |
| S12 | « 30 JOURS D'ESSAI SATISFAIT OU REMBOURSÉ » | Page, pubs | ❌ | Contredit la politique (utilisé = non remboursé ; promo = non remboursé) ; dir. 2011/83 | Politique alignée |
| S13 | « Conçue pour durer toute une vie », « plus de 25 ans », « DURE 25 ANS », « la dernière poêle que vous achèterez » | Page, galerie, pubs | ⚠️ | Dir. 2024/825 (durabilité, applicable fin sept. 2026) | Essais d'usure / garantie réelle |
| S14 | « Le titane conduit la chaleur jusqu'à trois fois mieux que l'inox » | Raison 3 | ❌ | Faux physiquement ; 2005/29 art. 6 | Aucune |
| S15 | « 3x moins de matière grasse » / « 3X MOINS D'HUILE » / « -75 % de contact avec les aliments » | Galerie, raison 4 | ⚠️ | Chiffres à prouver | Protocole d'essai |
| S16 | « Texture titane martelée brevetée TITANOX » / « TITANOX RELIEF 2.0™ » | Galerie | ⚠️ | Brevet à prouver | N° de brevet |
| S17 | « Le manche… ne pas monter en température… à mains nues en toute sécurité » | FAQ | ❌ | GPSR 2023/988 (sécurité) | Essai de température du manche |
| S18 | « le titane ne se raye pas » / « Rien n'accroche » / « jamais » | FAQ, raisons | ⚠️ | Absolu contredit par des avis | Nuancer |
| S19 | « Va au four jusqu'à 260°C » vs « jusqu'à 548°C » | Page / page FAQ | ⚠️ | Incohérence | Fiche fournisseur |
| S20 | « Le métal le plus sûr au monde — utilisé même en implants médicaux » / « le seul matériau certifié sans toxine et biocompatible » | FAQ | ❌ | Superlatif et certification inexistants | Aucune |
| S21 | « OFFRE 15ᵉ ANNIVERSAIRE », « On a 15 ans », « On n'a jamais fait ça en 15 ans » | Pubs, bannière | ❌ | Fausse ancienneté (2005/29 art. 6 §1 f, qualités du professionnel) : fiche créée en avril 2026 | Kbis / historique de la marque |
| S22 | « Set de 5 ustensiles… offert d'une valeur de 79,99 € » ; « quatre cadeaux offerts d'une valeur de 220€ » | Pubs | ❌ | Le coffret 5 ustensiles est vendu 59,99 € sur le site (`products.json`) : valeur gonflée | Prix réellement pratiqués |
| S23 | « Dans la limite des stocks », « Stock limité », « Plus que 4 », compte à rebours | Pubs, page | ❌ | Annexe I pt 7 | Stock réel |
| S24 | « Retrouvez une santé que vous pensiez perdue », « Ma santé s'est améliorée le jour où j'ai jeté mes poêles toxiques » | Pubs (page 1495731186949867 et 106977935010411) | ❌ | Allégation de guérison / bénéfice santé (2005/29 annexe I pt 17) ; Meta (promesse santé) | Aucune |
| S25 | « Une noisette de matière grasse suffit », « nettoyage 10 secondes » | Page, FAQ | ⚠️ | Promesse de résultat | Démonstration vidéo réelle |

## 5. Les pubs actives (bibliothèque publicitaire Meta)

### Quelle page Meta correspond à titanoxfrance.com ?

| Page | page_id | Pubs actives | Destination lue dans les pubs | Verdict |
|---|---|---|---|---|
| **Titanox** | **106977935010411** (profil FB 100094249497095) | **~1 600** | **titanoxfrance.com/products/titanox-poele-en-titane-pur-sans-pfas** (27 liens sur 27 lus) | **RETENUE** |
| Titanox | 1495731186949867 (profil FB 61596157143439) | 13 (98 au total) | **titanoxtitanepur.com**/products/titanox-poele-en-titane-pur-sans-pfas : une **autre boutique Shopify** (shop id 101262983470, prix 66,00 / 72,00 / 77,00 € barrés 132 / 143 / 154 €) | Non retenue : autre domaine, mêmes visuels et textes. **Clone d'un concurrent ou autre boutique de l'utilisateur : [À VÉRIFIER]** |
| Titanox Pure Titanium | 1195472263648011 | ~370 | shoptitanox.com/products/100-pure-titanium-pan-titanox (anglais, USD) | Non retenue : marché US, autre domaine |
| Bien Manger Magazine | 1194227740437833 | 58 | **titanoxfrance.com** (25 liens sur 25) | Page au **nom de média** qui pousse la même offre : voir ❌ ci-dessous |

Raison du choix : c'est la seule page « Titanox » dont les liens de destination pointent vers titanoxfrance.com (vérifié dans la bibliothèque, 27 liens sur 27), avec le même handle produit, les mêmes offres (-50 %, « 15 ans », garantie à vie) et la même devise de page FR. Les deux pages citées dans la demande ne vont pas sur ce domaine.

### Pubs de la page 106977935010411 (relevé du 22/11/2026, 327 cartes lues, classées par impressions)

« Cartes » = blocs de la bibliothèque ; « pubs » = total des variantes (« N publicités utilisent ce contenu »). « Restreinte » = mention Meta « Cette publicité n'est pas active pour certaines audiences car elle ne répondait pas à certaines exigences ». Âge au 22/11/2026.

| Pub (ID exemple) | Active depuis | Variantes | Format | Hook (début exact) | Angle | Restreinte |
|---|---|---|---|---|---|---|
| 1137834651932059 | 16/10 (37 j) → 15/11 | 37 cartes / 68 pubs | Image | « 🔥 La plus grosse réduction de notre histoire sur la meilleure poêle antiadhésive et saine du marché. » | Promo + santé + durabilité | Oui |
| 2229406277619462 | 16/10 (37 j) → 15/11 | 74 / 74 | Image | « 🔥 La plus grosse réduction de notre histoire sur la poêle Titanox. » — titre « 🔥 -50 % dans la limite des stocks » | Promo / rareté | Non |
| 1688993129231133 | 16/10 (37 j) → 15/11 | 64 / 65 | Image | « 🔥 On a 15 ans. On fait -50 % sur la poêle Titanox, avec les cadeaux offerts 🎁. » — titre « 🚨 -50 % + CADEAUX — OFFRE 15 ANS » | Anniversaire + cadeaux | Non |
| 1664633185392146 / 1089490777196409 | 19/10 (34 j) | 18/44 + 9/28 | Vidéo | « 🚨 Ce que l'industrie ne veut pas que vous sachiez : vos poêles antiadhésives contiennent des PFAS classés cancérigènes. Chaque repas, une dose supplémentaire dans votre corps. Pour toujours. » | Peur PFAS / ennemi commun | Oui |
| 1593104432504230 | 19/10 (34 j) | 6 / 11 | Vidéo 0:53 | « 😋 Vos plats n'auront plus jamais le même goût. » | Goût / saisie | Oui |
| 1116527824670769 | 16/10 (37 j) | 13 / 13 | Vidéo | « 💰 800 euros. C'est ce que coûtent 20 ans de poêles antiadhésives. 40 euros pièce, remplacées tous les ans quand le revêtement lâche. » | Coût sur la durée | Non |
| 1634351554856936 | 16/10 (37 j) → 09/11 | 10 / 10 | Image | « 🍳 Quand j'ai commandé, j'étais persuadée que ça allait coller. » — titre « 🍳 J'étais sûre que ça allait coller. » | Sceptique convaincue (témoignage) | Non |
| 1833533227677514 | 16/10 (37 j) → 16/11 | 9 / 9 | Image | « ⚖️ Vous cherchez une poêle saine. Vous avez trois options sur le marché, et deux vous décevront. » — titre « ⚖️ Céramique, inox, titane : le vrai match. » | Comparatif matériaux | Non |
| 1450250900571854 | 16/10 (37 j) → 15/11 | 11 / 12 | Image | « 🏆 La meilleure poêle antiadhésive et saine du marché. » — titre « ⭐⭐⭐⭐⭐ La poêle la mieux notée de France. » | Superlatif / preuve sociale | Non |
| 1434017485504698 | 16/10 (37 j) → 15/11 | 11 / 14 | Image | « 🔥 On n'a jamais fait ça en 15 ans. Et on ne le refera pas. » — titre « 🔥 LA PLUS GROSSE VENTE DE L'ANNÉE : -50 % » | Promo exceptionnelle | Non |
| 2299842060805678 / 2086627821980284 | 17/10 (36 j) → 13/11 | 3 + 4 | Image | « ⚠️ Regardez le fond de votre poêle. Ces petites rayures, ces zones où le noir a disparu. » — titre « ⚠️ Ces rayures partent quelque part. » | Constat chez soi (rayures) | Non |
| 1470593321838917 | 19/10 (34 j) | 6 / 14 | Image | « On vous a vendu des poêles "pratiques". » | Ennemi commun | Oui |
| 1846919102970620 | 19/10 (34 j) | 3 / 12 | Vidéo | « 🚨 J'ai jeté TOUTES mes poêles antiadhésives le jour où j'ai compris ce qu'elles relâchaient dans nos assiettes. 😱 » | Témoignage mère / enfants | Oui |
| 1736677547438896 | 19/10 → 15/11 | 2 / 6 | Vidéo | « Ne payez jamais Titanox au prix plein. Profitez de l'offre en cours — moins 50% et quatre cadeaux offerts d'une valeur de 220€. » | Promo + cadeaux | Non |
| 1755037612374163 | 16/10 (37 j) | 2 / 2 | Vidéo | « 🍳 Je ne pensais pas qu'une poêle sans revêtement pouvait être antiadhésive. Franchement, j'y croyais pas du tout. » | Sceptique (UGC) | Non |
| 3420650731476743 | 16/10 (37 j) → 15/11 | 3 / 3 | Vidéo | « 🤨 Toutes les marques de poêles vous promettent une cuisson saine. » — titre « 🤨 « Sans toxines. » Vous l'avez déjà entendu. » | Méfiance du marché | Non |
| 1130271736421587 | 27/10 (26 j) | 4 / 4 | Image | « 🛡️ Vous hésitez parce qu'une poêle sans revêtement, il faut le voir pour le croire. C'est normal. Alors testez-la. » — titre « 🛡️ 30 jours pour l'essayer chez vous. » | Inversion du risque | Non |
| 1632799151974688 | 27/10 (26 j) | 5 / 5 | Image | « 🔬 Le martelage du titane crée des milliers de micro-creux sur toute la surface. » — titre « 🔬 L'antiadhésif n'a jamais eu besoin de chimie. » | Mécanisme | Non |
| 1118262954467385 | 02/11 (20 j) | 3 / 3 | Image | « 💸 J'ai compté. Neuf poêles en douze ans. » — titre « 💸 J'en rachetais une tous les ans. Fini. » | Coût sur la durée (1re personne) | Non |
| 29089261414038027 | 28/10 (25 j) | 3 / 3 | Image | « 🏆 Une poêle antiadhésive classique tient un an. Deux si vous y faites attention. » — titre « 🏆 Une seule poêle. Pour le reste de votre vie. » | Durabilité | Non |
| 1152340777212268 | 30/10 (23 j) | 3 / 4 | Vidéo | « 😳 Un matin, je fais des œufs pour mon petit-fils. Et je vois des petits points noirs dans le blanc. » | Grand-parent / déclic | Non |
| 1118805417276869 | 19/10 (34 j) | 1 | Vidéo | « À 73 ans, je viens de comprendre une chose terrible... » — titre « Préserver La Santé De Ma Famille 👉 » | Senior / santé | Non |
| Autres (1 à 2 cartes) | 15-20/10 à 16/11 | | Vidéo / image | « 🥘 Imaginez une poêle où rien n'accroche, rien ne brûle, rien ne toxifie. » · « J'ai compris quelque chose le mois dernier qui m'a glacée. » · « Les chefs étoilés ne cuisinent pas avec les poêles que vous avez chez vous. » · « 🍳 J'ai payé 280 euros pour un cours de cuisine 👨‍🍳. » · « ⚖️ Jusqu'ici, une poêle saine vous obligeait à un compromis. » · « 🚨 Votre poêle antiadhésive contient des composés controversés ⚠️, aujourd'hui interdits dans plusieurs pays. » | Divers | Selon pub |

Texte complet de chaque pub : `pubs/meta-106977935010411-actives.json`.

Titres vus via l'API sur les pages liées (non retenues, mêmes textes) : « Vous empoisonnez votre famille sans le savoir », « ✅ Retrouvez une santé que vous pensiez perdue. », « 🚨 Ma santé s'est améliorée le jour où j'ai jeté mes poêles toxiques. », « 🚨 ALERTE — On vous vend du poison depuis 40 ans. », « 🏆 Tout simplement la meilleure poêle de 2026 », « 🚨 Vos poêles contiennent des PFAS — -50 % aujourd'hui ».

**Angles qui tiennent** (actifs depuis 14 jours ou plus, plusieurs variantes) :
- **Promo « plus grosse réduction » / -50 % / « 15 ans » + cadeaux** : 175 cartes environ depuis le 16/10. Angle n° 1 en volume, mais repose sur un prix barré et une ancienneté non prouvés (❌).
- **Peur PFAS « Ce que l'industrie ne veut pas que vous sachiez »** : 27 cartes / 72 pubs depuis le 19/10, **toutes restreintes par Meta** sur une partie des audiences.
- **Sceptique « J'étais sûre que ça allait coller »** (image + UGC) : 16 cartes depuis le 16/10, non restreint.
- **Coût sur la durée « 800 euros / 20 ans », « Neuf poêles en douze ans »** : 16 cartes depuis le 16/10, non restreint.
- **Comparatif « Céramique, inox, titane : le vrai match »** : 9 cartes depuis le 16/10, non restreint.
- **Goût / saisie « Vos plats n'auront plus jamais le même goût »** : 6 cartes / 11 pubs depuis le 19/10 (restreint).
- **Rayures « Regardez le fond de votre poêle »** : 7 cartes depuis le 17/10, non restreint.

Constat : **les angles santé et peur sont restreints, les angles sceptique / coût / comparatif / rayures passent.** `[PUB]`

## 6. Les personas

| Persona | Problème (ses mots) | Déjà essayé | Hésitation | Angle qui lui parle | Provenance |
|---|---|---|---|---|---|
| P1 — Parent ou grand-parent protecteur (40-75 ans) | « Quand j'ai compris que mon ancienne poêle libérait des PFAS dans leurs assiettes chaque soir, j'ai eu honte. » (Sonia M.) · « Mes petits-enfants mangent enfin sainement. » (Monique D.) | Poêles antiadhésives classiques | Prix (60 € vs 30 €), peur que ça accroche | Rayures « Regardez le fond de votre poêle » ; constat avec le petit-fils | `[PAGE]` `[PUB]` |
| P2 — Retraité(e) qui cuisine tous les jours | « C'est moi qui cuisine à la maison depuis que je suis à la retraite… Elle chauffe vite et rien n'accroche. » (Gérard P.) | Poêles rachetées tous les 1-2 ans | « Encore une promesse » | Coût sur la durée « Neuf poêles en douze ans » ; « une seule poêle pour le reste de votre vie » | `[PAGE]` `[PUB]` |
| P3 — Cuisinier exigeant / ex-inox | « Je cuisine depuis plus de trente ans et j'ai toujours travaillé avec de l'inox. Quand j'ai vu qu'elle saisissait mieux… » (Jean-Marc D.) · « J'ai tout essayé — fonte, inox, céramique. » (Yanis B.) | Inox, fonte, céramique | Ça accroche comme l'inox ? | Comparatif « Céramique, inox, titane » ; goût / saisie | `[PAGE]` `[PUB]` |
| P4 — Actif(ve) pressé(e) | « Je cuisine vite fait en rentrant du taf, et ça me saoulait que ça colle ou que ça brûle. » (Sabrina T.) | Antiadhésif bas de gamme | Nettoyage, prise en main | Nettoyage facile ; « rien n'accroche » (démo œuf) | `[PAGE]` |
| **Oublié — Petite cuisine / rangement** | « Mes trois poêles prennent la place d'une seule sur mon étagère et moi qui ai une petite cuisine je gagne une place folle. » (Martine L.) | Poêles à manche fixe | — | Manche amovible + empilable (aucune pub sur cet angle) | `[PAGE]` `[DÉDUIT]` |
| **Oublié — Acheteur de cadeau (Noël)** | — | — | Taille à choisir pour un autre | Set 2 poêles « une pour vous, une à offrir », boîte cadeau | `[DÉDUIT]` (relevé fin novembre ; bloc « coffret ruban rouge » déjà dans les visuels) |
| **Oublié — Le déçu de l'inox / de la prise en main** | « il est très difficile de maîtriser la poêle pour ne pas que les aliments accrochent » (Dorian, Trustpilot) | A déjà acheté | Ne sait pas préchauffer | Mode d'emploi / « comment bien la culotter et la préchauffer » (rétention, email) | `[AVIS]` |

## 7. Verbatims clients (avis)

> Recopiés tels quels. Un verbatim santé n'est **jamais** un claim. Les avis de la page n'ont pas de source vérifiable (aucune app d'avis) : à traiter comme « avis affichés par la marque ».

**Sur la page — mini-avis sous le bouton** `[PAGE]`
- « Mes petits-enfants mangent enfin sainement. C'est tellement rassurant de pouvoir cuisiner tous leurs plats préférés sans aucun revêtement toxique. » — Monique D.
- « Rien n'accroche ! Je ne pensais pas que c'était possible sans revêtement et pourtant même les œufs se décollent sans le moindre effort. Agréablement surpris. » — Didier B.
- « Solide comme du béton ! J'ai la mienne depuis bientôt cinq ans et je l'utilise presque tous les jours pour ma famille. Elle est toujours dans un état impeccable. » — Aurélie L. (❌ impossible, produit en ligne depuis avril 2026)

**Sur la page — carrousel « Acheteur vérifié »** `[PAGE]`
- « J'ai filmé ma première recette avec cette poêle. J'en pouvais plus de cuisiner avec un truc qui s'écaillait. Maintenant je peux cuisiner sereine et rien n'accroche. Je la recommande à 100% !! » — Véronique S.
- « Premier poulet dans ma nouvelle poêle. J'avoue que j'avais un peu peur que ça accroche sans revêtement mais pas du tout. Même le nettoyage n'a pris que deux minutes. Ravie de mon achat. » — Catherine M.
- « Les poignées qui s'enlèvent c'est tellement pratique. Mes trois poêles prennent la place d'une seule sur mon étagère et moi qui ai une petite cuisine je gagne une place folle. Validé ! » — Martine L.
- « Je l'avais prise pour éviter les fameux revêtements toxiques, mais finalement c'est la qualité de cuisson qui m'a le plus épatée. On sent vraiment une meilleure maîtrise et c'est super satisfaisant. » — Pascale V.
- « C'est moi qui cuisine à la maison depuis que je suis à la retraite et franchement j'aurais dû l'avoir bien avant. Elle chauffe vite et rien n'accroche. On n'utilise plus aucune autre poêle chez nous. » — Gérard P.
- « Je cuisine depuis plus de trente ans et j'ai toujours travaillé avec de l'inox. Quand j'ai vu qu'elle saisissait mieux que mes vieilles poêles de métier j'étais sidéré. Le titane, c'est du sérieux. » — Jean-Marc D.
- « Ça va faire bientôt 6 ans que je cuisine presque tous les jours avec mes poêles Titanox, et toujours pas une griffe en vue. Clairement le meilleur investissement que j'ai pu faire pour ma cuisine. » — Antonio D. (❌ impossible)
- « Ma spécialité c'est les boulettes de viande. Avec mes anciennes poêles ça collait et je devais toujours gratter le fond. Sur cette poêle ça glisse tout seul et la cuisson est toujours parfaite. » — Éléna R.
- « Quand j'ai compris à quel point certaines poêles pouvaient être nocives pour la santé de mes enfants, j'ai décidé de m'équiper d'une poêle réellement saine et fiable pour ma famille. » — Élodie B.

**Sur la page — « AVIS CLIENTS » (Trustpilot affiché)** `[PAGE]`
- « Je cuisine plus sereinement — Je ne suis pas du genre à me prendre la tête, mais là ça m'a marqué. Avant, je cuisinais sans vraiment réfléchir à la surface… maintenant je fais attention. C'est devenu automatique, et honnêtement ça change tout dans ma façon de voir la cuisine. Mille merci!! » — Nathalie P.
- « Je ne pouvais plus ignorer ce que mes enfants inhalaient. — Quand j'ai compris que mon ancienne poêle libérait des PFAS dans leurs assiettes chaque soir, j'ai eu honte. La Titanox, c'est ma façon de les protéger. Maintenant je cuisine sans me poser de questions. » — Sonia M.
- « La seule poêle qui tient ses promesses. — J'ai tout essayé — fonte, inox, céramique. Rien ne tient dans le temps. La Titanox, ça fait 8 mois, zéro rayure, zéro accroche. Le saumon se détache tout seul. C'est une autre catégorie. » — Yanis B. (⚠️ 8 mois = avant la mise en ligne du 04/04/2026 si l'avis date de novembre)
- « Moins de prise de tête — Je cuisine vite fait en rentrant du taf, et ça me saoulait que ça colle ou que ça brûle. Là c'est propre, rapide, efficace. J'ai gagné du temps et moins de prise de tête. » — Sabrina T.
- « Simple, rapide, sans stress. — Honnêtement, ça m'a réconcilié avec la cuisine. C'est facile à utiliser, ça ne colle presque pas, et je n'ai pas besoin de réfléchir à chaque geste. » — Camille F.
- « On sent la différence — J'ai testé pas mal de poêles, et celle-ci est vraiment différente. La cuisson est plus régulière, plus propre, et surtout je sens mieux la maîtrise. Rien à voir avec les poêles revêtues. » — Elodie J.
- « Enfin une poêle qui tient — Je ne suis pas chef, je veux juste cuisiner sans prise de tête. La Titanox fait exactement ça. Et en bonus, plus de produits chimiques dans mes plats. C'est tout ce dont j'avais besoin. » — Amélie L.
- « On parle de ce qu'on mange, jamais de ce avec quoi on cuisine. — C'est le truc que personne ne dit. J'ai mis des mois à réaliser que ma poêle antiadhésive était un problème. Depuis la Titanox, je cuisine sans m'inquiéter. C'est libérateur. » — Hugo D.

**Trustpilot réel** — https://fr.trustpilot.com/review/titanoxfrance.com (relevé 22/11/2026) `[AVIS]`
- Profil « Titanoxfrance Avis », **non revendiqué**, **TrustScore 3,7**, **391 avis** (12 derniers mois) ; 5★ 55 %, 4★ 12 %, 3★ 3 %, 2★ 3 %, **1★ 27 %**. Trustpilot indique que l'entreprise n'invite pas ses clients à laisser un avis.
- « Bonjour, je suis très déçue des produits titanox » — Agnès, 20/11/2026, 1★
- « la poêle a accroché immédiatement, et les aliments ont carrément brûlé » — 13/11/2026, 1★
- « A fuir,les poêles accrochent ....impossible de se faire rembourser » — Jacques, 19/11/2026, 1★
- « Revêtement extrêmement adhésif, très compliqué à nettoyer. » — Grégory, 18/11/2026, 1★
- « Malgré les dires, il est très difficile de maîtriser la poêle pour ne pas que les aliments accrochent » — Dorian, 09/11/2026, 3★
- « EXCELLENT PRODUIT !!!QUALITE IRREPROCHABLE!!!JE RECOMMANDE » — Jean-Baptiste, 15/11/2026, 5★
- « La poêle est de très bonne qualité » — Tonio, 12/11/2026, 5★
- « Cuisson facile, utilisation très agreable » — Genevieve, 03/11/2026, 5★

Objections réelles qui ressortent : **ça accroche**, **difficile à maîtriser**, **remboursement refusé**. Elles contredisent les promesses « rien n'accroche, jamais » et « satisfait ou remboursé ».

## 8. Direction artistique

- **Couleurs** (hex lus dans le CSS calculé) :
  - principale `#0c3358` (boutons « AJOUTER AU PANIER », « JE PROFITE », « JE COMMANDE ») · secondaire `#144a79` (badges « MEILLEURE VENTE », « 7 RAISONS ») · bleu nuit `#03213e` (badge « LE PLUS CHOISI ») · section problème `#1a2b4d`
  - accent urgence `#e11b22` (« Plus que 4 ») / `#b22222` sur `#ffdede` (« STOCK FAIBLE ! ») / `#c95343` (« OFFRE LIMITÉE ») · accent économie `#1d7a3a` (« Économisez ») / `#004d00` sur `#e0ffd8` (« 30J ») · prix barré `#7a828c`
  - fond `#ffffff` · fond paliers `#f4f5f7` · fond guide des tailles `#f5f4f0` · barre d'annonce `#111315` · footer `#010101`
  - texte `#010101` (titres et corps), `#151515` (note)
- **Polices** : Poppins (corps 15 px, titres 700) et sa copie locale « TNX Poppins » ; « Sofia Sans » 800-900 (étiquettes de sections, CTA bas de page) ; « TNX Inter » (badge du guide) ; « TNX Montserrat » (présente).
- **Ambiance** : sérieux, rassurant, médical-propre (bleu marine + blanc + acier).
- **Style des visuels** : packshots acier sur fond noir dégradé ou blanc ; infographies comparatives « POÊLES CLASSIQUES (rouge) vs TITANOX (bleu) » ; badges médaille dorés ; coupe technique en couches ; portraits « clients » ; vidéos UGC verticales (cuisson œufs, viande) ; bandeau de logos médias.

## 9. Synthèse réglementaire

| Repère | Nombre | Les plus importants |
|---|---|---|
| ❌ à éviter | 35 textes (T) + 17 claims (S) | 1) « 100 % titane pur » contredit par le site lui-même (noyau alu + base inox) · 2) Prix barrés et urgences fabriqués (120 € jamais pratiqué, -60 %/-70 % faux, minuteur qui se relance, stock « 4 » fixe, « 15 ans », valeurs de cadeaux gonflées) · 3) Preuves sociales et garanties fausses (Trustpilot 4,8 affiché contre 3,7 réel, avis « 5-6 ans », « Élu poêle santé », logos médias, CE, garantie à vie contre 30 jours, remboursement refusé sur promo) |
| ⚠️ à prouver / nuancer | 26 textes + 8 claims | « sans PFAS » (rapport de labo), contact alimentaire (déclaration de conformité 1935/2004), durabilité « 25 ans » (2024/825), « 3x moins d'huile », « -75 % de contact », brevet, 260 °C / 548 °C, délais et service client incohérents |
| ✅ OK | 9 textes (T18, T25 et T28 portent deux repères, comptés dans chaque colonne) | Tailles et guide des tailles, manche amovible / empilable, compatibilité plaques (si testée), « Tout finit par coller » (constat), suivi de commande, moyens de paiement, CTA |

Autres points de structure :
- **Pages légales** : mentions sans SIREN / RCS / capital / directeur de publication (LCEN art. 6) ; CGV = modèle Shopify sans droit de rétractation de 14 jours ni garantie légale de conformité (info précontractuelle L221-5) ; fabricant ou responsable UE non identifié (GPSR 2023/988).
- **Page Meta « Bien Manger Magazine »** (1194227740437833) qui pousse titanoxfrance.com : nom de média utilisé pour une pub de marque, risque de faux média (annexe I pt 11) et de refus Meta. Propriétaire **[À VÉRIFIER]**.
- **Meta** : les pubs santé et peur (« PFAS classés cancérigènes », « Vous empoisonnez votre famille », « Retrouvez une santé… ») sont déjà **restreintes** sur une partie des audiences. Le compte s'expose à des refus en série.
- **Image « fondateur »** générée par IA (texte incohérent sur l'étiquette) présentée comme réelle.

> Repères, pas un avis juridique. Produit au **contact alimentaire** avec des allégations de santé : faire valider les claims et la composition par un professionnel (juriste conso + déclaration de conformité du fournisseur).

## 10. Propositions de karim

> Propositions seulement. En mode « mon site », rien n'est réécrit dans `PRODUIT.md` sans ta décision : je reprends tout à l'identique avec les repères, sauf ce que tu choisis de changer.

**Angles** (3 à 5) :
1. **« J'étais sûre que ça allait coller »** (sceptique convaincue) — persona P1/P4. Preuve : 16 cartes actives depuis le 16/10, non restreintes ; verbatims Didier B., Catherine M. → **garder tel quel**. C'est aussi la réponse directe à l'objection n° 1 de Trustpilot.
2. **« Neuf poêles en douze ans » / coût sur la durée** — persona P2. Preuve : 16 cartes depuis le 16/10 (« 800 euros… 20 ans »), non restreint → **garder**, en alignant un seul calcul (la page dit 149,95 € puis 1 000 € sur 10 ans, la pub 800 € sur 20 ans).
3. **« Céramique, inox, titane : le vrai match »** — persona P3. Preuve : 9 cartes depuis le 16/10, non restreint → **adapter** : garder la structure, mais « 100 % titane pur certifié » doit coller à la vraie composition (couche titane sur noyau alu / base inox).
4. **« Regardez le fond de votre poêle »** (rayures) — persona P1. Preuve : 7 cartes depuis le 17/10, non restreint → **garder**. C'est la version de l'angle PFAS qui passe chez Meta, alors que « PFAS classés cancérigènes » est restreint.
5. **Nouveau : petite cuisine / manches amovibles empilables + cadeau de Noël** — personas oubliés. Preuve : verbatim Martine L. ; aucune pub ne l'exploite ; saison de fin d'année → **nouveau** (Set 2 « une pour vous, une à offrir »).

**Prix et offre** :
- Prix unitaires 59,99 / 64,99 / 69,99 € : **garder** (déjà en ,99 ; marché vu : titanoxtitanepur.com à 66 / 72 / 77 €).
- Packs 99,98 € et 134,97 € : hors règle maison (,95 / ,99). Proposition : **99,99 €** (2 poêles) et **134,99 €** ou **129,99 €** (3 poêles). À calculer à 3,5 × le coût fournisseur minimum (**coût [À VÉRIFIER]**).
- Prix barrés : en l'état, **non conformes Omnibus** et pourcentages faux. Trois options : (a) garder tel quel (risque DGCCRF, tu décides) ; (b) afficher les **vrais** pourcentages (-50 %, -58 %, -62 %) avec une référence réellement pratiquée 30 jours ; (c) remplacer le barré par une économie de pack (« 2e poêle à 39,99 € »). Le test Intelligems déjà en cours (« retirer le prix barré du palier 1x ») va dans le sens de (c).
- Urgence : proposer de couper le minuteur qui se relance et le « 4 » fixe ; garder « OFFRE DE SAISON » seulement avec une vraie date de fin.
- Garantie : choisir **une** promesse écrite et cohérente partout (la page dit « à vie », « 25 ans » et « 30 jours »), plus la mention de la garantie légale de 2 ans et des 14 jours de rétractation.

**Palette** :
- **Par défaut, celle de la source** : principale `#0c3358` · secondaire `#144a79` · accent `#e11b22` (urgence) / `#1d7a3a` (économie) · fond `#ffffff` · texte `#010101`.
- **Option différenciante « titane chaud »** (cuisine artisanale, moins « labo ») : principale `#2B3A42` (graphite) · secondaire `#8A9BA8` (titane) · accent `#C8742E` (cuivre, saisie) · fond `#F6F3EE` (crème) · texte `#1A1A1A`.

**Packshots à produire** (à partir des photos du vrai produit uniquement ; les 11 images HD sont dans `images/`) :
1. Fond blanc 1:1, 3/4 avant, pour chaque taille (26 / 28 / 30 cm).
2. Situation : œuf au plat qui glisse (démo anti-adhérence réelle).
3. Situation : steak saisi, sur induction.
4. Situation : 3 poêles empilées, manches retirés, dans un petit placard.
5. Détail matière : macro du martelage + tranche visible (pour montrer honnêtement les couches).
6. Échelle : poêle tenue à la main au-dessus d'une plaque.
7. Contenu du colis : boîte noire TITANOX ouverte, poêle, manche, notice (contenu réel à confirmer).

**Questions pour toi** :
1. **Mode** : c'est bien ta boutique (reprise à l'identique) ? Tu as écrit « concurrent » dans ta demande.
2. **Composition réelle** : titane massif ou couche de titane sur noyau aluminium et base inox (comme le montre ton infographie `images/08.png`) ? Grade du titane, épaisseur de chaque couche ?
3. **Preuves** : as-tu la déclaration de conformité contact alimentaire (règl. 1935/2004) et un rapport de labo « sans PFAS » du fournisseur ?
4. **Prix de référence** : la poêle a-t-elle déjà été vendue 120 € ? Quel est le coût fournisseur (pour calculer les packs) ?
5. **Stock** : le « Plus que 4 poêles » est-il relié à l'inventaire ou écrit à la main ?
6. **Preuves sociales** : nombre réel de commandes (100 000 ? 46 842 ?) ; d'où viennent les avis affichés (4,8 / 3 214) ; y a-t-il eu de vraies parutions dans marmiton, Cuisine Actuelle, Santé Magazine, Cuisine et Vins de France ; d'où vient « Élu poêle santé 2026 » ?
7. **« 15 ans » / fondateur** : la marque a-t-elle 15 ans ? La photo du fondateur est-elle réelle ?
8. **Garantie et retours** : quelle est la vraie garantie (à vie, 25 ans, 30 jours) ? Veux-tu garder la politique « promo = non remboursable » (non conforme) ?
9. **Four** : 260 °C ou 548 °C ? Le manche chauffe-t-il au four ?
10. **Pages Meta** : « Titanox » 1495731186949867 (→ titanoxtitanepur.com) et « Bien Manger Magazine » 1194227740437833 (→ titanoxfrance.com) sont-elles à toi ?
11. **Fabricant** : nom, pays de fabrication, responsable UE (GPSR), poids et dimensions exacts, contenu du colis.
