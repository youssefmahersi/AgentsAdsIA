# 02 · Clés API et connecteurs

Les agents ne génèrent rien sans tes clés. **Ne colle jamais une clé dans une conversation, un fichier du pack ou un message Telegram** : elle va dans ton terminal, dans un fichier caché à toi.

## Les comptes à créer

| Service | Pour quoi faire | Obligatoire ? | Où créer la clé |
|---|---|---|---|
| **kie.ai** | Toutes les images (Nano Banana Pro, GPT Image) et les vidéos (Wan 3.0, Kling, Seedance, Veo) depuis un seul compte, payé au crédit | **Oui** | kie.ai → API Key |
| **ElevenLabs** | Voix off et voix d'UGC ultra naturelles | **Oui pour la vidéo** | elevenlabs.io → Profile → API Keys |
| **Google AI Studio (Gemini)** | Musique (Lyria), voix rapides (Gemini TTS), écoute et contrôle automatique des vidéos | Recommandé | aistudio.google.com → Get API key |
| **Shopify** | Pour que yassine travaille sur ta boutique | Oui pour le site | voir « Connecteur Shopify » plus bas |
| Higgsfield | Images et vidéos supplémentaires | Optionnel | higgsfield.ai |

## Poser les clés (une seule fois)

### Mac
```bash
nano ~/.zshrc
```
Ajoute ces lignes à la fin du fichier, avec tes vraies clés :
```bash
export KIE_API_KEY="ta_cle_kie"
export ELEVENLABS_API_KEY="ta_cle_elevenlabs"
export GEMINI_API_KEY="ta_cle_gemini"
export GOOGLE_API_KEY="$GEMINI_API_KEY"
```
Enregistre (`Ctrl + O`, `Entrée`, `Ctrl + X`), puis lance `source ~/.zshrc`.

### Windows (PowerShell)
```powershell
setx KIE_API_KEY "ta_cle_kie"
setx ELEVENLABS_API_KEY "ta_cle_elevenlabs"
setx GEMINI_API_KEY "ta_cle_gemini"
setx GOOGLE_API_KEY "ta_cle_gemini"
```
Ferme et rouvre PowerShell.

### Vérifier (appel gratuit)
```bash
cd ~/AgentsAds && python3 outils/kie.py solde
```
La commande doit afficher tes crédits kie.ai restants.

## L'outil `kie.py` (déjà dans ton dossier)
C'est par lui que hamid et ziad génèrent. Tu n'as pas à le lancer toi-même, mais voici ce qu'il fait :
- il **estime le coût avant chaque envoi** et refuse si ça dépasse le plafond fixé dans `config/kie.json` ;
- il journalise chaque génération dans `journal/kie.jsonl` (suivi des crédits et des reprises) ;
- il dépose tes fichiers locaux (packshots, images de départ) chez kie.ai.

Pour régler tes plafonds : copie `config/kie.example.json` en `config/kie.json` et modifie les montants.

Commandes utiles :
```bash
python3 outils/kie.py modeles                      # modèles disponibles et options
python3 outils/kie.py solde                        # crédits restants
python3 outils/kie.py image --help                 # options d'image
python3 outils/kie.py video --help                 # options de vidéo
```

## Connecteur Shopify (pour yassine)
1. Sur **claude.ai** → Paramètres → **Connecteurs** → ajoute **Shopify** et connecte ta boutique.
2. Le connecteur est ensuite disponible dans Claude Code, avec le même compte.
3. Vérifie avec : « yassine, lis le nom de ma boutique et la liste des thèmes ».

> Règle de sécurité : yassine travaille **toujours sur un thème dupliqué non publié**. **C'est toi qui publies**, après avoir vu les captures et le PASS d'omar. L'API ne peut pas modifier un thème déjà publié : il faut toujours dupliquer d'abord.

## Connecteur Chrome
Il est déjà installé à l'étape 6 de l'installation. Pour le vérifier, dans le terminal :
```bash
claude mcp list
```
`chrome-devtools` doit apparaître.

## Ce que coûte une pub (ordre de grandeur)
| Créa | Coût indicatif |
|---|---|
| Static 1:1 reproduit (2-3 essais) | 0,20 à 0,50 $ |
| Vidéo UGC 30-45 s reproduite plan par plan (480p puis 720p) | 3 à 10 $ |
| Voix ElevenLabs | quelques centimes par pub |
| Page produit reproduite | 0 $ en génération, seulement les images de la page |

Les agents annoncent toujours le prix avant de dépenser. Tu peux leur dire « pas plus de 5 $ sur cette pub ».

Étape suivante : **`03-TELEGRAM.md`**.
