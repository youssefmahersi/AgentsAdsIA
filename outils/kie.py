r"""
PONT KIE.AI — un seul outil pour les images (Nano Banana) et les vidéos (Veo, Kling, Seedance).

    python kie.py solde
    python kie.py modeles
    python kie.py image "<prompt>" [--modele nano-banana] [--ratio 9:16] [--ref <url> ...] [...]
    python kie.py video "<prompt>" [--modele veo] [--duree 8] [--ratio 9:16] [--ref <url> ...] [...]
    python kie.py etat <taskId>
    python kie.py recuperer <taskId> --sortie <dossier>

Tout passe par le même couple d'endpoints (vérifiés sur docs.kie.ai, 22/09/2026) :
  POST https://api.kie.ai/api/v1/jobs/createTask   -> {"code":200,"data":{"taskId":"…"}}
  GET  https://api.kie.ai/api/v1/jobs/recordInfo?taskId=…  -> data.state + data.resultJson
  GET  https://api.kie.ai/api/v1/chat/credit       -> data = crédits restants (appel GRATUIT)

LA CLÉ N'EST JAMAIS STOCKÉE. Elle se lit dans la variable d'environnement KIE_API_KEY au moment
de l'appel, ne s'écrit ni dans la config, ni dans le journal, ni dans un message d'erreur
(tout ce qui sort passe par `masquer()`).

GARDE-FOUS (une génération coûte des crédits, comme chez Artlist) :
  - `--dry-run` n'ouvre AUCUNE connexion : il imprime la requête exacte et s'arrête. Il ne
    réclame même pas la clé — c'est le mode de vérification par défaut avant un batch.
  - avant tout envoi réel, le solde est relu (appel gratuit) et l'appel est REFUSÉ si le solde
    passe sous `garde_fous.solde_minimum` ;
  - le coût est estimé AVANT l'envoi à partir de la grille de `config/kie.json` : les images
    coûtent un forfait, les vidéos se facturent À LA SECONDE (coût = tarif × durée). Au-dessus de
    `credits_max_par_appel`, REFUS sauf `--go` ;
  - un palier absent de la grille prend le tarif le plus cher du modèle (majorant), et un modèle
    sans tarif est refusé si `exiger_tarif` est actif : on ne devine jamais un prix à la baisse.

Sortie : code 0 = OK, code 1 = REFUS ou échec. Tests : `tests_kie.py` (zéro réseau, zéro crédit).
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import os
import re
import sys
import mimetypes
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from uuid import uuid4

RACINE = Path(__file__).resolve().parent
_DOSSIER_CONFIG = RACINE.parent / "config"
# kie.json (tes réglages réels) passe devant kie.example.json (le modèle livré).
CONFIG_PATH = (_DOSSIER_CONFIG / "kie.json" if (_DOSSIER_CONFIG / "kie.json").exists()
               else _DOSSIER_CONFIG / "kie.example.json")
JOURNAL = RACINE.parent / "journal" / "kie.jsonl"

BASE_URL = "https://api.kie.ai"
CHEMIN_CREATE = "/api/v1/jobs/createTask"
CHEMIN_RECORD = "/api/v1/jobs/recordInfo"
CHEMIN_CREDIT = "/api/v1/chat/credit"
# Dépôt de fichiers kie.ai : autre domaine, même clé. Gratuit, mais les fichiers y EXPIRENT
# (24 h à 3 jours selon les pages de la doc) : c'est un transit pour les références, pas un
# hébergement. L'original reste la source de vérité sur le disque.
UPLOAD_URL = "https://kieai.redpandaai.co/api/file-stream-upload"

ETATS_FINIS = ("success", "fail")


class Refus(Exception):
    """Refus net : rien n'a été envoyé, aucun crédit n'a été consommé."""


# --------------------------------------------------------------------------- registre

RATIOS_IMAGE = ["1:1", "9:16", "16:9", "3:4", "4:3", "3:2", "2:3", "5:4", "4:5", "21:9", "auto"]

REGISTRE_DEFAUT = {
    "nano-banana": {
        "model": "google/nano-banana",
        "type": "image",
        "resume": "Nano Banana — texte vers image.",
        "prompt_max": 5000,
        "champs": {
            "ratio": {"cible": "aspect_ratio", "type": "enum", "valeurs": RATIOS_IMAGE, "defaut": "1:1"},
            "format": {"cible": "output_format", "type": "enum", "valeurs": ["png", "jpeg"], "defaut": "png"},
        },
    },
    "nano-banana-edit": {
        "model": "google/nano-banana-edit",
        "type": "image",
        "resume": "Nano Banana Edit — retouche/montage à partir d'images existantes.",
        "prompt_max": 5000,
        "champs": {
            "ref": {"cible": "image_urls", "type": "urls", "min": 1, "max": 10, "requis": True},
            "ratio": {"cible": "aspect_ratio", "type": "enum", "valeurs": RATIOS_IMAGE, "defaut": "1:1"},
            "format": {"cible": "output_format", "type": "enum", "valeurs": ["png", "jpeg"], "defaut": "png"},
        },
    },
    "nano-banana-pro": {
        "model": "nano-banana-pro",
        "type": "image",
        "resume": "Nano Banana Pro — texte vers image, jusqu'à 4K, 8 images d'entrée.",
        "prompt_max": 10000,
        "champs": {
            "ref": {"cible": "image_input", "type": "urls", "max": 8},
            "ratio": {"cible": "aspect_ratio", "type": "enum",
                      "valeurs": [r for r in RATIOS_IMAGE if r != "auto"] + ["auto"], "defaut": "1:1"},
            "resolution": {"cible": "resolution", "type": "enum", "valeurs": ["1K", "2K", "4K"], "defaut": "1K"},
            "format": {"cible": "output_format", "type": "enum", "valeurs": ["png", "jpg"], "defaut": "png"},
        },
    },
    "veo": {
        "model": "veo-3-1",
        "type": "video",
        "resume": "Veo 3.1 — 4/6/8 s, 720p à 4K, son natif.",
        "prompt_max": 5000,
        "champs": {
            "ref": {"cible": "image_urls", "type": "urls", "max": 2},
            "ratio": {"cible": "aspect_ratio", "type": "enum", "valeurs": ["16:9", "9:16", "Auto"], "defaut": "9:16"},
            "resolution": {"cible": "resolution", "type": "enum", "valeurs": ["720p", "1080p", "4k"], "defaut": "720p"},
            "duree": {"cible": "duration", "type": "enum_entier", "valeurs": [4, 6, 8], "defaut": 8},
            "watermark": {"cible": "watermark", "type": "texte"},
            "traduire": {"cible": "enable_translation", "type": "booleen"},
        },
    },
    "kling": {
        "model": "kling-3.0/video",
        "type": "video",
        "resume": "Kling 3.0 — 3 à 15 s, modes std/pro/4K, son optionnel.",
        "prompt_max": 5000,
        "champs": {
            "ref": {"cible": "image_urls", "type": "urls", "max": 2},
            "ratio": {"cible": "aspect_ratio", "type": "enum", "valeurs": ["16:9", "9:16", "1:1"], "defaut": "9:16"},
            "duree": {"cible": "duration", "type": "entier", "min": 3, "max": 15, "defaut": 5, "en_texte": True},
            "mode": {"cible": "mode", "type": "enum", "valeurs": ["std", "pro", "4K"], "defaut": "pro"},
            "audio": {"cible": "sound", "type": "booleen", "defaut": True},
            # kie.ai exige ce champ depuis 09/2026 (422 « multi_shots cannot be empty », Ziad 28/09/2026).
            "multi_shots": {"cible": "multi_shots", "type": "booleen", "defaut": False},
        },
    },
    "seedance-2.5": {
        "model": "bytedance/seedance-2-5",
        "type": "video",
        "resume": "Seedance 2.5 — 4 à 30 s, 480p à 1080p, jusqu'à 30 images de référence.",
        "prompt_max": 30000,
        "prompt_min": 3,
        "champs": {
            "ref": {"cible": "reference_image_urls", "type": "urls", "max": 30},
            "image_debut": {"cible": "first_frame_url", "type": "url"},
            "image_fin": {"cible": "last_frame_url", "type": "url"},
            # Référence vidéo (mouvement) et audio (voix) — mode « multimodal reference-to-video ».
            # Exclusif avec image_debut/image_fin (doc kie.ai, vérifiée le 23/09/2026).
            "ref_video": {"cible": "reference_video_urls", "type": "urls", "max": 10},
            "ref_audio": {"cible": "reference_audio_urls", "type": "urls", "max": 10},
            "ratio": {"cible": "aspect_ratio", "type": "enum",
                      "valeurs": ["1:1", "4:3", "3:4", "16:9", "9:16", "21:9", "adaptive"], "defaut": "9:16"},
            "resolution": {"cible": "resolution", "type": "enum",
                           "valeurs": ["480p", "720p", "1080p"], "defaut": "720p"},
            "duree": {"cible": "duration", "type": "entier", "min": 4, "max": 30, "defaut": 5},
            "audio": {"cible": "generate_audio", "type": "booleen", "defaut": True},
            "format": {"cible": "output_format", "type": "enum", "valeurs": ["mp4", "mov"], "defaut": "mp4"},
        },
    },
    "seedance": {
        "model": "bytedance/seedance-2",
        "type": "video",
        "resume": "Seedance 2.0 — 4 à 15 s, 480p à 4K, images/vidéos de référence.",
        "prompt_max": 20000,
        "prompt_min": 3,
        "champs": {
            "ref": {"cible": "reference_image_urls", "type": "urls", "max": 9},
            "image_debut": {"cible": "first_frame_url", "type": "url"},
            "image_fin": {"cible": "last_frame_url", "type": "url"},
            "ratio": {"cible": "aspect_ratio", "type": "enum",
                      "valeurs": ["1:1", "4:3", "3:4", "16:9", "9:16", "21:9", "adaptive"], "defaut": "9:16"},
            "resolution": {"cible": "resolution", "type": "enum",
                           "valeurs": ["480p", "720p", "1080p", "4k"], "defaut": "720p"},
            "duree": {"cible": "duration", "type": "entier", "min": 4, "max": 15, "defaut": 5},
            "audio": {"cible": "generate_audio", "type": "booleen", "defaut": True},
        },
    },
}

GARDE_FOUS_DEFAUT = {"solde_minimum": 0, "credits_max_par_appel": None, "exiger_tarif": False}
API_DEFAUT = {"base_url": BASE_URL, "timeout_s": 60, "attente_max_s": 900, "intervalle_poll_s": 5,
              "upload_url": UPLOAD_URL, "upload_max_mo": 100, "upload_timeout_s": 300}


def charger_config(chemin: Path = None) -> dict:
    """Config du disque fusionnée sur les valeurs intégrées. Config absente ou cassée = valeurs
    intégrées : l'outil marche sans config, il ne marche jamais avec des réglages devinés."""
    brut = {}
    chemin = CONFIG_PATH if chemin is None else chemin
    try:
        brut = json.loads(Path(chemin).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        brut = {}
    conf = {
        "api": dict(API_DEFAUT),
        "garde_fous": dict(GARDE_FOUS_DEFAUT),
        "modeles": {a: dict(m) for a, m in REGISTRE_DEFAUT.items()},
    }
    if isinstance(brut.get("api"), dict):
        conf["api"].update({k: v for k, v in brut["api"].items() if not k.startswith("_")})
    if isinstance(brut.get("garde_fous"), dict):
        conf["garde_fous"].update({k: v for k, v in brut["garde_fous"].items() if not k.startswith("_")})
    for alias, spec in (brut.get("modeles") or {}).items():
        if alias.startswith("_") or not isinstance(spec, dict):
            continue
        fusion = dict(conf["modeles"].get(alias, {}))
        fusion.update({k: v for k, v in spec.items() if not k.startswith("_")})
        conf["modeles"][alias] = fusion
    return conf


# --------------------------------------------------------------------------- secret

def masquer(texte: str, cle: str = None) -> str:
    """Rien ne sort d'ici avec la clé dedans — ni un log, ni une trace, ni un message d'erreur."""
    texte = "" if texte is None else str(texte)
    cle = os.environ.get("KIE_API_KEY", "") if cle is None else cle
    if cle and len(cle) >= 8:
        texte = texte.replace(cle, "****")
    return re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{8,}", r"\1****", texte)


def lire_cle() -> str:
    cle = (os.environ.get("KIE_API_KEY") or "").strip()
    if not cle:
        raise Refus("KIE_API_KEY n'est pas dans l'environnement. Pose-la dans ton shell "
                    "(jamais dans un fichier du dépôt), puis relance.")
    if len(cle) < 8:
        raise Refus("KIE_API_KEY semble tronquée (moins de 8 caractères).")
    return cle


# --------------------------------------------------------------------------- construction

def _bool(valeur) -> bool:
    if isinstance(valeur, bool):
        return valeur
    return str(valeur).strip().lower() in ("1", "true", "oui", "yes", "on")


def _entier(valeur, option: str) -> int:
    try:
        return int(str(valeur).strip())
    except (TypeError, ValueError):
        raise Refus(f"--{option} attend un nombre entier, reçu : {valeur!r}")


def _url(valeur, option: str) -> str:
    valeur = str(valeur).strip()
    if valeur.startswith("asset://"):
        return valeur
    morceaux = urllib.parse.urlparse(valeur)
    if morceaux.scheme not in ("http", "https") or not morceaux.netloc:
        raise Refus(f"--{option} attend une URL http(s) publique, reçu : {valeur!r}")
    return valeur


def _valeur_champ(option: str, spec: dict, brut):
    genre = spec.get("type", "texte")
    if genre == "enum":
        valeurs = spec["valeurs"]
        if brut not in valeurs:
            raise Refus(f"--{option} : « {brut} » n'est pas accepté. Valeurs : {', '.join(map(str, valeurs))}.")
        return brut
    if genre == "enum_entier":
        n = _entier(brut, option)
        if n not in spec["valeurs"]:
            raise Refus(f"--{option} : {n} n'est pas accepté. Valeurs : "
                        f"{', '.join(str(v) for v in spec['valeurs'])}.")
        return n
    if genre == "entier":
        n = _entier(brut, option)
        if "min" in spec and n < spec["min"]:
            raise Refus(f"--{option} : {n} est sous le minimum ({spec['min']}).")
        if "max" in spec and n > spec["max"]:
            raise Refus(f"--{option} : {n} dépasse le maximum ({spec['max']}).")
        return str(n) if spec.get("en_texte") else n
    if genre == "booleen":
        return _bool(brut)
    if genre == "url":
        return _url(brut, option)
    if genre == "urls":
        liste = [brut] if isinstance(brut, str) else list(brut)
        liste = [_url(u, option) for u in liste]
        if "max" in spec and len(liste) > spec["max"]:
            raise Refus(f"--{option} : {len(liste)} images fournies, le modèle en accepte {spec['max']} au plus.")
        if "min" in spec and len(liste) < spec["min"]:
            raise Refus(f"--{option} : au moins {spec['min']} image(s) attendue(s).")
        return liste
    return str(brut)


def trouver_modele(alias: str, conf: dict, type_attendu: str = None) -> dict:
    modeles = conf["modeles"]
    spec = modeles.get(alias)
    if spec is None:
        raise Refus(f"Modèle inconnu : « {alias} ». Connus : {', '.join(sorted(modeles))}. "
                    f"(`python kie.py modeles` les détaille.)")
    if type_attendu and spec.get("type") != type_attendu:
        raise Refus(f"« {alias} » est un modèle {spec.get('type')}, pas {type_attendu}. "
                    f"Utilise la commande « {spec.get('type')} ».")
    return spec


def construire_requete(alias: str, prompt: str, options: dict = None, conf: dict = None,
                       type_attendu: str = None, callback: str = None) -> dict:
    """Corps JSON exact du POST createTask. Toute option que le modèle ne connaît pas est un refus :
    kie.ai ignore silencieusement un champ inconnu, et un ratio ignoré se paie en crédits."""
    conf = charger_config() if conf is None else conf
    spec = trouver_modele(alias, conf, type_attendu)
    champs = spec.get("champs", {})
    options = {k: v for k, v in (options or {}).items() if v is not None and v != []}

    prompt = (prompt or "").strip()
    if not prompt:
        raise Refus("Prompt vide : rien à générer.")
    if len(prompt) > spec.get("prompt_max", 5000):
        raise Refus(f"Prompt de {len(prompt)} caractères, le maximum de « {alias} » est "
                    f"{spec.get('prompt_max', 5000)}.")
    if len(prompt) < spec.get("prompt_min", 1):
        raise Refus(f"Prompt de {len(prompt)} caractères, « {alias} » en exige au moins "
                    f"{spec['prompt_min']}.")

    inconnues = sorted(set(options) - set(champs))
    if inconnues:
        acceptees = ", ".join("--" + o for o in sorted(champs)) or "aucune"
        raise Refus(f"« {alias} » ne prend pas : {', '.join('--' + o for o in inconnues)}. "
                    f"Options acceptées : {acceptees}.")

    entree = {"prompt": prompt}
    for option, regle in champs.items():
        if option in options:
            entree[regle["cible"]] = _valeur_champ(option, regle, options[option])
        elif regle.get("requis"):
            raise Refus(f"« {alias} » exige --{option}.")
        elif "defaut" in regle:
            entree[regle["cible"]] = regle["defaut"]

    if entree.get("reference_video_urls") or entree.get("reference_audio_urls"):
        if entree.get("first_frame_url") or entree.get("last_frame_url"):
            raise Refus("--ref-video/--ref-audio (référence multimodale) et --image-debut/--image-fin "
                        "(image-to-video) sont exclusifs chez kie.ai : choisis l'un des deux modes.")
    corps = {"model": spec["model"], "input": entree}
    if callback:
        corps["callBackUrl"] = _url(callback, "callback")
    return corps


# --------------------------------------------------------------------------- réseau

def _http(methode: str, url: str, corps: dict = None, cle: str = None, timeout: int = 60) -> dict:
    """Seul point de sortie réseau du module — les tests le remplacent pour ne jamais rien envoyer."""
    donnees = json.dumps(corps).encode("utf-8") if corps is not None else None
    requete = urllib.request.Request(url, data=donnees, method=methode)
    requete.add_header("Authorization", "Bearer " + cle)
    requete.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(requete, timeout=timeout) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = ""
        try:
            detail = err.read().decode("utf-8")[:400]
        except Exception:  # noqa: BLE001 — le détail est un bonus, jamais une raison de planter
            pass
        raise Refus(masquer(f"kie.ai a répondu HTTP {err.code}. {detail}", cle))
    except urllib.error.URLError as err:
        raise Refus(masquer(f"Connexion à kie.ai impossible : {err.reason}", cle))
    except json.JSONDecodeError:
        raise Refus("kie.ai a répondu autre chose que du JSON.")


def _envoyer_multipart(url: str, chemin: Path, champs: dict, cle: str, timeout: int = 300) -> dict:
    """Seconde et dernière porte de sortie réseau (multipart) — piégée elle aussi par les tests."""
    frontiere = "----kie" + uuid4().hex
    nom = Path(chemin).name
    mime = mimetypes.guess_type(nom)[0] or "application/octet-stream"
    corps = bytearray()
    for clef, valeur in champs.items():
        corps += (f"--{frontiere}\r\nContent-Disposition: form-data; name=\"{clef}\"\r\n\r\n"
                  f"{valeur}\r\n").encode("utf-8")
    corps += (f"--{frontiere}\r\nContent-Disposition: form-data; name=\"file\"; "
              f"filename=\"{nom}\"\r\nContent-Type: {mime}\r\n\r\n").encode("utf-8")
    corps += Path(chemin).read_bytes() + f"\r\n--{frontiere}--\r\n".encode("utf-8")
    requete = urllib.request.Request(url, data=bytes(corps), method="POST")
    requete.add_header("Authorization", "Bearer " + cle)
    requete.add_header("Content-Type", f"multipart/form-data; boundary={frontiere}")
    try:
        with urllib.request.urlopen(requete, timeout=timeout) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = ""
        try:
            detail = err.read().decode("utf-8")[:300]
        except Exception:  # noqa: BLE001
            pass
        raise Refus(masquer(f"Téléversement refusé (HTTP {err.code}). {detail}", cle))
    except urllib.error.URLError as err:
        raise Refus(masquer(f"Téléversement impossible : {err.reason}", cle))
    except json.JSONDecodeError:
        raise Refus("Le dépôt de fichiers a répondu autre chose que du JSON.")


def est_chemin_local(valeur: str) -> bool:
    """Un argument qui n'est ni http(s) ni asset:// est traité comme un fichier du disque."""
    valeur = str(valeur).strip()
    return not (valeur.startswith(("http://", "https://", "asset://")))


def _nom_unique(fichier: Path) -> str:
    """Piège payé le 24/09/2026  : le dépôt kie.ai range les fichiers sous
    uploadPath/fileName. Deux plans téléversant chacun leur « image_debut.png » en parallèle
    partageaient la MÊME URL : le clip S19 a démarré sur l'image de départ de S18. Le nom déposé
    porte donc l'empreinte du contenu : même fichier = même nom, fichiers différents = URL différentes."""
    import hashlib
    h = hashlib.sha256()
    with open(fichier, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return f"{h.hexdigest()[:16]}_{fichier.name}"


def televerser(chemin, cle: str, conf: dict) -> tuple:
    """Dépose un fichier local chez kie.ai et rend (url, expiration). Aucun crédit consommé."""
    fichier = Path(str(chemin)).expanduser()
    if not fichier.is_file():
        raise Refus(f"Référence introuvable sur le disque : {fichier}")
    plafond_mo = conf["api"].get("upload_max_mo", 100)
    taille_mo = fichier.stat().st_size / (1024 * 1024)
    if taille_mo > plafond_mo:
        raise Refus(f"{fichier.name} pèse {taille_mo:.1f} Mo, au-dessus de la limite de {plafond_mo} Mo.")
    reponse = _envoyer_multipart(conf["api"].get("upload_url", UPLOAD_URL), fichier,
                                 {"uploadPath": ("images/usine" if (mimetypes.guess_type(fichier.name)[0] or "").startswith("image")
                                                 else "media/usine"), "fileName": _nom_unique(fichier)}, cle,
                                 conf["api"].get("upload_timeout_s", 300))
    data = (reponse or {}).get("data") or {}
    url = data.get("fileUrl") or data.get("downloadUrl")
    if not url:
        raise Refus(masquer(f"Téléversement sans URL en retour : {str(reponse)[:200]}"))
    return url, data.get("expiresAt")


def duree_videos_locales(valeurs) -> float:
    """Somme des durées (s) des vidéos de référence LOCALES, via ffprobe. None si une durée est
    inconnue (URL distante, ffprobe absent) : l'estimation prendra alors le majorant."""
    if not valeurs:
        return None
    total = 0.0
    for v in (valeurs if isinstance(valeurs, list) else [valeurs]):
        if not est_chemin_local(v):
            return None
        try:
            sortie = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "csv=p=0", str(Path(str(v)).expanduser())],
                                    capture_output=True, text=True, timeout=30)
            total += float(sortie.stdout.strip())
        except (OSError, ValueError, subprocess.SubprocessError):
            return None
    return total


def resoudre_references(options: dict, cle: str, conf: dict, dry_run: bool = False) -> list:
    """Remplace les chemins locaux de --ref/--image-debut/--image-fin par des URL kie.ai.
    En dry-run, rien n'est téléversé : une URL témoin marque la place, et l'aperçu le dit."""
    notes = []
    for cle_option in ("ref", "image_debut", "image_fin", "ref_video", "ref_audio"):
        valeur = options.get(cle_option)
        if not valeur:
            continue
        liste = valeur if isinstance(valeur, list) else [valeur]
        resolu = []
        for element in liste:
            if not est_chemin_local(element):
                resolu.append(element)
                continue
            if dry_run:
                fichier = Path(str(element)).expanduser()
                etat = "" if fichier.is_file() else "  ⚠ INTROUVABLE sur le disque"
                notes.append(f"--{cle_option} {fichier.name} sera téléversé au lancement réel{etat}")
                resolu.append("https://kieai.redpandaai.co/attente/" + fichier.name)
                continue
            url, expire = televerser(element, cle, conf)
            notes.append(f"téléversé : {Path(str(element)).name} → {url}"
                         + (f" (expire {expire})" if expire else ""))
            resolu.append(url)
        options[cle_option] = resolu if isinstance(valeur, list) else resolu[0]
    return notes


def _payload(reponse: dict):
    if not isinstance(reponse, dict):
        raise Refus("Réponse inattendue de kie.ai.")
    code = reponse.get("code")
    if code != 200:
        raise Refus(masquer(f"kie.ai refuse : code {code} — {reponse.get('msg')}"))
    return reponse.get("data")


def solde(conf: dict, cle: str) -> float:
    data = _payload(_http("GET", conf["api"]["base_url"] + CHEMIN_CREDIT, None, cle,
                          conf["api"]["timeout_s"]))
    if isinstance(data, dict):
        data = data.get("credits", data.get("credit"))
    try:
        return float(data)
    except (TypeError, ValueError):
        raise Refus(f"Solde illisible dans la réponse : {data!r}")


def lire_resultat(reponse: dict) -> dict:
    """recordInfo -> {etat, urls, erreur, credits, progression}. `resultJson` arrive en CHAÎNE JSON."""
    data = _payload(reponse) or {}
    etat = data.get("state") or "inconnu"
    urls = []
    brut = data.get("resultJson")
    if isinstance(brut, str) and brut.strip():
        try:
            brut = json.loads(brut)
        except json.JSONDecodeError:
            brut = {}
    if isinstance(brut, dict):
        trouve = brut.get("resultUrls") or brut.get("result_urls") or []
        if isinstance(trouve, str):
            trouve = [trouve]
        urls = list(trouve)
        objet = brut.get("resultObject") or brut.get("result_object")
        if not urls and isinstance(objet, dict):
            for cle_possible in ("resultUrls", "url", "videoUrl", "imageUrl"):
                valeur = objet.get(cle_possible)
                if isinstance(valeur, str):
                    urls = [valeur]
                    break
                if isinstance(valeur, list):
                    urls = list(valeur)
                    break
    erreur = ""
    if etat == "fail":
        erreur = f"{data.get('failCode') or ''} {data.get('failMsg') or ''}".strip() or "échec sans détail"
    return {
        "etat": etat,
        "urls": urls,
        "erreur": erreur,
        "credits": data.get("creditsConsumed"),
        "progression": data.get("progress"),
        "taskId": data.get("taskId"),
    }


def etat_tache(task_id: str, conf: dict, cle: str) -> dict:
    url = (conf["api"]["base_url"] + CHEMIN_RECORD + "?" +
           urllib.parse.urlencode({"taskId": task_id}))
    return lire_resultat(_http("GET", url, None, cle, conf["api"]["timeout_s"]))


def attendre(task_id: str, conf: dict, cle: str, bavard: bool = True) -> dict:
    debut = time.time()
    intervalle = max(2, int(conf["api"]["intervalle_poll_s"]))
    plafond = int(conf["api"]["attente_max_s"])
    dernier = ""
    while True:
        etat = etat_tache(task_id, conf, cle)
        if etat["etat"] in ETATS_FINIS:
            return etat
        if bavard and etat["etat"] != dernier:
            dernier = etat["etat"]
            print(f"   … {etat['etat']}", flush=True)
        if time.time() - debut > plafond:
            etat["erreur"] = (f"toujours « {etat['etat']} » après {plafond} s — la tâche continue "
                              f"chez kie.ai, reprends-la avec : python kie.py etat {task_id}")
            return etat
        time.sleep(intervalle)


# --------------------------------------------------------------------------- garde-fous & journal

def estimer_cout(spec: dict, entree: dict, entree_video_s: float = None) -> tuple:
    """(crédits, explication). Les vidéos se facturent À LA SECONDE : coût = tarif × durée.
    Palier absent de la grille = MAJORANT (le tarif le plus cher du modèle) : on préfère un refus
    injuste à un batch qui vide le compte. Modèle sans grille = None, donc non protégé."""
    tarif = spec.get("tarif")
    if not isinstance(tarif, dict) or not isinstance(tarif.get("par"), dict) or not tarif["par"]:
        return None, "modèle non tarifé dans la config"
    grille = {str(k).lower(): v for k, v in tarif["par"].items()}
    cles = tarif.get("cles") or []
    clef = "|".join(str(entree.get(c)).lower() for c in cles)
    unite = grille.get(clef)
    note = ""
    if unite is None:
        unite = max(grille.values())
        note = f"palier « {clef or 'défaut'} » non tarifé → majorant {unite:g} "
    if tarif.get("mode") == "par_seconde":
        try:
            duree = int(entree.get(tarif.get("champ_duree", "duration"), 5))
        except (TypeError, ValueError):
            duree = 5
        grille_video = {str(k).lower(): v for k, v in (tarif.get("par_avec_video") or {}).items()}
        if entree.get("reference_video_urls") and grille_video:
            # kie.ai facture entrée + sortie au tarif « avec vidéo ». Durée d'entrée inconnue = on
            # prend le maximum autorisé (30 s) : majorant, jamais une estimation optimiste.
            entree_s = entree_video_s if entree_video_s is not None else 30.0
            u2 = grille_video.get(clef, max(grille_video.values()))
            total = math.ceil(entree_s) + duree
            return u2 * total, note + f"{u2:g} crédit(s)/s × ({math.ceil(entree_s)} s d'entrée vidéo + {duree} s)"
        return unite * duree, note + f"{unite:g} crédit(s)/s × {duree} s"
    return unite, note + f"{unite:g} crédit(s) par tirage"


def decision_depense(solde_actuel: float, cout_estime, garde_fous: dict, go: bool = False) -> tuple:
    """(autorisé, raison). Le coût inconnu ne bloque pas : seul le solde plancher fait foi."""
    minimum = garde_fous.get("solde_minimum") or 0
    plafond = garde_fous.get("credits_max_par_appel")
    if solde_actuel <= 0:
        return False, f"solde à {solde_actuel:g} crédit(s) : recharge avant de relancer."
    if cout_estime is not None and solde_actuel - cout_estime < minimum:
        return False, (f"solde {solde_actuel:g} − coût {cout_estime:g} passerait sous le plancher "
                       f"({minimum:g}). Relève le plancher ou recharge.")
    if cout_estime is None:
        if solde_actuel < minimum:
            return False, f"solde {solde_actuel:g} sous le plancher de {minimum:g} crédit(s)."
        if garde_fous.get("exiger_tarif") and not go:
            return False, ("coût inconnu : ce modèle n'a pas de tarif dans la config, le plancher "
                           "de solde ne peut donc rien garantir. Relève son prix sur kie.ai/pricing, "
                           "ou relance avec --go en connaissance de cause.")
    if plafond is not None and cout_estime is not None and cout_estime > plafond:
        if not go:
            return False, (f"coût estimé {cout_estime:g} crédits > plafond par appel ({plafond:g}). "
                           f"Relance avec --go si tu as validé la dépense.")
        return True, f"coût {cout_estime:g} > plafond {plafond:g}, forcé par --go."
    return True, f"solde {solde_actuel:g} crédit(s)."


CHAMPS_JOURNAL = ("projet", "plan", "essai", "motif", "resolution", "duree", "date", "taskId", "alias", "model", "type", "prompt", "cout_estime",
                  "etat", "credits", "fichiers")


def journaliser(ligne: dict, chemin: Path = None) -> None:
    """Liste blanche stricte : le journal n'écrit que des champs connus. Un secret glissé dans un
    champ imprévu ne peut pas atterrir sur le disque, même sous un nom anodin."""
    chemin = JOURNAL if chemin is None else Path(chemin)
    ligne = {k: v for k, v in ligne.items() if k in CHAMPS_JOURNAL}
    texte = masquer(json.dumps(ligne, ensure_ascii=False))
    try:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with chemin.open("a", encoding="utf-8") as f:
            f.write(texte + "\n")
    except OSError:
        pass  # un journal muet ne doit jamais faire échouer une génération payée


def nom_sortie(url: str, dossier: Path, prefixe: str = "kie", horodatage: str = None) -> Path:
    """Nom de fichier local. La tige est tronquée, JAMAIS l'extension : un .png coupé en « .p »
    n'est plus ouvrable d'un double-clic (ça s'est produit au premier tirage réel)."""
    nom = Path(urllib.parse.urlparse(url).path).name
    suffixe = Path(nom).suffix or ".bin"
    tige = Path(nom).stem[:40] or "resultat"
    horodatage = horodatage or f"{datetime.now():%Y%m%d-%H%M%S}"
    return Path(dossier) / f"{prefixe}-{horodatage}-{tige}{suffixe}"


def telecharger(url: str, dossier: Path, prefixe: str = "kie") -> Path:
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    cible = nom_sortie(url, dossier, prefixe)
    try:
        with urllib.request.urlopen(url, timeout=300) as reponse, cible.open("wb") as f:
            while True:
                bloc = reponse.read(1 << 16)
                if not bloc:
                    break
                f.write(bloc)
    except (urllib.error.URLError, OSError) as err:
        raise Refus(f"Téléchargement impossible ({url[:80]}…) : {err}")
    return cible


# --------------------------------------------------------------------------- commandes

def _apercu_requete(url: str, corps: dict) -> str:
    return ("POST " + url + "\n"
            "Authorization: Bearer ****\nContent-Type: application/json\n"
            + json.dumps(corps, ensure_ascii=False, indent=2))


def commande_generer(args, type_attendu: str) -> int:
    conf = charger_config()
    options = {
        "ratio": args.ratio, "format": getattr(args, "format", None),
        "resolution": args.resolution, "duree": args.duree, "mode": getattr(args, "mode", None),
        "ref": args.ref or None, "image_debut": getattr(args, "image_debut", None),
        "image_fin": getattr(args, "image_fin", None), "watermark": getattr(args, "watermark", None),
        "ref_video": getattr(args, "ref_video", None) or None,
        "ref_audio": getattr(args, "ref_audio", None) or None,
        "traduire": getattr(args, "traduire", None) or None,
        "audio": (None if getattr(args, "audio", None) is None else args.audio),
    }
    # Les chemins locaux passent par le dépôt kie.ai AVANT la construction : construire_requete
    # n'accepte que des URL, et c'est très bien ainsi.
    entree_video_s = duree_videos_locales(options.get("ref_video"))
    notes = resoudre_references(options, None if args.dry_run else lire_cle(), conf, args.dry_run)
    for note in notes:
        print("  " + note)
    corps = construire_requete(args.modele, args.prompt, options, conf, type_attendu, args.callback)
    url = conf["api"]["base_url"] + CHEMIN_CREATE

    if args.dry_run:
        cout, detail = estimer_cout(spec_dry := conf["modeles"][args.modele], corps["input"], entree_video_s)
        del spec_dry
        print("DRY-RUN — rien n'a été envoyé, aucun crédit consommé.")
        print("Coût estimé : " + ("inconnu" if cout is None else format(cout, "g") + " crédit(s)")
              + f" ({detail})\n")
        print(_apercu_requete(url, corps))
        return 0

    # Suivi des reprises : un plan déjà tiré deux fois ne repart pas sans que la raison soit écrite.
    essai = getattr(args, "essai", None)
    if essai is not None and essai >= 3 and not getattr(args, "motif", None):
        print(f"REFUSÉ — essai n° {essai} du plan « {getattr(args, 'plan', None) or '?'} » sans --motif. "
              "Écris ce qui n'allait pas dans les deux premiers et ce que ce tirage change.")
        return 1
    if type_attendu == "video" and not getattr(args, "plan", None):
        print("  Attention : tirage vidéo sans --projet / --plan / --essai, il ne pourra pas être compté dans le suivi des reprises.")
    cle = lire_cle()
    spec = conf["modeles"][args.modele]
    cout, detail = estimer_cout(spec, corps["input"], entree_video_s)
    restant = solde(conf, cle)
    ok, raison = decision_depense(restant, cout, conf["garde_fous"], args.go)
    print(f"Solde : {restant:g} crédit(s). Coût estimé : "
          f"{'inconnu' if cout is None else format(cout, 'g')} ({detail})"
          + ("" if cout is None else f" → resterait {restant - cout:g}."))
    if not ok:
        print("REFUSÉ — " + raison)
        return 1

    data = _payload(_http("POST", url, corps, cle, conf["api"]["timeout_s"])) or {}
    task_id = data.get("taskId")
    if not task_id:
        print("REFUSÉ — kie.ai n'a pas rendu de taskId.")
        return 1
    print(f"Tâche lancée : {task_id}  ({spec['model']})")
    journaliser({"date": datetime.now().isoformat(timespec="seconds"), "taskId": task_id,
                 "alias": args.modele, "model": spec["model"], "type": type_attendu,
                 "prompt": args.prompt, "cout_estime": cout,
                 "projet": getattr(args, "projet", None), "plan": getattr(args, "plan", None),
                 "essai": getattr(args, "essai", None), "motif": getattr(args, "motif", None),
                 "resolution": args.resolution, "duree": args.duree})

    if not args.attendre:
        print(f"Suivi : python kie.py etat {task_id}")
        return 0

    resultat = attendre(task_id, conf, cle)
    return _rendre(resultat, args, task_id)


def _rendre(resultat: dict, args, task_id: str) -> int:
    if resultat["etat"] != "success":
        print(f"ÉCHEC — état « {resultat['etat']} » : {masquer(resultat['erreur'])}")
        return 1
    credits = resultat.get("credits")
    print(f"OK — {len(resultat['urls'])} fichier(s)"
          + (f", {credits} crédit(s) consommé(s)." if credits is not None else "."))
    for u in resultat["urls"]:
        print("  " + u)
    if getattr(args, "sortie", None):
        for u in resultat["urls"]:
            chemin = telecharger(u, Path(args.sortie), prefixe=args.modele if hasattr(args, "modele") else "kie")
            print("  -> " + str(chemin))
    journaliser({"date": datetime.now().isoformat(timespec="seconds"), "taskId": task_id,
                 "etat": "success", "credits": credits, "fichiers": len(resultat["urls"])})
    return 0


def commande_solde(args) -> int:
    conf = charger_config()
    if args.dry_run:
        print("DRY-RUN — GET " + conf["api"]["base_url"] + CHEMIN_CREDIT + " (appel gratuit)")
        return 0
    restant = solde(conf, lire_cle())
    print(f"Solde kie.ai : {restant:g} crédit(s).")
    gf = conf["garde_fous"]
    print(f"Plancher configuré : {gf.get('solde_minimum') or 0:g} — plafond par appel : "
          f"{gf.get('credits_max_par_appel') if gf.get('credits_max_par_appel') is not None else 'aucun'}")
    return 0 if restant > (gf.get("solde_minimum") or 0) else 1


def commande_modeles(args) -> int:
    conf = charger_config()
    for alias in sorted(conf["modeles"], key=lambda a: (conf["modeles"][a].get("type", ""), a)):
        spec = conf["modeles"][alias]
        tarif = spec.get("tarif") or {}
        grille = tarif.get("par") or {}
        resume_tarif = ("non tarifé" if not grille else
                        ("de %g à %g cr/s" if tarif.get("mode") == "par_seconde" else "de %g à %g cr")
                        % (min(grille.values()), max(grille.values())))
        print(f"{spec.get('type', '?'):6s} {alias:18s} {spec['model']:24s} {resume_tarif}")
        print(f"       {spec.get('resume', '')}")
        print(f"       options : {', '.join('--' + o for o in sorted(spec.get('champs', {}))) or 'aucune'}")
    return 0


def commande_televerser(args) -> int:
    conf = charger_config()
    fichier = Path(args.fichier).expanduser()
    if args.dry_run:
        print("DRY-RUN — rien n'a été envoyé.")
        print(f"POST {conf['api'].get('upload_url', UPLOAD_URL)}  ({fichier.name}, "
              + (f"{fichier.stat().st_size / 1024:.0f} Ko)" if fichier.is_file() else "INTROUVABLE)"))
        return 0
    url, expire = televerser(fichier, lire_cle(), conf)
    print(url)
    print(f"(aucun crédit consommé" + (f", expire {expire}" if expire else "") + ")")
    return 0


def commande_etat(args) -> int:
    conf = charger_config()
    if args.dry_run:
        print("DRY-RUN — GET " + conf["api"]["base_url"] + CHEMIN_RECORD + "?taskId=" + args.task_id)
        return 0
    cle = lire_cle()
    resultat = attendre(args.task_id, conf, cle) if args.attendre else etat_tache(args.task_id, conf, cle)
    if resultat["etat"] != "success":
        print(f"état : {resultat['etat']}"
              + (f" — {masquer(resultat['erreur'])}" if resultat["erreur"] else "")
              + (f" ({resultat['progression']}%)" if resultat.get("progression") else ""))
        return 1 if resultat["etat"] == "fail" else 0
    return _rendre(resultat, args, args.task_id)


def _parseur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pont kie.ai — images et vidéos.")
    sous = p.add_subparsers(dest="commande", required=True)

    def commun(sp):
        sp.add_argument("--dry-run", action="store_true",
                        help="imprime la requête et s'arrête : aucune connexion, aucun crédit")
        return sp

    s = commun(sous.add_parser("solde", help="crédits restants (appel gratuit)"))
    s.set_defaults(fonction=commande_solde)

    m = sous.add_parser("modeles", help="modèles connus et leurs options (hors ligne)")
    m.set_defaults(fonction=commande_modeles, dry_run=True)

    def generation(nom, defaut, aide):
        sp = commun(sous.add_parser(nom, help=aide))
        sp.add_argument("prompt")
        sp.add_argument("--modele", default=defaut)
        sp.add_argument("--ratio")
        sp.add_argument("--resolution")
        sp.add_argument("--duree")
        sp.add_argument("--ref", action="append", default=[],
                        help="image de référence : URL, asset://…, ou CHEMIN LOCAL (téléversé tout seul). Répétable.")
        sp.add_argument("--callback", help="URL de webhook (optionnelle)")
        sp.add_argument("--sortie", help="dossier où télécharger le résultat")
        sp.add_argument("--go", action="store_true", help="passer outre le plafond par appel")
        sp.add_argument("--projet", help="suivi : nom du projet (ex. MARQUE-PRODUIT-V1)")
        sp.add_argument("--plan", help="suivi : nom du plan ou de l'image (ex. plan-03)")
        sp.add_argument("--essai", type=int, help="suivi : numéro du tirage pour ce plan (1, 2, 3…)")
        sp.add_argument("--motif", help="suivi : pourquoi on retire ce plan (obligatoire à partir du 3e essai)")
        sp.add_argument("--pas-attendre", dest="attendre", action="store_false", default=True)
        return sp

    i = generation("image", "nano-banana", "générer une image")
    i.add_argument("--format")
    i.set_defaults(fonction=lambda a: commande_generer(a, "image"))

    v = generation("video", "veo", "générer une vidéo")
    v.add_argument("--format", help="Seedance 2.5 : mp4 | mov")
    v.add_argument("--mode", help="Kling : std | pro | 4K")
    v.add_argument("--image-debut", dest="image_debut", help="Seedance : première image")
    v.add_argument("--image-fin", dest="image_fin", help="Seedance : dernière image")
    v.add_argument("--ref-video", dest="ref_video", action="append", default=None,
                   help="Seedance 2.5 : vidéo de référence (mouvement), chemin local ou URL. Répétable. "
                        "Exclusif avec --image-debut/--image-fin.")
    v.add_argument("--ref-audio", dest="ref_audio", action="append", default=None,
                   help="Seedance 2.5 : audio de référence (voix), chemin local ou URL. Répétable.")
    v.add_argument("--watermark", help="Veo : filigrane")
    v.add_argument("--traduire", action="store_true", default=None, help="Veo : traduire le prompt")
    audio = v.add_mutually_exclusive_group()
    audio.add_argument("--audio", dest="audio", action="store_true", default=None)
    audio.add_argument("--sans-audio", dest="audio", action="store_false")
    v.set_defaults(fonction=lambda a: commande_generer(a, "video"))

    u = commun(sous.add_parser("televerser", help="déposer un fichier local chez kie.ai (gratuit)"))
    u.add_argument("fichier")
    u.set_defaults(fonction=commande_televerser)

    e = commun(sous.add_parser("etat", help="état d'une tâche (appel gratuit)"))
    e.add_argument("task_id")
    e.add_argument("--sortie", help="dossier où télécharger si la tâche est finie")
    e.add_argument("--attendre", action="store_true", help="rester jusqu'à la fin de la tâche")
    e.set_defaults(fonction=commande_etat, modele="kie")

    r = commun(sous.add_parser("recuperer", help="télécharger le résultat d'une tâche finie"))
    r.add_argument("task_id")
    r.add_argument("--sortie", required=True)
    r.set_defaults(fonction=commande_etat, attendre=False, modele="kie")
    return p


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = _parseur().parse_args(argv)
    try:
        return args.fonction(args)
    except Refus as refus:
        print("REFUSÉ — " + masquer(str(refus)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
