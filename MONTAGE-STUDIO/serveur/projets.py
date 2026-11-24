"""Projets de montage (fiche de montage = projet JSON). Chaque enregistrement crée une nouvelle version
(v001, v002…) ; une version existante n'est jamais réécrite."""
import json
import re
from pathlib import Path

from .commun import (EXT_IMAGE, PROJET_ADS, PROJETS, chemin_media, maintenant, nouvel_id, probe_cache,
                     relatif)

FORMAT_DEFAUT = {"largeur": 1080, "hauteur": 1920, "ips": 30}
RE_ID = re.compile(r"^[A-Za-z0-9_\-]{1,60}$")


def _dossier(pid: str) -> Path:
    if not RE_ID.match(pid or ""):
        raise ValueError("identifiant de projet invalide")
    return PROJETS / pid


def versions(pid: str) -> list:
    d = _dossier(pid) / "versions"
    return sorted(p.stem for p in d.glob("v[0-9][0-9][0-9].json")) if d.exists() else []


def lister() -> list:
    sortie = []
    for d in sorted(PROJETS.iterdir()) if PROJETS.exists() else []:
        if d.is_dir() and versions(d.name):
            v = versions(d.name)[-1]
            data = json.loads((d / "versions" / f"{v}.json").read_text())
            sortie.append({"id": d.name, "nom": data.get("nom", d.name), "version": v,
                           "nb_versions": len(versions(d.name)), "plans": len(data.get("plans", [])),
                           "modifie": data.get("enregistre")})
    return sortie


def charger(pid: str, version: str = None) -> dict:
    vs = versions(pid)
    if not vs:
        raise FileNotFoundError("projet introuvable")
    v = version if version in vs else vs[-1]
    data = json.loads((_dossier(pid) / "versions" / f"{v}.json").read_text())
    data["id"], data["version"], data["versions"] = pid, v, vs
    return data


def enregistrer(pid: str, data: dict, note: str = "") -> str:
    """Nouvelle version, toujours. Renvoie son nom."""
    d = _dossier(pid) / "versions"
    d.mkdir(parents=True, exist_ok=True)
    vs = versions(pid)
    n = int(vs[-1][1:]) + 1 if vs else 1
    nom = f"v{n:03d}"
    propre = {k: v for k, v in data.items() if k not in ("versions", "_extrait_debut")}
    propre.update(id=pid, version=nom, enregistre=maintenant(), note=note)
    cible = d / f"{nom}.json"
    if cible.exists():   # ceinture et bretelles : jamais d'écrasement
        raise FileExistsError(nom)
    cible.write_text(json.dumps(propre, ensure_ascii=False, indent=1))
    return nom


def plan_depuis_media(chemin: str, idx: int) -> dict:
    p = chemin_media(chemin)
    info = probe_cache(p)
    if p.suffix.lower() in EXT_IMAGE:
        return {"id": f"p{idx}", "source": relatif(p), "type": "image", "duree": 2.0, "debut": 0, "fin": 2.0,
                "vitesse": 1, "volume": 1, "effets": [], "look": None}
    return {"id": f"p{idx}", "source": relatif(p), "type": "video", "debut": 0.0,
            "fin": round(info.get("duree") or 3.0, 3), "duree_source": round(info.get("duree") or 0, 3),
            "vitesse": 1, "volume": 1, "effets": [], "look": None}


def creer(nom: str, medias: list, sons: list = None) -> str:
    base = re.sub(r"[^A-Za-z0-9_\-]+", "-", nom).strip("-")[:40] or "projet"
    pid = base
    i = 2
    while (PROJETS / pid).exists():
        pid = f"{base}-{i}"
        i += 1
    plans = [plan_depuis_media(m, i + 1) for i, m in enumerate(medias)]
    data = {"nom": nom, "format": dict(FORMAT_DEFAUT), "plans": plans, "transitions": [], "textes": [],
            "sons": [{"id": f"s{i + 1}", "source": relatif(chemin_media(s)), "type": "musique", "debut": 0,
                      "volume": 0.6} for i, s in enumerate(sons or [])]}
    enregistrer(pid, data, "création")
    return pid


def importer_b0002() -> str:
    """Premier projet de test : le remake B0002 (plans 480p de ziad + mix son à −14 LUFS)."""
    if (PROJETS / "B0002-remake").exists():
        return "B0002-remake"
    racine = "produits/poele-titane/videos/_travail/B0002_remake_titanox"
    plans = []
    for i, (f, debut, fin, vitesse) in enumerate([("P1_480_e2.mp4", 0, 3.0, 0.957), ("P2_480_e1.mp4", 0, 2.467, 1),
                                                  ("P3_480_e2.mp4", 0, 2.0, 1.25), ("P4_480_e2.mp4", 0, 2.433, 1),
                                                  ("P5_480_e1.mp4", 0.5, 1.1, 1)], 1):
        p = plan_depuis_media(f"{racine}/vid/{f}", i)
        p.update(debut=debut, fin=fin, vitesse=vitesse)
        plans.append(p)
    data = {"nom": "B0002 · remake Titanox (poêle titane)", "format": dict(FORMAT_DEFAUT), "plans": plans,
            "transitions": [], "textes": [],
            "sons": [{"id": "s1", "source": f"{racine}/son/mix_-14.wav", "type": "voix", "debut": 0, "volume": 1.0}],
            "source_montage": f"{racine}/montage/graph.txt"}
    pid = "B0002-remake"
    enregistrer(pid, data, "import du remake de ziad")
    return pid


# --------------------------------------------------------------------------- repères

def reperes(pid: str) -> list:
    f = _dossier(pid) / "markers.json"
    return json.loads(f.read_text()) if f.exists() else []


def ajouter_repere(pid: str, t: float, texte: str, plan: str = None) -> dict:
    liste = reperes(pid)
    r = {"id": nouvel_id("rep-"), "t": round(float(t), 3), "texte": texte[:1000], "plan": plan,
         "date": maintenant(), "statut": "nouveau"}
    liste.append(r)
    (_dossier(pid) / "markers.json").write_text(json.dumps(liste, ensure_ascii=False, indent=1))
    return r


def retirer_repere(pid: str, rid: str) -> None:
    liste = [r for r in reperes(pid) if r["id"] != rid]
    (_dossier(pid) / "markers.json").write_text(json.dumps(liste, ensure_ascii=False, indent=1))
