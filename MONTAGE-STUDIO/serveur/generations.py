"""Générations en direct : lit journal/kie.jsonl et journal/gemini.jsonl, suit l'état chez kie.ai,
prépare les relances à blanc et ne dépense qu'après la phrase de confirmation."""
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

from .commun import (CACHE, GEMINI, JOURNAUX, KIE, PROJET_ADS, STUDIO, ajouter_jsonl, lire_jsonl,
                     masquer, maintenant, nouvel_id, relatif)

PHRASE = "JE CONFIRME LA DEPENSE"
JOURNAL_STUDIO = CACHE / "relances.jsonl"   # ce que le studio a lancé (audit)
SORTIE_RELANCES = STUDIO / "generations"
ETATS_KIE = {"waiting": "en file", "queuing": "en file", "generating": "en cours",
             "success": "fini", "fail": "échec"}
_etat_direct = {}       # taskId -> {"etat":…, "progression":…, "vu": timestamp}
_relances = {}          # id -> suivi des relances lancées depuis le studio
_verrou = threading.Lock()


def _date(txt):
    try:
        return datetime.fromisoformat(txt)
    except (TypeError, ValueError):
        return None


def _type_fichier(chemin: str) -> str:
    ext = Path(chemin).suffix.lower()
    return "video" if ext in {".mp4", ".mov", ".webm", ".m4v"} else "image"


def lister() -> list:
    taches = {}
    ordre = []
    for ligne in lire_jsonl(JOURNAUX / "kie.jsonl"):
        tid = ligne.get("taskId")
        if not tid:
            continue
        if tid not in taches:
            taches[tid] = {"id": tid, "fournisseur": "kie.ai", "etat": "envoyé", "fichiers": [],
                           "urls": [], "credits": None, "cout_estime": None}
            ordre.append(tid)
        t = taches[tid]
        if "prompt" in ligne:   # ligne d'envoi
            t.update(date=ligne.get("date"), modele=ligne.get("model"), alias=ligne.get("alias"),
                     type=ligne.get("type"), prompt=masquer(ligne.get("prompt") or ""),
                     cout_estime=ligne.get("cout_estime"), projet=ligne.get("projet"),
                     plan=ligne.get("plan"), essai=ligne.get("essai"), motif=ligne.get("motif"),
                     resolution=ligne.get("resolution"), duree=ligne.get("duree"),
                     refs=ligne.get("refs"))
            if "image_debut" in ligne:
                t["image_debut"] = ligne["image_debut"]
        if ligne.get("etat"):   # ligne de retour
            t["etat"] = ETATS_KIE.get(ligne["etat"], ligne["etat"])
            t["fin"] = ligne.get("date")
            if ligne.get("credits") is not None:
                t["credits"] = ligne["credits"]
            if ligne.get("erreur"):
                t["erreur"] = masquer(ligne["erreur"])
            for c in ligne.get("chemins") or []:
                if c not in t["fichiers"]:
                    t["fichiers"].append(c)
            t["urls"] = ligne.get("urls") or t["urls"]
    with _verrou:
        for tid, d in _etat_direct.items():
            if tid in taches and taches[tid]["etat"] in ("envoyé", "en file", "en cours"):
                taches[tid]["etat"] = d["etat"]
                taches[tid]["progression"] = d.get("progression")
    vieux = datetime.now() - timedelta(hours=48)
    for t in taches.values():
        d = _date(t.get("date"))
        if t["etat"] == "envoyé" and d and d < vieux:
            t["etat"] = "sans nouvelles"
    sortie = [taches[t] for t in ordre if taches[t].get("date")]

    for i, ligne in enumerate(lire_jsonl(JOURNAUX / "gemini.jsonl")):
        fichiers = ligne.get("fichiers") or []
        if isinstance(fichiers, int):
            fichiers = []
        sortie.append({
            "id": f"gemini-{i}", "fournisseur": "Gemini", "date": ligne.get("date"),
            "modele": ligne.get("modele"), "type": "image",
            "prompt": masquer(ligne.get("prompt") or ligne.get("prompt_debut") or ""),
            "etat": {"ok": "fini", "vide": "échec"}.get(ligne.get("statut"), ligne.get("statut") or "fini"),
            "cout_usd": ligne.get("cout_estime_usd"), "fichiers": [str(PROJET_ADS / f) if not Path(f).is_absolute() else f for f in fichiers],
            "urls": [], "ratio": ligne.get("ratio"), "refs": ligne.get("refs")})

    for t in sortie:
        t["fichiers"] = [{"chemin": relatif(Path(f)), "type": _type_fichier(f)}
                         for f in t["fichiers"] if Path(f).exists()]
        if not t.get("type"):
            t["type"] = "image"
    _rapprocher(sortie)
    sortie.sort(key=lambda t: t.get("date") or "", reverse=True)
    return sortie


def compteurs(taches: list) -> dict:
    return {"total": len(taches),
            "en_cours": sum(t["etat"] in ("envoyé", "en file", "en cours") for t in taches),
            "echecs": sum(t["etat"] == "échec" for t in taches),
            "credits": round(sum(float(t.get("credits") or 0) for t in taches), 1),
            "usd": round(sum(float(t.get("cout_usd") or 0) for t in taches), 3)}


_index = {"t": 0, "fichiers": []}


def _candidats():
    """Médias récents de produits/ et livraisons/ (index rafraîchi toutes les 30 s)."""
    if time.time() - _index["t"] < 30:
        return _index["fichiers"]
    liste = []
    for base in (PROJET_ADS / "produits", PROJET_ADS / "livraisons", STUDIO / "generations"):
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if f.suffix.lower() in {".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg", ".webp"} and "_concurrents" not in f.parts:
                try:
                    liste.append((f.stat().st_mtime, f))
                except OSError:
                    pass
    _index.update(t=time.time(), fichiers=liste)
    return liste


def _rapprocher(taches):
    """Générations d'avant le studio : le journal ne notait pas le fichier. On propose le fichier
    écrit juste après le retour de kie.ai (même type, 0 à 60 s plus tard), marqué « probable »."""
    pris = {f["chemin"] for t in taches for f in t["fichiers"]}
    for t in sorted(taches, key=lambda x: x.get("fin") or ""):
        if t["fichiers"] or t["etat"] != "fini" or t["fournisseur"] != "kie.ai" or not t.get("fin"):
            continue
        d = _date(t["fin"])
        if not d:
            continue
        ref = d.timestamp()
        video = t.get("type") == "video"
        meilleurs = sorted((abs(m - ref), f) for m, f in _candidats()
                           if -2 <= m - ref <= 60 and (f.suffix.lower() in {".mp4", ".mov", ".webm"}) == video)
        for _ecart, f in meilleurs:
            r = relatif(f)
            if r not in pris:
                pris.add(r)
                t["fichiers"] = [{"chemin": r, "type": "video" if video else "image", "probable": True}]
                break


# --------------------------------------------------------------------------- suivi chez kie.ai

def _env_python():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _interroger(tid: str):
    """Appel GRATUIT : `kie.py etat <id>`. Ne télécharge rien, ne dépense rien."""
    try:
        r = subprocess.run([sys.executable, str(KIE), "etat", tid],
                           capture_output=True, text=True, timeout=40, cwd=PROJET_ADS, env=_env_python())
    except subprocess.SubprocessError:
        return
    sortie = r.stdout + r.stderr
    m = re.search(r"état : (\w+)(?:.*?\((\d+)%\))?", sortie)
    if m and m.group(1) == "fail":
        # kie.py ne note pas les échecs vus par « etat » : on ajoute la ligne de retour (ajout seul)
        err = re.search(r"état : fail — (.*)", sortie)
        ajouter_jsonl(JOURNAUX / "kie.jsonl", {"date": maintenant(), "taskId": tid, "etat": "fail",
                                               "erreur": masquer(err.group(1).strip() if err else "")[:300]})
    if m:
        with _verrou:
            _etat_direct[tid] = {"etat": ETATS_KIE.get(m.group(1), m.group(1)),
                                 "progression": m.group(2), "vu": time.time()}
    # Si la tâche est finie, kie.py écrit lui-même la ligne de retour dans le journal.


def boucle_suivi(stop: threading.Event):
    premier = True
    while premier or not stop.wait(20):
        premier = False
        if not os.environ.get("KIE_API_KEY"):
            continue
        limite = datetime.now() - timedelta(hours=48)
        for t in lister():
            if t["fournisseur"] != "kie.ai" or t["etat"] not in ("envoyé", "en file", "en cours"):
                continue
            d = _date(t.get("date"))
            if d and d > limite:
                _interroger(t["id"])


# --------------------------------------------------------------------------- relances

def _commande(t: dict, prompt: str, essai: bool) -> list:
    sortie = SORTIE_RELANCES / datetime.now().strftime("%Y-%m-%d")
    cmd = [sys.executable, str(KIE), "video" if t.get("type") == "video" else "image", prompt,
           "--modele", t.get("alias") or "", "--projet", t.get("projet") or "studio",
           "--plan", (t.get("plan") or "relance"), "--motif", "relance depuis Studio Ads",
           "--sortie", str(sortie)]
    for opt, cle in (("--resolution", "resolution"), ("--duree", "duree")):
        if t.get(cle):
            cmd += [opt, str(t[cle])]
    if t.get("image_debut") and t.get("type") == "video":
        cmd += ["--image-debut", str(t["image_debut"])]
    for r in t.get("refs") or []:
        cmd += ["--ref", str(r)]
    if essai:
        cmd.append("--dry-run")
    return cmd


def trouver(tid: str):
    for t in lister():
        if t["id"] == tid:
            return t
    return None


def preparer(tid: str, prompt: str) -> dict:
    t = trouver(tid)
    if not t:
        return {"ok": False, "message": "Génération introuvable."}
    if t["fournisseur"] != "kie.ai" or not t.get("alias"):
        return {"ok": False, "message": "La relance depuis le studio marche pour kie.ai. "
                                        "Pour Gemini, demande à karim ou hamid dans Claude."}
    cmd = _commande(t, prompt, essai=True)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=PROJET_ADS, env=_env_python())
    texte = masquer((r.stdout + "\n" + r.stderr).strip())
    cout = re.search(r"co[uû]t[^0-9]{0,30}([0-9]+(?:[.,][0-9]+)?)", texte, re.I)
    avert = None
    if t.get("type") == "video" and "image_debut" not in t:
        avert = ("Attention : cette génération date d'avant le studio, son image de départ et ses options "
                 "(son, références) n'étaient pas notées. La relance partirait sans image de départ.")
    return {"ok": r.returncode == 0, "apercu": texte[-4000:], "cout": cout.group(1) if cout else None,
            "avertissement": avert,
            "commande": " ".join(c if " " not in c else f"«{c[:60]}…»" for c in cmd[:3]) + " …"}


def lancer(tid: str, prompt: str, phrase: str) -> dict:
    if (phrase or "").strip().upper() != PHRASE:
        return {"ok": False, "message": f"Tape exactement « {PHRASE} » pour autoriser la dépense."}
    t = trouver(tid)
    if not t or t["fournisseur"] != "kie.ai" or not t.get("alias"):
        return {"ok": False, "message": "Relance impossible pour cette génération."}
    cmd = _commande(t, prompt, essai=False)
    rid = nouvel_id("relance-")
    log = CACHE / "relances" / f"{rid}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    ajouter_jsonl(JOURNAL_STUDIO, {"date": maintenant(), "id": rid, "depuis": tid, "modele": t.get("alias"),
                                   "prompt": prompt[:2000], "confirmation": PHRASE})

    def tourner():
        with log.open("w", encoding="utf-8") as f:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 cwd=PROJET_ADS, env=_env_python())
            _relances[rid] = {"etat": "en cours", "pid": p.pid}
            for ligne in p.stdout:
                f.write(masquer(ligne))
                f.flush()
            p.wait()
            _relances[rid] = {"etat": "fini" if p.returncode == 0 else "échec"}

    threading.Thread(target=tourner, daemon=True).start()
    return {"ok": True, "id": rid, "message": "Relance envoyée. Elle apparaîtra dans la liste dès que kie.ai l'accepte."}
