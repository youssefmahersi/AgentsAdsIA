#!/usr/bin/env python3
r"""
LECTEUR AGENTSADS — lecteur web local, en lecture seule, des fichiers .md du projet.

    python3 outils/lecteur.py              # ouvre http://127.0.0.1:8765 dans le navigateur
    python3 outils/lecteur.py --port 9000 --no-browser

Ce qu'il lit : le dossier du projet, ~/.claude/agents (fiches des agents) et ~/.claude/skills.
Ce qu'il sert : uniquement des fichiers .md et des images (png, jpg, webp, gif, svg), jamais un
autre type de fichier, jamais un fichier caché, jamais hors de ces trois dossiers.
Il écoute seulement sur 127.0.0.1 : rien n'est accessible depuis un autre appareil.
Il ne modifie aucun fichier. Aucune dépendance : Python standard uniquement.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PROJET = Path(__file__).resolve().parent.parent
RACINES = {
    "projet": PROJET,
    "agents": Path.home() / ".claude" / "agents",
    "skills": Path.home() / ".claude" / "skills",
}
PAGE = Path(__file__).resolve().parent / "lecteur" / "index.html"

EXT_MD = {".md"}
EXT_IMG = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
TYPES_IMG = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}
IGNORES = {"node_modules", "__pycache__"}

TAG_ATTENTE = re.compile(r"\[(À VÉRIFIER|À DÉCIDER|À CONFIRMER|À FOURNIR)\]")


# --------------------------------------------------------------------------- fichiers

def lister():
    """Tous les .md et images autorisés : liste de dicts {id, kind, mtime, size}."""
    sortie = []
    for rid, base in RACINES.items():
        if not base.is_dir():
            continue
        for dossier, sous, fichiers in os.walk(base):
            sous[:] = sorted(d for d in sous if not d.startswith(".") and d not in IGNORES)
            for nom in sorted(fichiers):
                if nom.startswith("."):
                    continue
                p = Path(dossier) / nom
                ext = p.suffix.lower()
                if ext not in EXT_MD and ext not in EXT_IMG:
                    continue
                try:
                    st = p.stat()
                except OSError:
                    continue
                sortie.append({"id": f"{rid}/{p.relative_to(base).as_posix()}",
                               "kind": "md" if ext in EXT_MD else "img",
                               "mtime": st.st_mtime, "size": st.st_size})
    return sortie


def resoudre(ident: str):
    """Identifiant « racine/chemin » → Path sûr, ou None."""
    rid, _, rel = (ident or "").partition("/")
    base = RACINES.get(rid)
    if base is None or not rel:
        return None
    base = base.resolve()
    try:
        p = (base / rel).resolve()
        parts = p.relative_to(base).parts
    except (ValueError, OSError):
        return None
    if any(x.startswith(".") for x in parts) or any(x in IGNORES for x in parts):
        return None
    if p.suffix.lower() not in EXT_MD | EXT_IMG or not p.is_file():
        return None
    return p


def lire_md(ident: str):
    p = resoudre(ident)
    if p is None or p.suffix.lower() not in EXT_MD:
        return None
    return p, p.read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- vues

def version():
    fichiers = lister()
    return {"v": f"{len(fichiers)}-{max((f['mtime'] for f in fichiers), default=0):.3f}"}


def recherche(q: str, limite: int = 80):
    q = (q or "").strip()
    if len(q) < 2:
        return {"q": q, "resultats": []}
    bas = q.lower()
    resultats = []
    for f in lister():
        if f["kind"] != "md":
            continue
        lu = lire_md(f["id"])
        if not lu:
            continue
        lignes = lu[1].splitlines()
        touches = [(i + 1, l.strip()) for i, l in enumerate(lignes) if bas in l.lower()]
        nom_touche = bas in f["id"].lower()
        if touches or nom_touche:
            resultats.append({"id": f["id"], "lignes": [{"n": n, "texte": t[:240]} for n, t in touches[:5]],
                              "total": len(touches)})
    resultats.sort(key=lambda r: (-r["total"], r["id"]))
    return {"q": q, "resultats": resultats[:limite]}


def a_faire():
    """Points en attente dans les fiches produits et les livraisons (hors concurrents)."""
    groupes = []
    for f in lister():
        fid = f["id"]
        if f["kind"] != "md" or not (fid.startswith("projet/produits/") or fid.startswith("projet/livraisons/")):
            continue
        if fid.startswith("projet/produits/_"):
            continue
        lu = lire_md(fid)
        if not lu:
            continue
        items = []
        for i, ligne in enumerate(lu[1].splitlines(), 1):
            if ligne.lstrip().startswith(">"):
                continue
            tags = TAG_ATTENTE.findall(ligne)
            if tags:
                items.append({"n": i, "texte": ligne.strip()[:300], "tags": sorted(set(tags))})
        if items:
            groupes.append({"id": fid, "items": items})
    return {"groupes": groupes, "total": sum(len(g["items"]) for g in groupes)}


def tableau_de_bord():
    fichiers = lister()
    images = [f["id"] for f in fichiers if f["kind"] == "img"]
    produits = []
    dossier = PROJET / "produits"
    if dossier.is_dir():
        for d in sorted(dossier.iterdir()):
            if not d.is_dir() or d.name.startswith((".", "_")):
                continue
            slug = d.name
            fiche_id = f"projet/produits/{slug}/PRODUIT.md"
            lu = lire_md(fiche_id)
            texte = lu[1] if lu else ""
            titre = next((l[2:].strip() for l in texte.splitlines() if l.startswith("# ")), slug)
            prix = ""
            for l in texte.splitlines():
                if "**Prix de vente**" in l:
                    prix = l.split(":", 1)[-1].strip()
                    break
            attente = {}
            for t in TAG_ATTENTE.findall("\n".join(l for l in texte.splitlines() if not l.lstrip().startswith(">"))):
                attente[t] = attente.get(t, 0) + 1
            livraisons = sorted({i.split("/")[2] for i in images
                                 if i.startswith("projet/livraisons/") and len(i.split("/")) > 4
                                 and i.split("/")[3] == slug}, reverse=True)
            creas = [i for i in images if i.startswith("projet/livraisons/") and len(i.split("/")) > 4
                     and i.split("/")[3] == slug]
            packshots = [i for i in images if i.startswith(f"projet/produits/{slug}/packshots/")]
            produits.append({"slug": slug, "titre": titre, "fiche": fiche_id if lu else None, "prix": prix,
                             "attente": attente, "livraisons": livraisons, "creas": creas[-6:],
                             "nb_creas": len(creas), "packshots": packshots[:8], "nb_packshots": len(packshots)})
    agents = [f["id"] for f in fichiers if f["id"].startswith("agents/") and f["kind"] == "md"]
    skills = sorted({f["id"].split("/")[1] for f in fichiers if f["id"].startswith("skills/") and f["id"].count("/") >= 2})
    return {"produits": produits, "agents": agents, "nb_skills": len(skills), "a_faire": a_faire()["total"]}


# --------------------------------------------------------------------------- HTTP

class Gestionnaire(BaseHTTPRequestHandler):
    server_version = "LecteurAgentsAds/1.0"

    def log_message(self, *args):
        pass

    def _envoyer(self, code: int, corps: bytes, type_: str, cache: bool = False):
        self.send_response(code)
        self.send_header("Content-Type", type_)
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "max-age=300" if cache else "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(corps)

    def _json(self, obj, code: int = 200):
        self._envoyer(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        url = urlparse(self.path)
        qs = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path in ("/", "/index.html"):
                self._envoyer(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif url.path in ("/favicon.ico", "/favicon.png", "/icone.png"):
                nom = "icone-512.png" if url.path == "/icone.png" else "favicon.png"
                self._envoyer(200, (PAGE.parent / nom).read_bytes(), "image/png", cache=True)
            elif url.path == "/api/fichiers":
                self._json({"racines": {k: str(v) for k, v in RACINES.items()}, "fichiers": lister()})
            elif url.path == "/api/version":
                self._json(version())
            elif url.path == "/api/fichier":
                lu = lire_md(qs.get("id", ""))
                if not lu:
                    return self._json({"erreur": "Fichier introuvable."}, 404)
                p, texte = lu
                self._json({"id": qs["id"], "chemin": str(p), "texte": texte, "mtime": p.stat().st_mtime})
            elif url.path == "/brut":
                p = resoudre(qs.get("id", ""))
                if p is None or p.suffix.lower() not in EXT_IMG:
                    return self._envoyer(404, b"introuvable", "text/plain; charset=utf-8")
                self._envoyer(200, p.read_bytes(), TYPES_IMG[p.suffix.lower()], cache=True)
            elif url.path == "/api/recherche":
                self._json(recherche(qs.get("q", "")))
            elif url.path == "/api/a-faire":
                self._json(a_faire())
            elif url.path == "/api/tableau":
                self._json(tableau_de_bord())
            else:
                self._envoyer(404, b"introuvable", "text/plain; charset=utf-8")
        except (BrokenPipeError, ConnectionResetError):
            pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lecteur web local des fichiers .md du projet AgentsAds.")
    ap.add_argument("--port", type=int, default=3000)
    ap.add_argument("--no-browser", action="store_true", help="ne pas ouvrir le navigateur")
    args = ap.parse_args(argv)
    serveur = ThreadingHTTPServer(("127.0.0.1", args.port), Gestionnaire)
    adresse = f"http://127.0.0.1:{args.port}"
    print(f"Lecteur AgentsAds : {adresse}  (Ctrl + C pour arrêter)", flush=True)
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(adresse)).start()
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêté.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
