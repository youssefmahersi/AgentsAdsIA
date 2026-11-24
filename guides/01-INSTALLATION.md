# 01 · Installation (Mac et Windows)

Compte environ 30 minutes. Fais les étapes dans l'ordre. Une commande se tape dans le **Terminal** (Mac : `Cmd + Espace`, tape « Terminal ») ou dans **PowerShell** (Windows : menu Démarrer, tape « PowerShell »).

## 1. Le compte Claude
Il faut un abonnement **Claude Pro ou Max** sur claude.ai. **Max** est conseillé : les agents travaillent longtemps et lancent des sous-tâches.

## 2. Les outils de base

### Sur Mac
Installe Homebrew (le gestionnaire de logiciels), puis le reste :
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install node python ffmpeg yt-dlp git
curl -fsSL https://bun.sh/install | bash      # requis pour Telegram
```

### Sur Windows
```powershell
winget install OpenJS.NodeJS.LTS Python.Python.3.12 Gyan.FFmpeg yt-dlp.yt-dlp Git.Git
powershell -c "irm bun.sh/install.ps1 | iex"   # requis pour Telegram
```
Ferme PowerShell et rouvre-le après l'installation.

### À quoi servent ces outils
| Outil | Rôle |
|---|---|
| node | Remotion, HyperFrames et les connecteurs MCP |
| python | les scripts du pack (`kie.py`, contrôles) |
| ffmpeg | découper, monter, mesurer les vidéos (indispensable à ziad et omar) |
| yt-dlp | télécharger la pub concurrente à analyser |
| bun | le bot Telegram |
| Google Chrome | yassine et omar l'utilisent pour regarder les pages et faire des captures |

Si Chrome n'est pas déjà installé, installe-le.

Optionnel, pour séparer une voix de sa musique : `pip install demucs`.

## 3. Claude Code
**Mac :**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```
**Windows :**
```powershell
irm https://claude.ai/install.ps1 | iex
```

Ensuite, tape `claude` puis connecte-toi avec ton compte claude.ai. Vérifie que tout marche avec `claude --version`.

## 4. Le pack (agents, skills, outils)
Dézippe le pack, ouvre un terminal **dans le dossier du pack**, puis lance :

**Mac :**
```bash
bash install.sh
```
**Windows :**
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Le script fait trois choses :
- il copie les 4 agents dans `~/.claude/agents/` et les skills dans `~/.claude/skills/` ;
- il crée ton dossier de travail **`~/AgentsAds/`**, avec `CLAUDE.md`, `REGLES-MAISON.md`, `outils/`, `config/` et `modeles/` ;
- il crée les dossiers `produits/` et `livraisons/`.

**Travaille toujours depuis ce dossier :**
```bash
cd ~/AgentsAds && claude
```

## 5. Les plugins Remotion et HyperFrames (montage vidéo en code)
Dans Claude Code, tape ces commandes une par une :
```
/plugin marketplace add remotion-dev/claude-code-plugin
/plugin install remotion@remotion
/plugin marketplace add heygen-com/hyperframes
/plugin install hyperframes@hyperframes
```
- **Remotion** : vidéos et motion design en React. Ziad s'en sert pour le montage, les sous-titres, les cartes de fin et les animations de produit.
- **HyperFrames** : vidéos en HTML (sous-titres incrustés, explainers, slideshows, recut d'une vidéo face caméra).

Quitte Claude Code (`/exit`) et relance-le pour que les plugins se chargent.

## 6. Le connecteur Chrome (MCP)
Dans le terminal (pas dans Claude) :
```bash
claude mcp add chrome-devtools --scope user -- npx -y chrome-devtools-mcp@latest
```
Ce connecteur permet à yassine et omar d'ouvrir une page, de la passer en mobile (390 px) ou en ordinateur (1440 px), de faire des captures et de lancer Lighthouse.

## 7. Vérifier que tout est en place
Lance `cd ~/AgentsAds && claude`, puis tape :
```
Liste tes agents et tes skills disponibles, puis vérifie que ffmpeg, yt-dlp, python et node répondent.
```
Tu dois voir **omar, hamid, ziad, yassine** et les skills du pack. Si un outil manque, l'agent te dit lequel.

Étape suivante : **`02-CLES-API-ET-MCP.md`**.
