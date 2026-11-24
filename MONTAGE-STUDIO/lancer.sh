#!/bin/zsh
# Studio Ads : lancement sans Terminal.
#   ./lancer.sh mac       → ouvre le studio sur ce Mac (127.0.0.1 seulement)
#   ./lancer.sh iphone    → ouvre aussi l'accès téléphone sur le Wi-Fi local (code à 6 chiffres)
#   ./lancer.sh arreter   → arrête le studio proprement (jamais pendant un rendu)
#   ./lancer.sh etat      → dit si le studio tourne, dans quel mode, et les rendus en cours
emulate -L zsh
setopt no_unset pipe_fail
DOSSIER="${0:A:h}"
cd "$DOSSIER" || exit 1
PORT=7880
JOURNAL="$DOSSIER/cache/serveur.log"
PIDF="$DOSSIER/cache/serveur.pid"
MODEF="$DOSSIER/cache/serveur.mode"
PY="$DOSSIER/.venv/bin/python"
mkdir -p "$DOSSIER/cache"

# Clés d'API : seulement les lignes « export … » de ~/.zshrc, jamais affichées.
if [[ -f "$HOME/.zshrc" ]]; then
  eval "$(grep -E '^[[:space:]]*export[[:space:]]+(KIE_API_KEY|GEMINI_API_KEY|ELEVENLABS_API_KEY)=' "$HOME/.zshrc" 2>/dev/null)" 2>/dev/null
fi
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

tourne() { [[ -f "$PIDF" ]] && kill -0 "$(cat "$PIDF")" 2>/dev/null }
ip_wifi() {  # adresse du Mac sur le réseau local (Wi-Fi ou câble), via l'interface de la route par défaut
  local i; i=$(route -n get default 2>/dev/null | awk '/interface:/{print $2}')
  { [[ -n "$i" ]] && ipconfig getifaddr "$i" 2>/dev/null } || ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null
}
code() { "$PY" -c 'import json;print(json.load(open("cache/code_acces.json"))["code"])' 2>/dev/null }

demarrer() {
  local mode=$1
  if tourne; then
    if [[ "$(cat "$MODEF" 2>/dev/null)" == "$mode" ]]; then return 0; fi
    arreter || return 1
  fi
  if [[ ! -x "$PY" ]]; then
    echo "Environnement Python absent : lance d'abord ./installer.sh" >&2; return 1
  fi
  nohup "$PY" -m serveur.app --mode "$mode" --port $PORT >>"$JOURNAL" 2>&1 &
  echo $! >"$PIDF"; echo "$mode" >"$MODEF"
  for i in {1..40}; do
    curl -s -o /dev/null "http://127.0.0.1:$PORT/api/etat" && return 0
    sleep 0.25
  done
  echo "Le studio n'a pas démarré. Voir $JOURNAL" >&2; return 1
}

rendus_en_cours() {
  curl -s "http://127.0.0.1:$PORT/api/rendus" 2>/dev/null | "$PY" -c 'import json,sys
try: l=json.load(sys.stdin)
except Exception: l=[]
print(sum(1 for t in l if t.get("etat") in ("en cours","en file","en pause")))' 2>/dev/null || echo 0
}

arreter() {
  tourne || { rm -f "$PIDF" "$MODEF"; return 0; }
  local n; n=$(rendus_en_cours)
  if [[ "${n:-0}" != "0" ]]; then
    echo "Un rendu est en cours ($n). Le studio n'est pas arrêté : attends la fin du rendu." >&2
    return 2
  fi
  kill -TERM "$(cat "$PIDF")" 2>/dev/null
  for i in {1..20}; do tourne || break; sleep 0.25; done
  rm -f "$PIDF" "$MODEF"
}

case "${1:-mac}" in
  mac)
    demarrer mac && { [[ -n "${STUDIO_SANS_NAVIGATEUR:-}" ]] || open "http://127.0.0.1:$PORT/"; } ;;
  iphone)
    demarrer iphone || exit 1
    [[ -n "${STUDIO_SANS_NAVIGATEUR:-}" ]] || open "http://127.0.0.1:$PORT/"
    echo "Sur ton téléphone (même Wi-Fi) : http://$(ip_wifi):$PORT  ·  code : $(code)" ;;
  arreter)
    arreter ;;
  etat)
    if tourne; then
      echo "Studio Ads tourne (mode $(cat "$MODEF" 2>/dev/null)) : http://127.0.0.1:$PORT"
      [[ "$(cat "$MODEF" 2>/dev/null)" == "iphone" ]] && echo "Téléphone : http://$(ip_wifi):$PORT  ·  code : $(code)"
      echo "Rendus en cours : $(rendus_en_cours)"
    else
      echo "Studio Ads est arrêté."
    fi ;;
  adresse)   # utilisé par l'appli Téléphone
    echo "http://$(ip_wifi):$PORT|$(code)" ;;
  tourne)
    tourne && echo oui || echo non ;;
  *)
    echo "Usage : ./lancer.sh mac | iphone | arreter | etat" ;;
esac
