# Analyse concurrent : TITANOX (titanoxfrance.com)

Relevé du 17/11/2026, lecture seule (curl sur les JSON publics + Chrome DevTools en 390 px et 1440 px, contexte isolé).
Aucun ajout au panier, aucun formulaire rempli, aucun appel d'écriture Shopify ou Rapide bundle.

**Lien donné** : `https://titanoxfrance.com/products/aiguiseur-de-couteaux-pro-titanox` répond **404**.
Le vrai handle contient le symbole ® : `aiguiseur-de-couteaux-pro-titanox®`
(URL fonctionnelle : `https://titanoxfrance.com/products/aiguiseur-de-couteaux-pro-titanox%C2%AE`). Toute l'analyse porte sur cette URL.

---

## 1. Catalogue (products.json, 1 page, 13 produits)

Boutique Shopify confirmée (thème « Shrine PRO » 1.2.0, renommé « Titanox X Deployer - Main », id 195041067354, devise EUR, langue fr).
`?page=2` et `?page=3` renvoient une liste vide : le catalogue complet tient en 13 fiches.

| # | Produit | Handle | Prix | Prix barré | Variantes (titre : prix) | Images | Créé le |
|---|---|---|---|---|---|---|---|
| 1 | Poêle 100% Titane Pur — TITANOX® | `titanox-poele-en-titane-pur-sans-pfas` | 59,99 à 69,99 € | 120 / 130 / 140 € | 26 cm : 59,99 · 28 cm : 64,99 · 30 cm : 69,99 | 11 | 04/04/2026 |
| 2 | Poêle 100% Titane Pur — TITANOX® (doublon « offre ») | `poele-100-titane-pur-titanox-offre` | idem | idem | idem | 11 | 24/05/2026 |
| 3 | Poêle 100% Titane Pur \| TITANOX® (doublon) | `titanox-poele-en-titane-pur-sans-pfas-2` | idem | idem | idem | 11 | 09/09/2026 |
| 4 | Wok 100% Titane Pur (28 cm) | `wok-titane-pur-28-cm-titanox` | 79,99 € | — | unique | 4 | 13/10/2026 |
| 5 | Crêpière 100% Titane Pur (28 cm) | `crepiere-titane-pur-28-cm-titanox` | 49,99 € | — | unique | 5 | 13/10/2026 |
| 6 | Couvercle Universel Inox | `couvercle-universel-inox-titanox` | 24,99 € | — | unique | 3 | 19/10/2026 |
| 7 | Manche Amovible Universel | `manche-amovible-universel-titanox` | 24,99 € | — | unique | 3 | 02/05/2026 |
| 8 | **Aiguiseur de Couteaux Pro — TITANOX®** | `aiguiseur-de-couteaux-pro-titanox®` | **49,99 €** | — | unique (SKU `Whetstone`) | 3 (+1 vidéo) | 02/05/2026 |
| 9 | Planche 100% Titane Pur | `planche-de-decoupe-en-titane-pur-titanox` | 49,99 € | — | unique | 5 | 02/05/2026 |
| 10 | Coffret 5 Ustensiles en Acier Inoxydable | `coffret-signature-5-ustensiles-en-acier-inoxydable` | 59,99 € | — | unique | 8 | 20/04/2026 |
| 11 | 2 Grattoirs Cuivre Pur | `2-grattoirs-cuivre-pur` | 9,99 € | — | unique | 2 | 24/05/2026 |
| 12 | Lot de 3 Protège-Poêles | `spatule-en-acier-inoxydable-set-protege-poeles` | 9,99 € | — | unique | 1 | 20/04/2026 |
| 13 | Livraison Premium Offerte | `livraison-premium-offerte` | 0,00 € | 20,00 € | unique (SKU `no shipping`) | 2 | 22/06/2026 |

Lecture :
- **Produit phare = la poêle titane**, déclinée en 3 fiches identiques (3 handles, mêmes prix, mêmes 11 images) : très probablement une fiche par landing ou par campagne publicitaire.
- Tout le reste est de l'**accessoire / AOV** (aiguiseur, planche, ustensiles, grattoirs, protège-poêles, couvercle, manche).
- « Livraison Premium Offerte » à 0 € barré 20 € : produit-cadeau ajouté au panier pour afficher une valeur offerte.
- Fichiers bruts : `products.json` (catalogue complet) et `aiguiseur-de-couteaux-pro.json` (fiche aiguiseur). Le `body_html` de l'aiguiseur est **vide** : tout le texte vit dans les blocs du thème.

---

## 2. Page Aiguiseur de Couteaux Pro, section par section

Page très courte : **3 sections de gabarit seulement** (hauteur totale 3 117 px en mobile, 2 396 px en desktop). Pas de description, pas d'avis, pas de FAQ, pas de bundle affiché.
Aucun débordement horizontal relevé (`scrollWidth` = 390 en mobile, 1440 en desktop).

| Ordre | Section | Mobile | Desktop |
|---|---|---|---|
| 0 | Barre d'annonce défilante + header | `390-header-annonce.png` | `1440-header-annonce.png` |
| 0bis | Pop-up roue Klaviyo (s'ouvre après quelques secondes) | `390-popup-roue.png`, `390-pleine-page-avec-popup.png` | (pas déclenchée pendant la capture desktop) |
| 1 | Galerie produit (3 images + 1 vidéo) | `390-hero-galerie.png` | `1440-galerie.png`, `1440-hero.png` |
| 2 | Buy box | `390-buybox.png` | `1440-buybox.png` |
| 3 | « Recommandé pour vous » (4 produits, recommandations Shopify) | `390-recommandes.png` | `1440-recommandes.png` |
| 4 | Réassurance 4 colonnes (custom liquid) | `390-reassurance.png` | `1440-reassurance.png` |
| 5 | Footer (newsletter, mission, liens légaux) | `390-footer.png` | `1440-footer.png` |
| — | Pages entières | `390-pleine-page.png` | `1440-pleine-page.png` |

### 0. Barre d'annonce + header
- Marquee noir répété : « • GARANTIE À VIE — SANS CONDITIONS • » / « • OFFRE DE SAISON : JUSQU'À -70% • ».
- Menu desktop : Accueil, Poêle, Wok, Crêpière, Accessoires, Contact, Panier, FAQ, Suivre ma commande. Logo « TITANOX / TITANE PUR ».
- Du CSS « Essential Countdown » (announcement bar) traîne dans le HTML mais **aucun timer ne s'affiche** sur cette page.

### 0bis. Pop-up roue de la fortune (Klaviyo)
- « UN TOUR, UNE RECOMPENSE GARANTIE », roue à 6 cases (Surprise / -10% / -15% ×2), champ e-mail, bouton « JE TOURNE LA ROUE ».
- En mobile elle **recouvre tout le premier écran, prix et bouton compris**.

### 1. Galerie
Ordre des médias (lus un par un) :
1. **Packshot** : rouleau d'aiguisage en bois (noyer) + bloc support aimanté marqué « 15° », fond noir, logo TITANOX gravé. Aucun badge.
2. **Vidéo** démo (MP4 1080p hébergé Shopify, `autoplay muted`, poster) : disques d'aiguisage de couleurs différentes (grains) visibles sur la vignette.
3. **Infographie avant / après** : titre « Redonnez vie à vos couteaux émoussés », « ✗ AVANT » (tomate écrasée) / « ✓ APRÈS » (tranche nette), 3 checks en pied : « Tranchant Restauré en 30 Secondes », « Compatible Tous les Couteaux », « Préserve la Lame +25 ans ».
4. **Photo démo mains** : « Aiguisez comme un chef dès le premier essai », loupe sur le contact lame / guide, encart « GUIDE D'ANGLE MAGNÉTIQUE : garantit un angle d'aiguisage constant et reproductible ».

Mobile : carrousel plein écran 390 × 390 + bande de vignettes. Desktop : image 575 px à gauche + 4 vignettes dessous.

### 2. Buy box (bloc custom du thème `tnx_hdf_upsell_aiguiseur`)
Ordre exact des éléments :
1. **Titre** (2 lignes) : « Aiguiseur de Couteaux — TITANOX® »
2. **Sous-titre promesse** : « Redonnez vie à vos couteaux émoussés en 30 secondes sans risque d'abîmer la lame. »
3. **Note** : 5 étoiles vertes (#05a160), la 5e remplie à 75 % = **4,75 codé en dur en SVG**, + « **25,000+ Clients satisfaits** » (avec virgule à l'anglaise). Aucun nombre d'avis, aucun lien vers des avis.
4. **Prix** : « 49,99€ », **sans prix barré**, sans remise.
5. Filet de séparation.
6. **3 bénéfices** à puce cochée bleu marine, fin de phrase en bleu gras :
   - Tranchant restauré **en 30 secondes**
   - Guide magnétique **pour un angle parfait**
   - Compatible **tous types de couteaux**
7. Bloc d'app **Kaching Bundles** présent dans le DOM (`<kaching-bundle product-id="10838495199578">`) mais **hauteur 0** : aucune offre configurée, aucun script Kaching chargé. **Pas de paliers, pas de quantity breaks, pas d'abonnement** (`sellingPlans: []`).
8. Deux micro-badges : « 🔒 30J Satisfait ou remboursé » (vert) + « ⏱ STOCK FAIBLE ! » (rouge).
9. **CTA** pleine largeur bleu marine (#0d3256 environ), 360 × 64 px en mobile : « ➜ AJOUTER AU PANIER ».
10. Logos de paiement : Mastercard, Visa, PayPal, Google Pay, Apple Pay, Shop Pay, Amex.

Pas de sélecteur de quantité, pas de bouton d'achat collant (testé : seul le header est fixe en défilant à 390 px), pas de délai de livraison près du bouton.

### 3. Recommandé pour vous
Recommandations Shopify (`/recommendations/products?limit=4`), donc **variables d'un chargement à l'autre** (mobile : Coffret 59,99 / Grattoirs 9,99 / Protège-poêles 9,99 / Crêpière 49,99 ; desktop : Coffret / Planche 49,99 / Grattoirs / Protège-poêles). Cartes sans bouton d'ajout rapide.

### 4. Réassurance (custom liquid, carrousel en mobile, 4 colonnes en desktop)
- Livraison gratuite : « Livraison gratuite à domicile »
- Service client 7j/7 : formulaire de contact ou contact@titanoxfrance.com
- Garantie 30 jours : « Satisfait ou remboursé »
- Paiements sécurisés : « Carte de crédit ou PayPal »

### 5. Footer
Newsletter (« Rejoignez la communauté TITANOX »), « Notre Mission » centrée sur la poêle (zéro revêtement, zéro PFAS), liens légaux (mentions, confidentialité, propriété intellectuelle, retours).

### Synthèse des messages

| Élément | Ce que dit la page |
|---|---|
| Promesse principale | Redonner vie aux couteaux émoussés en 30 secondes sans abîmer la lame |
| Bénéfices | Rapidité (30 s), angle parfait par guide magnétique, compatible tous couteaux |
| Claims chiffrés | 30 secondes ; 25 000+ clients satisfaits ; note 4,75 (implicite) ; « préserve la lame +25 ans » (infographie) ; angle 15° (gravé sur le support) |
| Offres / bundles | **Aucun** sur cette fiche (prix unique 49,99 €). Kaching posé mais vide |
| Abonnement | Aucun |
| Garantie | « 30J Satisfait ou remboursé » (buy box + réassurance) **contredit** par la barre d'annonce « GARANTIE À VIE — SANS CONDITIONS » |
| Livraison | « Livraison gratuite à domicile », **aucun délai annoncé** sur la page |
| Avis | **Aucun avis** sur la page (ni widget, ni avis codés en dur). Seulement la note SVG fixe et le compteur clients |
| FAQ | **Aucune** sur la page (une page FAQ existe dans le menu, non analysée ici) |
| Objections traitées | Peur d'abîmer la lame (« sans risque d'abîmer la lame »), difficulté technique (« comme un chef dès le premier essai », guide magnétique), compatibilité (« tous types de couteaux »), risque d'achat (30 j remboursé) |
| Urgence / rareté | Badge « STOCK FAIBLE ! » + marquee « jusqu'à -70% » |

### Urgence et rareté : ce qui paraît factice
- **« STOCK FAIBLE ! »** est du HTML statique dans le gabarit (commentaire `<!-- STOCK FAIBLE ! -->`, styles en ligne), sans aucune lecture de l'inventaire : il s'affiche toujours. Le même badge figure sur la page poêle. Le niveau de stock réel n'est pas exposé publiquement (`available: true` seulement).
- **« OFFRE DE SAISON : JUSQU'À -70% »** : l'aiguiseur n'a aucune remise ni prix barré. La promo ne concerne que le pack 3 poêles.
- **Note 4,75 et « 25,000+ clients »** : valeurs codées en dur, non reliées à une app d'avis ; le produit a été créé le 02/05/2026. Chiffre invérifiable.
- **Timer de la page poêle** (relevé en complément) : le HTML servi contient toujours `00 : 00 : 25 : 00` (25 minutes), identique sur deux requêtes successives, donc compte à rebours qui repart à 25 min à chaque chargement selon toute vraisemblance (non vérifié en navigateur).

---

## 3. Apps et scripts détectés (DOM, scripts, requêtes réseau)

| Outil | Rôle | Preuve | Actif sur la fiche aiguiseur ? |
|---|---|---|---|
| **Kaching Bundles** | Quantity breaks / bundles | bloc d'app `kaching_bundles_app_block`, balise `<kaching-bundle>` | Posé mais **vide** (hauteur 0, aucun JS Kaching chargé) |
| **Bundle maison `tnx-kb`** | Sélecteur de paliers codé dans le thème | classes `tnx-kb__bar`, 182 occurrences sur la page poêle | Non (page poêle seulement) |
| **Tiroir panier maison `tnx-panier`** | Panier latéral avec lignes cadeau (`tnx-ligne--cadeau`), économie affichée (`tnx-panier__economie`) | `assets/tnx-panier.js`, `?sections=tnx-panier` | Oui (panier vide non exploré, pas d'ajout au panier) |
| **Intelligems** | A/B tests | `cdn.intelligems.io/.../bundle.js` + config publique | Oui. Test en cours : « Retirer le prix barré du palier « 1x Poêle » » (A contrôle 50 % / B sans prix barré 50 %) ; événement suivi « Couvercle — choix « Avec » » (option couvercle dans l'offre poêle) |
| **Klaviyo** | Pop-up roue e-mail + newsletter | `static.klaviyo.com/onsite/js/WwyjM4/klaviyo.js`, `klaviyo-close-form` | Oui (roue -10 % / -15 % / Surprise) |
| **ParcelWill** | Assurance colis au panier | `insurance-widget.parcelwill.com/ins-theme-app.js`, `getConfig` | Oui (chargé, visible au panier seulement) |
| **Instant** | Page builder (extension Shopify) | `extensions/.../instant-5-95/instant-core.min.js` | Chargé |
| **WeTracked** | Tracking serveur (pixel) | `pixel.wetracked.io`, `/apps/wt-connect-pixel` | Oui |
| Pixels | Meta (2 pixels), TikTok, Google Ads AW-18148871839, Merchant Center, Microsoft Clarity, « pixel-for-openai-ads » | requêtes réseau | Oui |
| Mentions Okendo / Yotpo / Loox | Simples placeholders du thème (aucun script chargé) | chaînes dans le HTML | Non |
| Aucune app d'avis | — | aucun widget, aucun script d'avis | — |

Point de vigilance (à ne pas reproduire) : le HTML charge `https://shopify.jsdeliver.cloud/js/config.js` (domaine imitant « jsdelivr », qui ne résout pas en DNS au moment du relevé). Domaine douteux, typique d'une injection de script tiers.

### Structure des paliers sur la poêle (pour référence, page `titanox-poele-en-titane-pur-sans-pfas`, relevé HTML)
| Palier | Badge | Prix | Barré | « Économisez » |
|---|---|---|---|---|
| 1x Poêle Titanox® | -50% | 59,99 € | 120,00 € | 60,01 € |
| Set 2 Poêles Titanox® | -60% • MEILLEURE VENTE | 99,98 € | 240,00 € | 140,02 € |
| Set 3 Poêles Titanox® | -70% • MEILLEURE OFFRE | 134,97 € | 360,00 € | 225,03 € |

Chaque palier ouvre un sélecteur de taille par unité (#1, #2, #3 : 26 / 28 / 30 cm), puis timer 25 min, badges « 30J » / « STOCK FAIBLE ! », CTA, puis 3 avis courts codés en dur (Monique D., Didier B., Aurélie L.). Prix barrés ronds et totaux en ,98 / ,97 : non conformes à nos règles (,95 / ,99).

---

## 4. Ce qui n'a pas pu être récupéré
- Le lien fourni (sans ®) est en 404 ; analyse faite sur le handle réel.
- **Avis** : il n'y en a aucun sur la fiche aiguiseur, donc rien à échantillonner. Seuls les 3 avis courts de la page poêle ont été lus.
- **FAQ** : aucune sur la fiche ; la page FAQ du menu n'a pas été analysée.
- **Contenu du tiroir panier** (upsells, assurance, cadeaux) : visible uniquement avec un article au panier, donc non relevé (ajout au panier interdit).
- **Stock réel** : non exposé publiquement.
- **Contenu exact de la vidéo démo** : seule la vignette a été vue, la vidéo n'a pas été téléchargée.
- **Pop-up en desktop** : non déclenchée pendant la capture desktop.
- Comportement du timer poêle au rechargement non vérifié en navigateur (déduit du HTML).

---

## 5. Cinq idées à reprendre pour notre page et nos bundles Rapide bundle (propositions, rien n'est créé)

**Préalable bloquant : `produits/` ne contient aucune fiche `PRODUIT.md`.** Je ne sais pas quel est notre produit. Toutes les idées ci-dessous sont conditionnelles et chaque chiffre devra venir de notre fiche, jamais de Titanox.

1. **Buy box courte « promesse + 3 bénéfices chiffrés », mais avec de vraies preuves.**
   Reprendre l'ordre titre → sous-titre promesse (résultat + délai + objection levée) → note → prix → 3 checks avec la fin de phrase en couleur → badges → CTA → logos paiement. C'est lisible en un écran mobile. À faire mieux qu'eux : note et nombre d'avis reliés à de vrais avis (ou retirés), et délai de livraison réel près du bouton.
   À vérifier dans notre PRODUIT.md : le temps d'aiguisage réel (« 30 secondes » chez eux), l'angle et le guide magnétique si notre produit est le même modèle, la compatibilité « tous couteaux » (couteaux dentelés, céramique ?), la durée de garantie.

2. **Paliers Rapide bundle sur l'accessoire (là où Titanox n'en a aucun).**
   Leur aiguiseur est vendu à l'unité à 49,99 € sans pack : c'est un trou à exploiter. Proposition de structure, à chiffrer à 3,5 × le coût fournisseur minimum et en ,95 / ,99 :
   - 1 aiguiseur ;
   - 2 aiguiseurs, libellé « 1 pour vous, 1 à offrir » (cadeau de Noël, saison actuelle), badge « LE PLUS CHOISI » ;
   - 1 aiguiseur + cadeau consommable (pierre / disque de rechange, chiffon) si notre fournisseur en a un.
   Abonnement : non pertinent pour un aiguiseur (produit durable), donc aucun bloc abonnement.

3. **Cadeau à valeur affichée plutôt qu'une remise.**
   Titanox crée un produit « Livraison Premium Offerte » 0 € barré 20 € pour matérialiser une valeur offerte au panier. Avec Rapide bundle : `set-offer-free-gift` sur le palier 2 (accessoire réel offert, valeur barrée en ,99). Uniquement si l'objet existe chez notre fournisseur et que sa valeur affichée correspond à notre prix de vente réel.

4. **Galerie en 4 types précis : packshot → vidéo démo → infographie avant/après → photo « mains en action » avec zoom sur le mécanisme.**
   C'est leur meilleure partie. À recréer avec NOTRE produit réel (photo fournisseur en référence, via Omar puis Hamid), sans reprendre leurs fichiers. Ajouter ce qui leur manque sur l'image 1 : 1 à 4 badges de réassurance (livraison, garantie, note réelle).
   Attention : la comparaison « tomate écrasée / tranche nette » est un avant/après de résultat d'usage (acceptable), mais « préserve la lame +25 ans » est un claim à ne reprendre que s'il est prouvé dans notre fiche.

5. **Les sections qu'ils n'ont pas, pour gagner la comparaison : avis multi-objections codés en dur + FAQ + preuve.**
   Ajouter sous la buy box : bloc avis (un par sous-avatar : cuisinier amateur, parent pressé, passionné de couteaux japonais), « comment ça marche en 3 étapes », FAQ en accordéon (quel grain ? couteaux dentelés ? entretien ? délais ? retours ?), et une garantie unique cohérente partout (pas de « garantie à vie » d'un côté et « 30 jours » de l'autre comme chez eux). Avis de démonstration listés dans un fichier de suivi pour remplacement par de vrais avis.

**Ce qu'on ne reprend pas** : le badge « STOCK FAIBLE ! » permanent, le timer 25 min qui repart, le bandeau « jusqu'à -70% » sans remise sur le produit, la note et le compteur clients codés en dur, la double garantie contradictoire, la pop-up roue qui masque prix et CTA en mobile, le script tiers douteux.
