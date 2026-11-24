# Studio Ads

Studio de montage local pour l'équipe Ads. Il permet de :
- voir en direct ce que l'équipe envoie à kie.ai et à Gemini ;
- monter les vidéos comme dans CapCut, sur le Mac ou le téléphone ;
- donner des ordres à Claude ;
- exporter avec les bons réglages Meta et TikTok.

## Lancer
- **Sur le Mac** : double-clique **Studio Ads** sur le Bureau. Le navigateur s'ouvre sur http://127.0.0.1:7880.
- **Sur le téléphone** : double-clique **Studio Ads – Téléphone**. Une fenêtre donne l'adresse à ouvrir (même Wi-Fi ou même box) et le code à 6 chiffres.
- **Si le studio tourne déjà**, l'appli te propose « Ouvrir » ou « Arrêter ».

Sans les applis, depuis un terminal ouvert dans `MONTAGE-STUDIO/` :
```
./lancer.sh mac        # ouvrir sur le Mac
./lancer.sh iphone     # ouvrir aussi pour le téléphone
./lancer.sh etat       # le studio tourne-t-il ?
./lancer.sh arreter    # arrêter (refusé tant qu'un rendu est en cours)
```
Pour réinstaller (nouvel ordinateur, applis effacées), lance `./installer.sh`.

## Arrêter
Double-clique l'appli, puis choisis « Arrêter ». Le studio refuse de s'arrêter pendant un rendu : il ne coupe jamais un travail en cours.

## Où sont les fichiers

| Quoi | Où |
|---|---|
| Projets de montage (une version par enregistrement : v001, v002…) | `projets/<projet>/versions/` |
| Repères | `projets/<projet>/markers.json` |
| Exports vérifiés | `exports/<projet>/` |
| Looks en LUT .cube | `luts/` |
| Vidéos à reproduire | `references/<date>_<nom>/` |
| Boîte d'ordres et réponses | `inbox/ordres.jsonl`, `inbox/reponses.jsonl` |
| Relances lancées depuis le studio | `generations/<date>/` |
| Journal du serveur, aperçus, code d'accès | `cache/` (peut être vidé, sauf `code_acces.json`) |
| Carte des fonctions (V1 / V2) | `docs/FONCTIONS.md` |
| Test peau des looks | `docs/planche_peau.png`, `docs/rapport_peau.json` |

## Pour Claude et les agents : traiter les ordres
```
python3 outils/ordres.py liste
python3 outils/ordres.py pris <id>
python3 outils/ordres.py repondre <id> "texte"
python3 outils/ordres.py fait <id>
```

## Sécurité
- **Accès** : le studio n'écoute que sur ce Mac et, en mode téléphone, sur le réseau local, avec un code obligatoire. Jamais sur Internet.
- **Clés d'API** : elles sont lues dans `~/.zshrc` au lancement et ne sont jamais affichées ni écrites.
- **Aucune dépense automatique** : une relance de génération se prépare d'abord à blanc (gratuit). Elle ne part que si tu tapes « JE CONFIRME LA DEPENSE ».
- **Rien n'est jamais écrasé** : chaque enregistrement et chaque export crée un nouveau fichier.
- **Charge de la machine** : 2 rendus lourds au maximum en même temps. Un rendu se met en pause, il ne s'arrête jamais.
