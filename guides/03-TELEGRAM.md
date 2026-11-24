# 03 · Parler à tes agents sur Telegram

Une fois en place, tu envoies un message à ton bot depuis ton téléphone (« hamid, refais ce static »), ton ordinateur travaille, et le bot te répond avec les fichiers (images, vidéos, captures).

**Condition :** ton ordinateur reste allumé, avec Claude Code lancé (étape 4 ci-dessous). Si tu fermes Claude Code, le bot ne répond plus.

## 1. Créer ton bot (2 min)
1. Dans Telegram, ouvre **@BotFather** et envoie `/newbot`.
2. Donne un nom (par exemple « Mon équipe Ads ») et un identifiant qui finit par `bot` (par exemple `monequipe_ads_bot`).
3. BotFather te répond avec un **token** du type `123456789:AAH...`. Copie-le en entier. C'est le mot de passe de ton bot : ne le partage jamais.

## 2. Installer le plugin Telegram
Bun doit être installé (voir l'étape 2 de l'installation). Dans ton dossier de travail :
```bash
cd ~/AgentsAds && claude
```
Puis, dans Claude Code :
```
/plugin install telegram@claude-plugins-official
```

## 3. Donner le token au bot
Toujours dans Claude Code :
```
/telegram:configure 123456789:AAH...ton_token
```
Le token est enregistré dans `~/.claude/channels/telegram/.env`, sur ton ordinateur uniquement.

## 4. Relancer Claude Code avec Telegram branché
Quitte avec `/exit`, puis relance avec cette commande. **C'est celle-là que tu utiliseras à chaque fois** :
```bash
cd ~/AgentsAds && claude --channels plugin:telegram@claude-plugins-official
```

## 5. Te connecter à ton bot (appairage)
1. Sur ton téléphone, ouvre ton bot (`t.me/ton_bot`) et envoie n'importe quel message.
2. Le bot répond avec un **code de 6 caractères**.
3. Dans Claude Code sur l'ordinateur, tape :
```
/telegram:access pair CODE
```
4. Verrouille ensuite le bot pour que personne d'autre ne puisse lui parler :
```
/telegram:access policy allowlist
```

C'est prêt : ton prochain message arrive directement à ton équipe.

## 6. Comment lui parler
- Appelle l'agent par son prénom : « **hamid**, … », « **ziad**, … », « **yassine**, … », « **omar**, contrôle … ».
- **Envoie la pub concurrente** : le lien (Facebook Ad Library, TikTok, Instagram) ou la vidéo et l'image directement. Pour garder la qualité d'origine, envoie l'image « en tant que fichier » (appui long, puis « Envoyer comme fichier »).
- Le bot te confirme avec « Reçu, je lance… », te fait un point d'étape pendant les longues missions, puis t'envoie le résultat avec le verdict d'omar.
- Pour tout arrêter : envoie `/stop`.

### Exemples de messages
```
hamid, refais ce static à l'identique pour mon produit (fiche produits/mon-produit/PRODUIT.md). Budget max 1 $.
ziad, voici une pub concurrente : <lien>. Refais-la plan par plan avec nos avatars IA. 480p d'abord, montre-moi la planche des images de départ avant de lancer les vidéos.
yassine, reproduis cette page produit : <lien>, sur un thème dupliqué, pour mon produit. Captures mobile + desktop.
omar, contrôle le dossier livraisons/2026-11-02 et donne-moi PASS ou CORRIGER pour chaque fichier.
```

## 7. En cas de souci
| Problème | Solution |
|---|---|
| Le bot ne répond pas | Claude Code n'a pas été lancé avec `--channels plugin:telegram@claude-plugins-official`, ou l'ordinateur est en veille. Mac : Réglages → Écran → empêcher la mise en veille automatique pendant que l'écran est éteint. |
| « bun: command not found » | Réinstalle Bun (étape 2 de l'installation), puis rouvre le terminal. |
| Le bot répond à d'autres personnes | `/telegram:access policy allowlist` |
| Photo floue reçue par l'agent | Envoie-la « comme fichier ». |
| Tu veux plusieurs bots, par exemple un par boutique | Un dossier de travail par boutique, et la variable `TELEGRAM_STATE_DIR` différente pour chaque bot. |

Étape suivante : **`04-UTILISER-LES-AGENTS.md`**.
