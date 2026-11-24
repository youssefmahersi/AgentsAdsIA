#!/bin/zsh
# Lecteur AgentsAds : lancement sans Terminal (utilisé par l'appli du Bureau).
#   ./lancer.sh ouvrir   → démarre le lecteur s'il ne tourne pas, puis ouvre le navigateur
#   ./lancer.sh tourne   → oui / non
#   ./lancer.sh arreter  → arrête le lecteur (seulement le lecteur, rien d'autre)
emulate -L zsh
DOSSIER="${0:A:h}"          # outils/lecteur
PROJET="${DOSSIER:h:h}"     # AgentsAds
PORT=3000
JOURNAL="$PROJET/MONTAGE-STUDIO/cache/lecteur.log"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

pid_lecteur() {  # pid qui écoute sur le port, seulement si c'est bien lecteur.py
  local p; p=$(lsof -nP -tiTCP:$PORT -sTCP:LISTEN 2>/dev/null | head -1)
  [[ -n "$p" ]] && ps -o command= -p "$p" 2>/dev/null | grep -q "lecteur.py" && echo "$p"
}

case "${1:-ouvrir}" in
  tourne)
    [[ -n "$(pid_lecteur)" ]] && echo oui || echo non ;;
  ouvrir)
    if [[ -z "$(pid_lecteur)" ]]; then
      mkdir -p "${JOURNAL:h}"
      cd "$PROJET" || exit 1
      nohup python3 outils/lecteur.py --port $PORT --no-browser >>"$JOURNAL" 2>&1 &
      for i in {1..40}; do curl -s -o /dev/null "http://127.0.0.1:$PORT/" && break; sleep 0.25; done
      [[ -n "$(pid_lecteur)" ]] || { echo "Le lecteur n'a pas démarré. Voir $JOURNAL" >&2; exit 1; }
    fi
    open "http://127.0.0.1:$PORT/" ;;
  arreter)
    p=$(pid_lecteur); [[ -n "$p" ]] && kill -TERM "$p" ;;
  *) echo "Usage : ./lancer.sh ouvrir | tourne | arreter" ;;
esac
