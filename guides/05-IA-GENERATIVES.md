# 05 · Les IA génératives : laquelle pour quoi

Tout passe par **kie.ai**, avec un seul compte et un seul solde de crédits. Les agents lancent les générations avec `outils/kie.py`. Tu n'as rien à faire à la main, mais tu dois savoir ce qu'ils utilisent et pourquoi.

## Priorité vidéo : Wan 3.0, puis Wan 3.0 Prime
| Modèle (alias kie.py) | Quand l'utiliser | Prix kie (crédits par seconde) |
|---|---|---|
| **Wan 3.0** (`wan-3`) | **Le modèle par défaut.** Clips parlants (UGC face caméra, témoignage, micro-trottoir), lip-sync piloté par la voix (`--ref_audio`), B-roll muet. De 2 à 30 s, au format 9:16. | 480p : 8 · 720p : 16 · 1080p : 32 |
| **Wan 3.0 Prime** (`wan-3-prime`) | **Pour le rendu final** d'un plan validé en Wan 3.0 : plus de détail, peau et mains plus propres, mouvements plus stables. Mêmes options que Wan 3.0. | 480p : 12,2 · 720p : 25,2 · 1080p : 50,4 |
| Kling 3.0 (`kling`) | Gestes complexes, mouvement de produit, plans d'action sans dialogue | 14 à 67 |
| Seedance 2.0 / 2.5 (`seedance`, `seedance-2.5`) | Personnage stylisé ou 3D (façon Pixar), plans multi-références, cohérence sur une suite de plans | 28 à 208 |
| Veo 3.1 (`veo`) | Son natif, plans cinéma de 4 à 8 s | selon le tarif kie |

### La méthode qui fait économiser
1. **Image de départ validée d'abord** (Nano Banana Pro). Le modèle vidéo part de cette image : si elle est fausse, la vidéo le sera aussi.
2. **Tester en Wan 3.0 en 480p.** On vérifie le jeu, le geste et la synchro.
3. **Rendu final** du même prompt en **Wan 3.0 Prime en 720p** (ou 1080p si nécessaire).
4. **Après 2 essais ratés** sur un plan, on change d'approche (autre cadrage, prise plus courte, autre modèle) au lieu de relancer à l'aveugle.

### Les règles Wan 3.0 qui marchent
- **Prises courtes pour les répliques rapides**, de 3 à 5 s. Au-delà, Wan ralentit et se décale de 1 à 2 s.
- **Le prompt commence par la caméra** : « Static, locked-off shot, no camera movement, no zoom, no push-in. » Sinon, il zoome tout seul.
- **Une ligne de voix verrouillée par personnage**, identique à chaque prise. Seule la réplique change.
- **Fin muette** : « Then she stops talking, closes her mouth and keeps looking at [X] until the end. »
- **Une seule action par prise**, liée à un mot précis.
- **Vérifier chaque prise** : comparer son audio à la voix (le décalage doit être de 0,00 s) et lire la transcription (aucun mot répété ou inventé).
- **Les lettres et les noms de marque s'écrivent comme ils se prononcent** (« A-tier », la marque écrite phonétiquement si elle est ambiguë).

## Images
| Modèle | Usage |
|---|---|
| **Nano Banana Pro** (`nano-banana-pro`) | **Le modèle par défaut** : statics, images de départ des vidéos, planches personnage, jusqu'à 8 images de référence (vrai packshot, avatar, décor). |
| Nano Banana Edit (`nano-banana-edit`) | Retouche ciblée d'une image existante : changer une personne, réécrire une pancarte, enlever un logo. Une seule retouche par image, jamais en chaîne. |
| GPT Image (via kie) | Mises en page riches en texte, si Nano Banana se trompe sur l'orthographe |

**Règles image** :
- le packshot est *placé* en référence, jamais décrit ;
- le texte exact est écrit entre guillemets ;
- quand on part d'une photo, aucun mot de qualité (« 4K », « realistic »), sinon la peau devient cireuse ;
- partir d'une **vraie photo** (prise au téléphone) et ne changer que la personne : c'est ce qui donne le rendu le plus réel.

## Son
| Outil | Usage |
|---|---|
| **ElevenLabs v4** | Toutes les voix : UGC, voix off, témoignages. Voir `07-VOIX-ULTRA-NATURELLE.md`. |
| ElevenLabs Music / Lyria (Gemini) | Musique de fond, jingles. Toujours « no vocals ». |
| Gemini TTS | Voix secondaire rapide, par exemple un intervieweur hors champ. |
| Demucs (gratuit) | Séparer la voix de la musique d'une piste. |

## Montage
| Outil | Usage |
|---|---|
| **ffmpeg** | Découpe, assemblage, sous-titres incrustés, mesure du volume (-14 LUFS), extraction des images |
| **Remotion** (plugin) | Montage en code : sous-titres karaoké, stickers, cartes de fin, motion design, incrustations |
| **HyperFrames** (plugin) | Vidéos en HTML : sous-titres incrustés, explainers, slideshows, recut d'une vidéo face caméra |

## Formats éprouvés à demander à ziad
| Format | Idée | Coût indicatif |
|---|---|---|
| Reproduction plan par plan | La pub concurrente refaite à l'identique avec tes avatars | 3 à 10 $ |
| Micro-trottoir « Change my mind » | Pancarte, quiz, passants qui se trompent, dégustation | ~5 $ |
| Tier list | Une fondatrice classe des habitudes, ton produit en A et une habitude gratuite en S | ~3 $ |
| Pub chantée au bureau | Complainte rimée sur les « règles » de la catégorie, B-roll dans des vignettes au mur | ~8 $ |
| Mécanisme Pixar | Personnage 3D sur fond uni, le mécanisme dessiné | faible en 480p |
