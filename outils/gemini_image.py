r"""
PONT GEMINI IMAGE — générer des packshots avec Nano Banana via l'API Gemini (clé GEMINI_API_KEY).

    python3 outils/gemini_image.py tarifs
    python3 outils/gemini_image.py image "<prompt>" --ref photo1.jpg [--ref photo2.jpg ...]
            [--modele nb2|nb2-lite|pro] [--ratio 1:1] [--taille 1K] [--nombre 1]
            [--sortie produits/<produit>/packshots/genere] [--prefixe packshot] [--dry-run] [--go]

Endpoint : POST https://generativelanguage.googleapis.com/v1beta/models/<modele>:generateContent
(clé envoyée dans l'en-tête x-goog-api-key, jamais dans l'URL).

ATTENTION AU COÛT : la génération d'images n'a PAS de niveau gratuit dans l'API Gemini.
Chaque image se paie sur la facturation Google Cloud du projet de la clé. Un abonnement Google AI
(Plus, Pro, étudiant) ne couvre PAS l'API.

LA CLÉ N'EST JAMAIS STOCKÉE : lue dans GEMINI_API_KEY au moment de l'appel, jamais écrite dans le
journal, la console ou un message d'erreur (tout passe par `masquer()`).

GARDE-FOUS
  - `--dry-run` n'ouvre AUCUNE connexion et ne lit pas la clé : il affiche le coût estimé et la
    requête (images de référence résumées), puis s'arrête.
  - coût estimé AVANT l'envoi (grille ci-dessous, en USD, tarif standard vérifié le 2026-08-04
    dans le skill nano-banana) ; au-dessus de `usd_max_par_appel` (config/gemini.json, défaut 0,30),
    REFUS sauf `--go`.
  - journal en liste blanche : journal/gemini.jsonl.

Sortie : code 0 = OK, code 1 = REFUS ou échec.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CONFIG = RACINE / "config" / "gemini.json"
JOURNAL = RACINE / "journal" / "gemini.jsonl"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

RATIOS_10 = ["1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]

# Prix USD par image en sortie (tarif standard). Entrée image : ~0,0011 $ par référence sur Pro,
# négligeable ailleurs ; on l'ajoute en majorant.
MODELES = {
    "nb2": {
        "id": "gemini-3.1-flash-image",
        "nom": "Nano Banana 2",
        "prix": {"0.5K": 0.045, "1K": 0.067, "2K": 0.101, "4K": 0.151},
        "ratios": RATIOS_10 + ["1:4", "1:8", "4:1", "8:1"],
        "refs_max": 14,
    },
    "nb2-lite": {
        "id": "gemini-3.1-flash-lite-image",
        "nom": "Nano Banana 2 Lite",
        "prix": {"1K": 0.0336},
        "ratios": RATIOS_10,
        "refs_max": 14,
    },
    "pro": {
        "id": "gemini-3-pro-image",
        "nom": "Nano Banana Pro",
        "prix": {"1K": 0.134, "2K": 0.134, "4K": 0.24},
        "ratios": RATIOS_10,
        "refs_max": 14,
    },
}
PRIX_REF_ENTREE = 0.002  # majorant par image de référence
REF_MAX_MO = 15


class Refus(Exception):
    """Refus net : rien n'a été envoyé, rien n'a été dépensé."""


def charger_config() -> dict:
    conf = {"usd_max_par_appel": 0.30}
    if CONFIG.exists():
        try:
            conf.update(json.loads(CONFIG.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as e:
            raise Refus(f"config/gemini.json illisible : {e}")
    return conf


def lire_cle() -> str:
    cle = os.environ.get("GEMINI_API_KEY", "").strip()
    if not cle:
        raise Refus("GEMINI_API_KEY absente de l'environnement (voir guides/02-CLES-API-ET-MCP.md).")
    return cle


def masquer(texte: str, cle: str | None = None) -> str:
    texte = str(texte)
    if cle:
        texte = texte.replace(cle, "***")
    return re.sub(r"AIza[0-9A-Za-z_\-]{20,}", "***", texte)


def estimer_cout(modele: dict, taille: str, nombre: int, nb_refs: int) -> float:
    return round(nombre * (modele["prix"][taille] + nb_refs * PRIX_REF_ENTREE), 4)


def lire_reference(chemin: str) -> dict:
    f = Path(chemin)
    if not f.is_file():
        raise Refus(f"image de référence introuvable : {chemin}")
    taille_mo = f.stat().st_size / 1_000_000
    if taille_mo > REF_MAX_MO:
        raise Refus(f"{f.name} pèse {taille_mo:.1f} Mo (limite {REF_MAX_MO} Mo) : réduis-la avant.")
    mime = mimetypes.guess_type(f.name)[0] or ""
    if mime not in ("image/jpeg", "image/png", "image/webp"):
        raise Refus(f"{f.name} : format {mime or 'inconnu'} non accepté (jpeg, png, webp).")
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(f.read_bytes()).decode()}}


def construire_corps(prompt: str, refs: list, ratio: str, taille: str) -> dict:
    return {
        "contents": [{"role": "user", "parts": [{"text": prompt}] + refs}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": ratio, "imageSize": taille},
        },
    }


def apercu(corps: dict) -> str:
    copie = json.loads(json.dumps(corps))
    for part in copie["contents"][0]["parts"]:
        if "inline_data" in part:
            n = len(part["inline_data"]["data"])
            part["inline_data"]["data"] = f"<{n} caractères base64>"
    return json.dumps(copie, ensure_ascii=False, indent=2)


def appeler(modele_id: str, corps: dict, cle: str, timeout: int = 180) -> dict:
    req = urllib.request.Request(
        f"{BASE_URL}/{modele_id}:generateContent",
        data=json.dumps(corps).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": cle},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        raise Refus(masquer(f"API Gemini HTTP {e.code} : {detail}", cle))
    except urllib.error.URLError as e:
        raise Refus(masquer(f"connexion impossible : {e.reason}", cle))


def extraire_images(reponse: dict) -> tuple[list, str]:
    images, textes = [], []
    for cand in reponse.get("candidates", []):
        for part in (cand.get("content") or {}).get("parts", []):
            donnees = part.get("inlineData") or part.get("inline_data")
            if donnees and donnees.get("data"):
                images.append((donnees.get("mimeType") or donnees.get("mime_type") or "image/png",
                               base64.b64decode(donnees["data"])))
            elif part.get("text") and not part.get("thought"):
                textes.append(part["text"])
    if not images:
        raison = reponse.get("promptFeedback") or [c.get("finishReason") for c in reponse.get("candidates", [])]
        textes.append(f"aucune image renvoyée ({raison})")
    return images, " ".join(textes).strip()


def journaliser(ligne: dict) -> None:
    autorises = ("date", "modele", "ratio", "taille", "refs", "nombre", "cout_estime_usd",
                 "fichiers", "statut", "prompt_debut", "prompt")
    try:
        JOURNAL.parent.mkdir(parents=True, exist_ok=True)
        with JOURNAL.open("a", encoding="utf-8") as f:
            f.write(json.dumps({k: ligne[k] for k in autorises if k in ligne}, ensure_ascii=False) + "\n")
    except OSError:
        pass


def commande_tarifs(_args) -> int:
    print("Tarifs USD par image (standard, vérifiés le 2026-08-04 — à revérifier sur ai.google.dev/pricing) :")
    for alias, m in MODELES.items():
        prix = " · ".join(f"{t} : {p:g} $" for t, p in m["prix"].items())
        print(f"  {alias:9} {m['nom']:20} ({m['id']})  {prix}")
    print(f"Plafond par appel : {charger_config()['usd_max_par_appel']:g} $ (config/gemini.json). "
          "Aucun niveau gratuit pour les images.")
    return 0


def commande_image(args) -> int:
    conf = charger_config()
    modele = MODELES[args.modele]
    if args.taille not in modele["prix"]:
        raise Refus(f"{modele['nom']} ne propose pas la taille {args.taille} "
                    f"(possible : {', '.join(modele['prix'])}).")
    if args.ratio not in modele["ratios"]:
        raise Refus(f"{modele['nom']} ne propose pas le ratio {args.ratio}.")
    refs_chemins = args.ref or []
    if len(refs_chemins) > modele["refs_max"]:
        raise Refus(f"{len(refs_chemins)} références : maximum {modele['refs_max']}.")
    if not 1 <= args.nombre <= 8:
        raise Refus("--nombre doit être entre 1 et 8.")

    refs = [lire_reference(c) for c in refs_chemins]
    corps = construire_corps(args.prompt, refs, args.ratio, args.taille)
    cout = estimer_cout(modele, args.taille, args.nombre, len(refs))
    print(f"{modele['nom']} · {args.ratio} · {args.taille} · {len(refs)} réf. · {args.nombre} image(s) "
          f"→ coût estimé ≈ {cout:g} $")

    if args.dry_run:
        print("DRY-RUN : rien n'est envoyé.\n" + apercu(corps))
        return 0
    plafond = conf["usd_max_par_appel"]
    if cout > plafond and not args.go:
        raise Refus(f"coût estimé {cout:g} $ > plafond {plafond:g} $. Relance avec --go si c'est voulu.")

    cle = lire_cle()
    sortie = Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    horo = datetime.now().strftime("%Y%m%d-%H%M%S")
    fichiers = []
    for i in range(1, args.nombre + 1):
        images, texte = extraire_images(appeler(modele["id"], corps, cle))
        if texte:
            print(f"  modèle : {masquer(texte, cle)[:300]}")
        for j, (mime, octets) in enumerate(images, 1):
            ext = mimetypes.guess_extension(mime) or ".png"
            chemin = sortie / f"{args.prefixe}-{horo}-{i}{'-' + str(j) if j > 1 else ''}{ext}"
            chemin.write_bytes(octets)
            fichiers.append(str(chemin))
            print(f"  ✔ {chemin}")
    journaliser({"date": datetime.now().isoformat(timespec="seconds"), "modele": modele["id"],
                 "ratio": args.ratio, "taille": args.taille, "refs": len(refs), "nombre": args.nombre,
                 "cout_estime_usd": cout, "fichiers": fichiers,
                 "statut": "ok" if fichiers else "vide", "prompt_debut": args.prompt[:120],
                 "prompt": args.prompt})
    return 0 if fichiers else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Packshots Nano Banana via l'API Gemini (payant à l'image).")
    sp = p.add_subparsers(dest="commande", required=True)
    sp.add_parser("tarifs", help="grille de prix et plafond")
    pi = sp.add_parser("image", help="générer une ou plusieurs images")
    pi.add_argument("prompt")
    pi.add_argument("--ref", action="append", help="photo du VRAI produit (répétable)")
    pi.add_argument("--modele", choices=list(MODELES), default="nb2")
    pi.add_argument("--ratio", default="1:1")
    pi.add_argument("--taille", default="1K")
    pi.add_argument("--nombre", type=int, default=1)
    pi.add_argument("--sortie", default=str(RACINE / "livraisons" / "gemini"))
    pi.add_argument("--prefixe", default="packshot")
    pi.add_argument("--dry-run", action="store_true")
    pi.add_argument("--go", action="store_true", help="autorise un coût au-dessus du plafond")
    args = p.parse_args(argv)
    try:
        return {"tarifs": commande_tarifs, "image": commande_image}[args.commande](args)
    except Refus as e:
        print(f"REFUS : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
