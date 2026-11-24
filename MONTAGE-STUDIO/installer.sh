#!/bin/zsh
# Installe (ou réinstalle) l'environnement Python du studio et crée les deux applis du Bureau.
emulate -L zsh
DOSSIER="${0:A:h}"
cd "$DOSSIER" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
PYBASE=$(command -v python3.13 || command -v python3.12 || command -v python3)
[[ -x .venv/bin/python ]] || "$PYBASE" -m venv .venv
.venv/bin/pip install -q --disable-pip-version-check -r requirements.txt || exit 1
command -v ffmpeg >/dev/null || { echo "ffmpeg manquant : brew install ffmpeg"; exit 1; }
chmod +x lancer.sh
zsh outils/creer_applis.sh
echo "Prêt. Double-clique « Studio Ads » sur le Bureau."
