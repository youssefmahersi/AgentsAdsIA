#!/usr/bin/env bash
# Lanceur de rea-video (décorticage de vidéo plan par plan), installé en environnement isolé.
#   bash outils/rea-video.sh decompose <video.mp4> -o <dossier> --lang en
#   bash outils/rea-video.sh review <dossier>        # l'agent regarde les images (recommandé)
#   bash outils/rea-video.sh apply-review <dossier> --by claude
# Installé le 2026-11-23 dans ~/.venvs/rea-video, code figé au commit c7162340f94b (Apache-2.0).
# Par défaut, AUCUNE vidéo n'est envoyée à Gemini : la clé est retirée de l'environnement.
# Pour l'analyse par Gemini (payante, envoie la vidéo à Google), passer REA_GEMINI=1 et --vlm.
set -euo pipefail
V="$HOME/.venvs/rea-video/bin"
export SSL_CERT_FILE="$("$V/python" -c 'import certifi; print(certifi.where())')"
if [ "${REA_GEMINI:-0}" = "1" ]; then
  exec "$V/rea-video" "$@"
else
  exec env -u GEMINI_API_KEY -u GOOGLE_API_KEY -u REA_VLM_API_KEY "$V/rea-video" "$@"
fi
