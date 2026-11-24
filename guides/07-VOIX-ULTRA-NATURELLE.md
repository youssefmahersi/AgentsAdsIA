# 07 · La voix ultra naturelle (ElevenLabs v4)

But : une voix qu'on ne distingue pas d'une vraie personne. Trois choses font la différence : **le texte écrit comme on parle**, **des réglages qui laissent vivre la voix**, et **un mixage propre**. Un exemple est fourni : `modeles/EXEMPLE_voix-ultra-naturelle.mp3`.

## 1. Écrire le texte comme on parle
- **Supprime les « e » qu'on avale** à l'oral : « je me » → « j'me », « ce qui » → « c'qui », « le » → « l' ». En anglais : « gonna », « kinda », les contractions.
- **Une balise d'émotion par phrase, au début**, en anglais entre crochets :
  - `[curious]` pour l'accroche ;
  - `[sighs]` pour le problème ;
  - `[excited]` pour la découverte ;
  - `[laughs]` pour le moment drôle ;
  - `[warmly]` pour la fin ;
  - `[pause]` pour laisser un temps.
- **Des mots de vraie personne** : « Genre, vraiment. », « Franchement… », « Tu sais ». C'est ce qui casse l'effet lecture.
- **Des phrases courtes.** Une pub de 30 s fait environ 90 mots, pas plus (3 mots par seconde au maximum).

Exemple :
```
[curious] Tu veux savoir c'qui a changé mes nuits ? [sighs] Pendant des mois, j'me réveillais avec la nuque bloquée… et j'me disais « c'est l'âge ». [pause] Sauf que c'était pas normal. [excited] Alors j'ai testé <le produit>. [laughs] La première nuit, j'ai dormi d'une traite. Genre, vraiment. [warmly] Franchement… si toi aussi tu t'réveilles fatigué, essaie.
```

## 2. Les réglages ElevenLabs
| Réglage | Valeur |
|---|---|
| Modèle | **Eleven v4** |
| Stabilité | **3 à 10 %** (6 % est un bon départ) : curseur vers « créatif » |
| Similarité | **91 à 96 %** (94 % est un bon départ) |
| Balisage automatique | **Activé** si ton texte n'a pas de balises |
| Prises | **3 générations du texte ENTIER**, on garde la plus vivante |
| Export | MP3 44,1 kHz, 192 kbps |

**Pourquoi :**
- une stabilité basse laisse l'intonation varier, comme chez un humain ;
- une similarité haute garde le timbre fidèle ;
- les réglages par défaut donnent une voix plate.

**Voix conseillées :**
- en français, les voix de la bibliothèque publique au ton « UGC creator », « warm » ou « narrative » (teste-en 3 et garde la plus humaine) ;
- en anglais, la plupart des voix fonctionnent.

## 3. Les erreurs qui rendent la voix robotique
- ❌ Générer **phrase par phrase** : chaque phrase repart à zéro et l'émotion ne suit pas. ✅ Une seule prise pour tout le script.
- ❌ **Accélérer la voix** (atempo) : ça sonne pressé et faux. ✅ Raccourcis plutôt le texte.
- ❌ Forcer **toutes** les pauses à la même durée. ✅ Ne touche qu'aux blancs de plus de 0,35 s, ramenés à 0,30 s.
- ❌ Un son « studio » trop propre sur une vidéo UGC. ✅ Applique la **chaîne micro iPhone** (étape 5).
- ❌ Ne pas vérifier : un mot sauté ou mal prononcé ruine la pub. ✅ Passe la prise dans Speech to Text (ElevenLabs) et compare-la au script.

## 4. Le mixage voix off + musique
| Étape | Réglage |
|---|---|
| Couper les blancs | aucun blanc de plus de 0,35 s |
| Nettoyer le bas | passe-haut à 85 Hz |
| Désépaissir | -2 dB à 250 Hz |
| Donner de la présence | +2,5 dB à 3 200 Hz |
| Adoucir les « s » | de-esser, intensité 0,35 |
| Compresser | seuil -20 dB, ratio 3:1 |
| Musique | -17 dB sous la voix, fondu d'entrée et de sortie |
| Ducking | la musique baisse quand la voix parle (sidechain, ratio 6:1) |
| Volume final | **-14 LUFS** pour la pub montée (crête à -1,5 dB) |

**A) Nettoyer la voix**
```bash
ffmpeg -i prise.mp3 -af "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.3:stop_threshold=-42dB:stop_silence=0.22,highpass=f=85,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,deesser=i=0.35,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3,alimiter=limit=0.89" -ar 48000 voix_traitee.wav
```
**B) Poser la musique avec ducking** : remplace T par la durée de la voix + 2,3 s, et F par T - 1,8.
```bash
ffmpeg -i voix_traitee.wav -stream_loop 1 -i musique.mp3 -filter_complex "[0:a]adelay=700|700,apad=pad_dur=2[v];[v]asplit=2[vm][vsc];[1:a]aresample=48000,volume=-17dB,atrim=0:T,afade=t=in:d=0.4,afade=t=out:st=F:d=1.8[m];[m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=300[md];[vm][md]amix=inputs=2:duration=first:normalize=0,atrim=0:T,loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 -c:a libmp3lame -b:a 256k VOIX-FINALE.mp3
```
**Prompt de musique** (ElevenLabs Music ou Lyria) :
```
Warm upbeat acoustic pop instrumental for a short social media ad, light claps, soft guitar and piano, positive and cosy, steady 105 bpm, no vocals, clean mix that leaves space for a voiceover
```

## 5. La chaîne « micro iPhone » (UGC face caméra)
Pour une voix d'UGC qui sort d'un téléphone, et pas d'un studio, après le nettoyage :
```bash
ffmpeg -i voix_traitee.wav -f lavfi -i "anoisesrc=color=brown:amplitude=0.004" -filter_complex "[0:a]highpass=f=120,lowpass=f=11000,equalizer=f=2800:t=q:w=1.2:g=2,aecho=0.8:0.5:18|32:0.10|0.06[v];[1:a]lowpass=f=900[n];[v][n]amix=inputs=2:duration=first:weights='1 0.25':normalize=0" voix_iphone.wav
```
Écoute le résultat au casque **et** sur le haut-parleur du téléphone. La voix doit sonner « dans une pièce », proche, sans écho exagéré.

## 6. Contrôle final (omar le fait, mais vérifie aussi)
- ✓ Aucun blanc de plus de 0,35 s (mesuré avec `silencedetect`).
- ✓ La transcription correspond au script, mot pour mot.
- ✓ -14 LUFS sur la pub finale, crête sous -1 dB.
- ✓ **Pilote validé à l'oreille** par toi avant de lancer toute une série de vidéos.
