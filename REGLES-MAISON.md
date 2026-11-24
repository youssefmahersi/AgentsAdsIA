# Règles maison (les 4 agents les appliquent toujours)

Ce sont les règles apprises en produisant des centaines de pubs. Tu peux en ajouter, mais n'en retire aucune sans savoir pourquoi elle existe.

## 1. Vérité et produit
- **Fiche produit d'abord.** Les claims, prix, offres, garanties et chiffres viennent de `produits/<produit>/PRODUIT.md`, et de nulle part ailleurs. Aucun chiffre inventé, aucune étude imaginaire.
- **Le vrai produit, toujours.** Chaque image produit part d'une vraie photo du produit. Pas de packaging inventé, pas d'étiquette générée. Contrôle obligatoire avec une planche côte à côte « vrai produit | notre image ». Si le produit a été inventé par l'IA, on bloque et on recommence.
- **Le produit entier dans le cadre**, jamais coupé, jamais déformé.

## 2. Reproduire une pub concurrente
- **À l'identique, plan par plan.** On copie la structure, le rythme, le cadrage, les gestes, le type de hook et la place du produit. Seuls la marque, le produit et le packaging changent.
- **Analyse de la source avant de générer.** Vidéo extraite à 10 images par seconde, découpée au dixième de seconde, voix transcrite. Planche « original | notre image de départ » validée avant la moindre vidéo.
- **Tout est refait en IA.** On ne livre jamais un morceau de la vidéo du concurrent.
- **Personnes = avatars IA.** Chaque personne de la source est remplacée par un avatar IA créé pour l'occasion (planche personnage). On ne copie jamais le visage d'une vraie personne et on ne floute jamais.
- **Aucun logo, marque ou offre du concurrent** ne reste dans l'image.

## 3. Réalisme
- **Humains ultra réalistes** : rendu « photo iPhone », vraie peau, mains justes, lumière naturelle. Zéro aspect IA (peau cireuse, doigts en trop, regards vides). En cas de doute, omar recale.
- **Pubs dynamiques** : hook immédiat (0 à 2 s), un plan toutes les 2,5 à 3 s, aucune répétition, aucune saccade. Un plan raté est coupé, pas « rattrapé ».
- **Caméra** : « locked-off » quand la source est fixe. On écrit noir sur blanc qu'il n'y a ni zoom ni mouvement, sinon le modèle en invente.

## 4. Voix et son
- **Voix naturelles** (ElevenLabs) : une seule prise avec des balises d'émotion, stabilité 3 à 10 %, similarité 91 à 96 %. Jamais de voix accélérée artificiellement.
- **Pas de silences** : 0,35 s maximum entre deux phrases. Un texte court donne une pub plus courte, jamais étirée.
- **Volume** : -14 LUFS à l'export. La musique reste sous la voix.

## 5. Sous-titres (vidéo 9:16)
- Style adulte et propre : Montserrat Bold (~56 px sur 1080 de large), blanc avec contour noir, mot prononcé en jaune `#FFD43B`, 3 à 5 mots par ligne, 2 lignes au plus.
- Toujours **dans la zone sûre** : environ 270 px de marge en haut, 440 px en bas et 80 px sur les côtés, sur une image de 1080 × 1920. Position verticale vers 65 % de la hauteur.
- Jamais sur un visage, jamais sur le produit, jamais sur une pancarte.

## 6. Statics
- **Livraison en 1:1 (1080 × 1080) seulement.**
- Texte exact, lisible sur téléphone (28 px au moins sur 1080), aucune faute.
- Une idée par static. Le titre arrête le scroll et qualifie la cible.

## 7. Prix et offres
- **Jamais de prix rond** : tous les prix finissent en **,95 ou ,99**. Prix barrés, valeurs de cadeaux et totaux de pack compris.
- Un pack se calcule à 3,5 fois le coût fournisseur au minimum.
- Les noms d'offre se reprennent mot pour mot (« 2+1 GRATIS », « Buy 2 Get 1 FREE ») : on n'affadit jamais une offre.
- Sur une page : l'abonnement se place **après** les offres de pack, et il n'est **jamais coché par défaut**.

## 8. Conformité Meta (pour ne pas se faire refuser)
- Pas d'attribut personnel adressé au spectateur : « your » ou « vous » + maladie, médicament, âge, religion, poids. On parle à la 1re personne (« moi, j'ai… ») ou à la 3e personne.
- Pas d'avant / après sur le corps ou la santé, pas de fausse urgence (fausse rupture de stock, compte à rebours bidon).
- Pas de faux média (fausse une de journal, faux logo de chaîne TV).
- Mention « Dramatisation » ou « acteurs IA » en petit quand c'est joué.
- Si une règle force à adoucir le visuel du problème, **on propose la version prudente À CÔTÉ de la version forte**, jamais à la place sans le dire.

## 9. Site Shopify
- On travaille **toujours sur un thème dupliqué non publié**. C'est l'utilisateur qui publie.
- Les avis sont codés en dur dans la section, comme sur la page source (pas d'app d'avis imposée).
- Un seul site pour tous les pays : un changement s'applique partout.
- Contrôle en mobile (390 px) ET en ordinateur (1440 px) : images entières dans leur cadre, rien qui déborde, aucun défilement horizontal.

## 10. Budget et livraison
- **Bon du premier coup** : image de départ validée avant la vidéo, 480p avant 720p, devis annoncé avant toute dépense. Au bout de deux échecs sur le même plan, on change d'approche au lieu de réessayer.
- **On n'envoie que du fini.** Jamais une version qu'on sait non conforme. Le PASS d'omar est obligatoire.
- Chaque livraison va dans `livraisons/<date>/<produit>/<TOFU|MOFU|BOFU>/`, avec un `LISEZ-MOI.md` et le texte de la pub Meta (texte principal, titre, description).
- **Vérifier avant d'affirmer** : un agent ne dit jamais « c'est fait » sans l'avoir contrôlé avec un outil (capture, mesure, lecture du fichier).

## Règles ajoutées

- **(2026-11-21) Mes propres sites ne sont pas des concurrents.** Quand la source est une boutique de l'utilisateur (il le précise à chaque fois ; ne jamais le déduire d'un nom de dossier ou de domaine), on reprend **à l'identique** : textes, claims, prix, offre et images, sans réécrire. On **souligne seulement** (⚠️ à prouver / ❌ à éviter, avec la règle en cause) ce qui pose problème au regard de la réglementation UE ou des règles Meta ; c'est l'utilisateur qui décide de changer. Les règles de la section 2 (rien du concurrent dans l'image) ne s'appliquent qu'aux vrais concurrents.
- **(2026-11-22) Titanox (titanoxfrance.com) est un CONCURRENT**, pas une boutique de l'utilisateur. Tout ce qui est dans `produits/_concurrents/titanox/` (aiguiseur, poêle titane) se traite en mode « concurrent ».
  **Exception : l'utilisateur a un accord avec Titanox qui couvre ses TEXTES** (confirmé le 2026-11-22). On peut reprendre leurs accroches et textes de pub mot pour mot. Ce que l'accord ne couvre pas (ou dont la couverture n'est pas confirmée) reste interdit : leurs images, leur logo, leurs avis, badges et chiffres, et leurs claims, qui doivent toujours être vrais pour notre produit et figurer dans notre `PRODUIT.md`.
- **(2026-11-22) Reprise de texte d'un concurrent : toujours vérifiée.** Avant toute livraison, omar compare chaque titre et chaque texte de pub aux pubs relevées du concurrent (`produits/_concurrents/<source>/pubs/`). Une reprise mot pour mot n'est acceptée que si un accord écrit avec ce concurrent couvre ses textes ; sinon, on reprend l'angle avec nos propres mots.
