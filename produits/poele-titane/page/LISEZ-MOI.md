# Page produit poêle Titanixxx — reproduction de la page Titanox (2026-11-22)

**Rien n'est en ligne.** Aucun connecteur Shopify n'était disponible pendant cette mission : pas de thème
dupliqué, pas de produit créé. Tout est prêt à importer, en fichiers.

## Contenu du dossier
- `theme/sections/` : 9 sections OS 2.0 (`ttx-annonce`, `ttx-produit`, `ttx-videos`, `ttx-avis`, `ttx-raisons`,
  `ttx-probleme`, `ttx-rappel-offre`, `ttx-faq`, `ttx-reassurance`)
- `theme/snippets/` : `ttx-head`, `ttx-offre`, `ttx-avis-carte`, `ttx-avis-source`, `ttx-emplacement`
- `theme/assets/` : `ttx-base.css`, `ttx-base.js`
- `theme/templates/product.titanixxx-poele.json` : la page (10 sections, tous les textes)
- `produit-brouillon.json` : le produit à créer en brouillon (2 variantes 59,99 € / 99,98 €, sans prix barré ; lot vendu via Rapid Bundle, 10 € de remise par poêle)
- `outils/gabarit.py` (régénère le gabarit) · `outils/apercu.py` (aperçu local du vrai Liquid)
- `preview/index.html` : aperçu local · `captures/` : captures 390 / 1440 et planches source | nous

## Import (à faire avec le connecteur Shopify, jamais sur le thème publié)
1. Dupliquer le thème publié, nommer la copie « BROUILLON poêle titane 2026-11-22 » (rôle UNPUBLISHED).
2. Écrire sur la copie les fichiers `theme/` (sections, snippets, assets, template), en TEXT.
3. Téléverser dans Contenu > Fichiers les 3 images listées dans `produit-brouillon.json` (mêmes noms de fichier,
   le gabarit y fait référence en `shopify://shop_images/…`).
4. Créer le produit en DRAFT d'après `produit-brouillon.json`, médias dans l'ordre indiqué, `templateSuffix`
   `titanixxx-poele`, stock renseigné (quantité réelle à fournir).
5. Préversion : `https://<boutique>/products/<handle>?preview_theme_id=<id de la copie>` et vérifier
   `window.Shopify.theme` (id de la copie, rôle unpublished) avant toute conclusion.
6. Avant publication : décocher « Afficher les emplacements vides » (sections Produit, Vidéos, Raisons) ou les
   remplir ; compléter « Comment ces avis sont collectés ».

## Choix techniques
- Paliers d'offre = **variantes** du produit (1 poêle / Lot de 2). Le prix affiché est lu sur la variante,
  l'économie (20,00 €, -16 %) est calculée, jamais écrite à la main. Sélection par boutons radio, sans JS.
  Alternative : l'app de bundles (bloc d'app accepté dans la section produit). Choix à faire.
- Le bouton poste vers `/cart/add` (redirection vers le panier). Le tiroir panier AJAX du thème n'est pas branché.
- Barre d'achat collante sur mobile : **absente de la source**, ajoutée pour avoir le bouton d'achat au
  premier écran (désactivable dans la section).
- Polices Poppins et Sofia Sans chargées depuis Google Fonts (RGPD : prévoir l'auto-hébergement ou les polices du thème).
- Le bandeau défilant est une section du gabarit (sous l'en-tête), pas la barre d'annonce globale du thème.
