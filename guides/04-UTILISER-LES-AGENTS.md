# 04 · Utiliser les agents : les 4 missions types

Avant la première mission, crée la fiche de ton produit :
```
produits/<mon-produit>/PRODUIT.md        ← copie de modeles/PRODUIT.example.md, remplie
produits/<mon-produit>/packshots/        ← tes VRAIES photos produit (fond blanc + en situation)
```
Sans vraies photos du produit, les agents refusent de produire des visuels produit : une IA qui invente un packaging, c'est une pub qui ment.

---

## Mission 1 · Reproduire un static concurrent (hamid + omar)
**Dis :**
> hamid, reproduis ce static à l'identique pour mon produit `<mon-produit>`. [image ou lien]

**Déroulé :**
1. hamid analyse la source : mise en page, zones, textes, hiérarchie, couleurs, typo, ce qui fait vendre.
2. omar écrit le prompt (7 blocs) en partant de ton vrai packshot.
3. hamid génère 1 à 3 essais (Nano Banana Pro via kie.ai) et pose les textes exacts. Quand c'est plus sûr, il retouche en code plutôt que de régénérer.
4. **Planche côte à côte « original | reproduction »** puis contrôle d'omar (PASS / CORRIGER).
5. Livraison en **1:1** dans `livraisons/<date>/`.

**Pour aller plus loin :** « hamid, décline ce static en 5 hooks différents », ou « hamid, fais-en 3 variantes avec un autre avatar ».

---

## Mission 2 · Reproduire une vidéo concurrente plan par plan (ziad + omar)
**Dis :**
> ziad, refais cette pub plan par plan pour mon produit `<mon-produit>` : <lien>. 480p d'abord.

**Déroulé :**
1. **Analyse de la source** : téléchargement, extraction à 10 images par seconde, découpage au dixième de seconde. Ziad liste chaque plan (durée, cadrage, action, texte, son) et transcrit la voix.
2. **Script adapté** : même structure, même rythme, mêmes types de hook. Seuls la marque, le produit et les claims changent, et les claims viennent de `PRODUIT.md`.
3. **Avatars IA** : chaque personne de la source est remplacée par un avatar IA créé pour l'occasion (planche personnage). Jamais de visage flouté, jamais le visage d'une vraie personne.
4. **Images de départ** : une par plan, montrées sur une **planche « original | départ »**. Rien n'est lancé avant ta validation.
5. **Vidéos en 480p** (kie.ai : Wan 3.0, Kling ou Seedance selon le plan), voix ElevenLabs, lip-sync.
6. **Montage** (ffmpeg, Remotion ou HyperFrames) : un plan toutes les 2,5 à 3 s, aucune répétition, sous-titres en zone sûre, -14 LUFS.
7. **Contrôle d'omar** : comparaison plan par plan avec la source, synchronisation, pauses, sous-titres, fidélité du produit. Ensuite seulement, passage en 720p.

**Formats « maison » à demander** (pour ne pas seulement copier) :
- « ziad, fais une version *micro-trottoir* : pancarte, quiz, dégustation ».
- « ziad, fais une *tier list* où mon produit est classé A et une habitude gratuite en S ».
- « ziad, fais une pub *chantée* au bureau, avec le B-roll dans des vignettes sur le mur ».

---

## Mission 3 · Reproduire une page produit concurrente (yassine + omar)
**Dis :**
> yassine, reproduis cette page produit section par section pour `<mon-produit>` : <lien>. Thème dupliqué, captures mobile et desktop.

**Déroulé :**
1. Captures de la page concurrente (390 px et 1440 px) et inventaire des sections : galerie, buy box, bundles, avis, FAQ, garantie…
2. **Duplication de ton thème.** Il ne touche jamais au thème publié.
3. Construction des sections Liquid une par une : textes de `PRODUIT.md`, prix en ,95 ou ,99, avis codés dans la section, offres de pack, puis l'abonnement **après** les offres.
4. Contrôle : images bien cadrées, prix, vitesse, mobile, aucun défilement horizontal. Captures avant / après.
5. Contrôle d'omar, puis yassine t'envoie le lien d'aperçu. **C'est toi qui publies.**

---

## Mission 4 · Contrôle qualité seul (omar)
**Dis :**
> omar, contrôle tout ce qu'il y a dans `livraisons/<date>/` et donne PASS ou CORRIGER pour chaque fichier, avec les corrections précises.

omar mesure, il ne se contente pas de « regarder » :
- format et durée ;
- zones sûres 9:16 ;
- pauses dans la voix ;
- texte lisible et sans faute ;
- produit fidèle au vrai ;
- aspect IA (mains, peau, logos parasites) ;
- conformité Meta.

---

## Entraîner tes agents
- **Corrige au fil de l'eau :** « Retiens : sur mes pubs, les sous-titres sont toujours en majuscules ». L'agent note la règle et l'applique la fois suivante.
- **Ajoute tes propres règles** dans `REGLES-MAISON.md`. Les 4 agents les lisent à chaque mission.
- **Une pub qui marche :** dis-le à l'agent (« celle-ci a fait un ROAS de 3, garde-la comme référence »). Il s'en servira comme modèle.

## Phrases utiles
| Tu dis | Effet |
|---|---|
| « montre-moi d'abord » | l'agent s'arrête avant toute dépense et te montre la planche ou le script |
| « budget max X $ » | plafond de dépense pour la mission |
| « 480p seulement » | test pas cher avant le rendu final |
| « omar, sois impitoyable » | contrôle plus strict |
| « range par TOFU / MOFU / BOFU » | livraison triée par étape du funnel |
