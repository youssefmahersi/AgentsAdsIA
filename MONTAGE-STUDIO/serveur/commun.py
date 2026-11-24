"""Chemins, outils ffmpeg/ffprobe et petites aides partagées par tout le studio."""
import hashlib
import json
import os
import re
import secrets
import subprocess
import threading
from datetime import datetime
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent          # MONTAGE-STUDIO/
PROJET_ADS = STUDIO.parent                                # AgentsAds/
WEB = STUDIO / "web"
PROJETS = STUDIO / "projets"
LUTS = STUDIO / "luts"
REFERENCES = STUDIO / "references"
INBOX = STUDIO / "inbox"
EXPORTS = STUDIO / "exports"
CACHE = STUDIO / "cache"
JOURNAUX = PROJET_ADS / "journal"
KIE = PROJET_ADS / "outils" / "kie.py"
GEMINI = PROJET_ADS / "outils" / "gemini_image.py"

for d in (PROJETS, LUTS, REFERENCES, INBOX, EXPORTS, CACHE):
    d.mkdir(parents=True, exist_ok=True)

EXT_VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
EXT_IMAGE = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
EXT_AUDIO = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
EXT_MEDIA = EXT_VIDEO | EXT_IMAGE | EXT_AUDIO

# Dossiers où le studio a le droit de lire des médias (lecture seule hors MONTAGE-STUDIO).
RACINES_MEDIA = [PROJET_ADS]
INTERDITS = {".venv", ".git", "node_modules", "__pycache__", "config"}

POLICES = {
    "black": "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "normal": "/System/Library/Fonts/Supplemental/Arial.ttf",
}

SECRET = re.compile(r"(?i)(api[_-]?key|token|bearer|authorization|secret)[\"'=:\s]+[A-Za-z0-9._\-]{12,}")


def masquer(texte: str) -> str:
    """Retire tout ce qui ressemble à une clé avant affichage."""
    if not isinstance(texte, str):
        return texte
    texte = SECRET.sub(lambda m: m.group(1) + "=****", texte)
    for var in ("KIE_API_KEY", "GEMINI_API_KEY", "ELEVENLABS_API_KEY", "GOOGLE_API_KEY"):
        v = os.environ.get(var)
        if v and len(v) > 6:
            texte = texte.replace(v, "****")
    return texte


def maintenant() -> str:
    return datetime.now().isoformat(timespec="seconds")


def nouvel_id(prefixe: str = "") -> str:
    return prefixe + datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(2)


def chemin_media(valeur: str) -> Path:
    """Chemin relatif à AgentsAds (ou absolu) → Path sûr, sinon ValueError."""
    p = Path(valeur)
    if not p.is_absolute():
        p = PROJET_ADS / p
    p = p.resolve()
    if not any(p == r or r in p.parents for r in RACINES_MEDIA):
        raise ValueError("chemin hors du dossier AgentsAds")
    if any(part in INTERDITS for part in p.relative_to(PROJET_ADS).parts):
        raise ValueError("dossier non autorisé")
    if p.suffix.lower() not in EXT_MEDIA:
        raise ValueError("type de fichier non autorisé")
    return p


def relatif(p: Path) -> str:
    try:
        return Path(p).resolve().relative_to(PROJET_ADS).as_posix()
    except ValueError:
        return str(p)


def lire_jsonl(chemin: Path) -> list:
    lignes = []
    if not chemin.exists():
        return lignes
    with chemin.open(encoding="utf-8") as f:
        for brut in f:
            brut = brut.strip()
            if brut:
                try:
                    lignes.append(json.loads(brut))
                except json.JSONDecodeError:
                    pass
    return lignes


_verrou_ajout = threading.Lock()


def ajouter_jsonl(chemin: Path, ligne: dict) -> None:
    """Ajout seul : on n'écrit jamais au milieu d'un journal."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with _verrou_ajout, chemin.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")


def empreinte(*morceaux) -> str:
    h = hashlib.sha1()
    for m in morceaux:
        h.update(json.dumps(m, sort_keys=True, ensure_ascii=False, default=str).encode())
    return h.hexdigest()[:16]


def nom_libre(dossier: Path, tige: str, ext: str) -> Path:
    """Jamais d'écrasement : tige.ext, puis tige_v002.ext, tige_v003.ext…"""
    dossier.mkdir(parents=True, exist_ok=True)
    cible = dossier / f"{tige}{ext}"
    n = 1
    while cible.exists():
        n += 1
        cible = dossier / f"{tige}_v{n:03d}{ext}"
    return cible


def ffprobe(chemin: Path) -> dict:
    """Infos utiles d'un média : durée, dimensions, i/s, audio."""
    try:
        sortie = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
             "-of", "json", str(chemin)], capture_output=True, text=True, timeout=30).stdout
        data = json.loads(sortie or "{}")
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return {}
    info = {"duree": float(data.get("format", {}).get("duration") or 0),
            "taille": int(data.get("format", {}).get("size") or 0),
            "debit": int(data.get("format", {}).get("bit_rate") or 0)}
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and "largeur" not in info:
            num, _, den = (s.get("r_frame_rate") or "0/1").partition("/")
            info.update(largeur=s.get("width"), hauteur=s.get("height"), codec_video=s.get("codec_name"),
                        ips=round(float(num) / float(den or 1), 3) if float(den or 1) else 0)
        elif s.get("codec_type") == "audio" and "audio_hz" not in info:
            info.update(audio_hz=int(s.get("sample_rate") or 0), codec_audio=s.get("codec_name"),
                        canaux=s.get("channels"))
    return info


_cache_probe = {}


def probe_cache(chemin: Path) -> dict:
    try:
        cle = (str(chemin), chemin.stat().st_mtime)
    except OSError:
        return {}
    if cle not in _cache_probe:
        _cache_probe[cle] = ffprobe(chemin)
    return _cache_probe[cle]


def ffmpeg(args: list, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)],
                          capture_output=True, text=True, timeout=timeout)


def vignette(source: Path, t: float = 0.0, largeur: int = 240) -> Path:
    """Image fixe d'une vidéo (ou réduction d'une image), mise en cache."""
    sortie = CACHE / "vignettes" / f"{empreinte(str(source), source.stat().st_mtime, round(t, 2), largeur)}.jpg"
    if not sortie.exists():
        sortie.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() in EXT_IMAGE:
            ffmpeg(["-i", source, "-vf", f"scale={largeur}:-2", "-frames:v", "1", sortie])
        else:
            ffmpeg(["-ss", max(0.0, t), "-i", source, "-vf", f"scale={largeur}:-2", "-frames:v", "1", sortie])
            if not sortie.exists():  # instant au-delà de la fin : on prend la première image
                ffmpeg(["-i", source, "-vf", f"scale={largeur}:-2", "-frames:v", "1", sortie])
    return sortie


def forme_onde(source: Path, largeur: int = 1200, hauteur: int = 80, couleur: str = "0x7FD1C7") -> Path:
    sortie = CACHE / "ondes" / f"{empreinte(str(source), source.stat().st_mtime, largeur, hauteur, couleur)}.png"
    if not sortie.exists():
        sortie.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg(["-i", source, "-filter_complex",
                f"aformat=channel_layouts=mono,showwavespic=s={largeur}x{hauteur}:colors={couleur}:scale=sqrt",
                "-frames:v", "1", sortie])
    return sortie
