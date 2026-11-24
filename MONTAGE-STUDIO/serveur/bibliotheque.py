"""Bibliothèque : créas de l'équipe (livraisons, travail en cours), fiches produit, sons trouvés dans
les dossiers, références à reproduire."""
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

from . import ordres
from .commun import (EXT_AUDIO, EXT_IMAGE, EXT_VIDEO, INTERDITS, PROJET_ADS, REFERENCES, probe_cache,
                     relatif)

DOSSIERS_CREAS = ["livraisons", "produits", "MONTAGE-STUDIO/generations", "MONTAGE-STUDIO/exports"]
DOSSIERS_SONS = [PROJET_ADS, Path.home() / "Music", Path.home() / "Downloads"]
IGNORER_CREAS = {"frames", "planches", "captures", "img", "_travail_frames", "packaging", "points", "cache",
                 "sauvegardes", "lighthouse"}


def _parcourir(base: Path, exts: set, profondeur_max=7, ignorer=frozenset()):
    if not base.is_dir():
        return
    base_n = len(base.parts)
    for dossier, sous, fichiers in os.walk(base):
        d = Path(dossier)
        sous[:] = [s for s in sous if not s.startswith(".") and s not in INTERDITS and s not in ignorer
                   and len(d.parts) - base_n < profondeur_max]
        for f in fichiers:
            if not f.startswith(".") and Path(f).suffix.lower() in exts:
                yield d / f


def creas() -> list:
    """Images et vidéos produites, rangées par dossier, les plus récentes d'abord."""
    sortie = []
    for rel in DOSSIERS_CREAS:
        for f in _parcourir(PROJET_ADS / rel, EXT_IMAGE | EXT_VIDEO, ignorer=IGNORER_CREAS):
            try:
                st = f.stat()
            except OSError:
                continue
            if st.st_size < 2000:
                continue
            r = relatif(f)
            partie = r.split("/")
            produit = partie[2] if partie[0] == "livraisons" and len(partie) > 3 else (partie[1] if partie[0] == "produits" and len(partie) > 2 else partie[0])
            sortie.append({"chemin": r, "type": "video" if f.suffix.lower() in EXT_VIDEO else "image",
                           "dossier": str(Path(r).parent), "produit": produit, "date": st.st_mtime,
                           "taille": st.st_size, "livre": partie[0] == "livraisons",
                           "concurrent": "_concurrents" in partie})
    sortie.sort(key=lambda c: -c["date"])
    return sortie


def lisezmoi(dossier: str):
    """Verdict d'omar (PASS / CORRIGER) trouvé dans le LISEZ-MOI du dossier de livraison, s'il existe."""
    for nom in ("LISEZ-MOI.md", "README.md", "CONTROLE.md", "VERDICT.md"):
        f = PROJET_ADS / dossier / nom
        if f.exists():
            texte = f.read_text(errors="ignore")
            m = re.findall(r"(PASS|CORRIGER)", texte)
            return {"fichier": relatif(f), "verdict": m[-1] if m else None}
    return None


def fiches() -> list:
    out = []
    for nom in ("PRODUIT.md", "FICHE-SOURCE.md"):
        for f in _parcourir(PROJET_ADS / "produits", {".md"}):
            if f.name == nom:
                out.append({"chemin": relatif(f), "nature": "Fiche produit" if nom == "PRODUIT.md" else "Fiche source (karim)",
                            "date": f.stat().st_mtime})
    out.sort(key=lambda c: -c["date"])
    return out


def sons() -> list:
    vus, sortie = set(), []
    for base in DOSSIERS_SONS:
        for f in _parcourir(base, EXT_AUDIO, profondeur_max=6):
            if f in vus or "MONTAGE-STUDIO/cache" in str(f):
                continue
            vus.add(f)
            st = f.stat()
            sortie.append({"chemin": str(f), "nom": f.name, "dossier": str(f.parent).replace(str(Path.home()), "~"),
                           "dans_projet": PROJET_ADS in f.parents, "taille": st.st_size})
            if len(sortie) > 400:
                return sortie
    return sortie


def importer_son(chemin: str) -> str:
    """Copie un son trouvé hors du projet dans MONTAGE-STUDIO/sons/ (jamais d'écrasement)."""
    src = Path(chemin).expanduser().resolve()
    if src.suffix.lower() not in EXT_AUDIO or not src.exists():
        raise ValueError("son introuvable")
    if not any(src == b or b in src.parents for b in DOSSIERS_SONS):
        raise ValueError("dossier non autorisé")
    if PROJET_ADS in src.parents:
        return relatif(src)
    dest_dir = PROJET_ADS / "MONTAGE-STUDIO" / "sons"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    n = 2
    while dest.exists():
        dest = dest_dir / f"{src.stem}_{n}{src.suffix}"
        n += 1
    shutil.copy2(src, dest)
    return relatif(dest)


# --------------------------------------------------------------------------- références

def _propre(nom: str) -> str:
    return re.sub(r"[^A-Za-z0-9._\-]+", "-", nom).strip("-")[:60] or "video"


def nouveau_dossier_reference(nom: str) -> Path:
    d = REFERENCES / f"{datetime.now():%Y-%m-%d}_{_propre(Path(nom).stem)}"
    base, n = d, 2
    while d.exists():
        d = Path(f"{base}-{n}")
        n += 1
    d.mkdir(parents=True)
    return d


def enregistrer_reference(dossier: Path, fichiers: list, note: str = "") -> dict:
    """fichiers = [(nom, octets_iter)] déjà écrits dans `dossier`. Ajoute l'ordre « À REPRODUIRE »."""
    videos = [f for f in sorted(dossier.rglob("*")) if f.suffix.lower() in EXT_VIDEO | EXT_IMAGE]
    detail = []
    for v in videos:
        info = probe_cache(v)
        detail.append({"chemin": relatif(v), "duree": round(info.get("duree") or 0, 2),
                       "dimensions": f"{info.get('largeur')}×{info.get('hauteur')}" if info.get("largeur") else None})
    o = ordres.ajouter(f"À REPRODUIRE : {len(detail)} fichier(s) déposé(s) dans {relatif(dossier)}."
                       + (f" Note : {note}" if note else ""),
                       pieces=[d["chemin"] for d in detail], nature="à reproduire")
    return {"dossier": relatif(dossier), "fichiers": detail, "ordre": o["id"]}


def references() -> list:
    sortie = []
    for d in sorted(REFERENCES.iterdir(), reverse=True) if REFERENCES.exists() else []:
        if d.is_dir():
            fichiers = []
            for v in sorted(d.rglob("*")):
                if v.suffix.lower() in EXT_VIDEO | EXT_IMAGE:
                    info = probe_cache(v)
                    fichiers.append({"chemin": relatif(v), "duree": round(info.get("duree") or 0, 2),
                                     "type": "video" if v.suffix.lower() in EXT_VIDEO else "image"})
            sortie.append({"dossier": relatif(d), "nom": d.name, "fichiers": fichiers})
    return sortie
