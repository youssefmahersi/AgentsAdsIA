"""Studio Ads : serveur local (FastAPI).

  .venv/bin/python -m serveur.app --mode mac       # 127.0.0.1 seulement
  .venv/bin/python -m serveur.app --mode iphone    # Wi-Fi local, code d'accès à 6 chiffres
"""
import argparse
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import threading
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import bibliotheque, generations, luts, ordres, projets, rendu, textes
from .commun import CACHE, EXPORTS, PROJET_ADS, WEB, chemin_media, forme_onde, probe_cache, relatif, vignette

app = FastAPI(title="Studio Ads", docs_url=None, redoc_url=None, openapi_url=None)
ETAT = {"mode": "mac", "port": 7880, "ip": None}
FICHIER_CODE = CACHE / "code_acces.json"
_essais = {}


# --------------------------------------------------------------------------- accès téléphone

def code_acces() -> str:
    if FICHIER_CODE.exists():
        return json.loads(FICHIER_CODE.read_text())["code"]
    code = f"{secrets.randbelow(10 ** 6):06d}"
    FICHIER_CODE.write_text(json.dumps({"code": code}))
    os.chmod(FICHIER_CODE, 0o600)
    return code


def _jeton(code: str) -> str:
    return hashlib.sha256(("studio-ads:" + code).encode()).hexdigest()


PAGE_CODE = """<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Studio Ads · code</title><style>body{background:#0E1014;color:#ECEDEF;font:16px -apple-system,system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}
form{background:#171A20;padding:28px;border-radius:16px;width:min(320px,90vw);text-align:center;border:1px solid #262A33}
h1{font-size:20px;margin:0 0 6px}p{color:#9AA0AA;font-size:14px;margin:0 0 18px}
input{font-size:28px;letter-spacing:8px;text-align:center;width:100%;box-sizing:border-box;padding:12px;border-radius:10px;border:1px solid #333;background:#0E1014;color:#fff}
button{margin-top:14px;width:100%;padding:12px;border-radius:10px;border:0;background:#2FD3B5;color:#06231D;font-weight:700;font-size:16px}
.err{color:#FF7A6B;margin-top:10px;font-size:14px}</style>
<form method="post" action="/code"><h1>Studio Ads</h1><p>Tape le code affiché sur ton Mac.</p>
<input name="code" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" autofocus autocomplete="one-time-code">
<button>Entrer</button>__ERR__</form></html>"""


def _local(request: Request) -> bool:
    return (request.client.host if request.client else "") in ("127.0.0.1", "::1", "localhost")


@app.middleware("http")
async def garde(request: Request, call_next):
    if _local(request) or request.url.path in ("/code", "/web/icones/icone-512.png"):
        return await call_next(request)
    if hmac.compare_digest(request.cookies.get("studio_acces", ""), _jeton(code_acces())):
        return await call_next(request)
    if request.url.path.startswith("/api") or request.method != "GET":
        return JSONResponse({"erreur": "code d'accès requis"}, status_code=401)
    return RedirectResponse("/code")


@app.get("/code")
def page_code():
    return HTMLResponse(PAGE_CODE.replace("__ERR__", ""))


@app.post("/code")
async def verifier_code(request: Request, code: str = Form("")):
    ip = request.client.host if request.client else "?"
    recents = [t for t in _essais.get(ip, []) if time.time() - t < 60]
    if len(recents) >= 5:
        return HTMLResponse(PAGE_CODE.replace("__ERR__", '<div class="err">Trop d\'essais. Attends une minute.</div>'), 429)
    if hmac.compare_digest(code.strip(), code_acces()):
        r = RedirectResponse("/", status_code=303)
        r.set_cookie("studio_acces", _jeton(code_acces()), httponly=True, samesite="strict", max_age=30 * 86400)
        return r
    _essais[ip] = recents + [time.time()]
    return HTMLResponse(PAGE_CODE.replace("__ERR__", '<div class="err">Code incorrect.</div>'), 401)


# --------------------------------------------------------------------------- pages et médias

app.mount("/web", StaticFiles(directory=WEB), name="web")


@app.get("/")
def accueil():
    return FileResponse(WEB / "index.html", headers={"Cache-Control": "no-store"})


def _media(chemin: str) -> Path:
    try:
        p = chemin_media(chemin)
    except ValueError as e:
        raise HTTPException(403, str(e))
    if not p.exists():
        raise HTTPException(404, "fichier introuvable")
    return p


@app.get("/media")
def media(chemin: str):
    return FileResponse(_media(chemin))


@app.get("/vignette")
def route_vignette(chemin: str, t: float = 0.0, l: int = 240):
    return FileResponse(vignette(_media(chemin), t, max(60, min(l, 720))), headers={"Cache-Control": "max-age=86400"})


@app.get("/onde")
def route_onde(chemin: str):
    p = _media(chemin)
    if "audio_hz" not in probe_cache(p):
        raise HTTPException(404, "pas de son")
    return FileResponse(forme_onde(p), headers={"Cache-Control": "max-age=86400"})


@app.get("/api/media/info")
def media_info(chemin: str):
    p = _media(chemin)
    return {"chemin": relatif(p), **probe_cache(p)}


@app.get("/api/etat")
def etat():
    return {"mode": ETAT["mode"], "ip": ETAT["ip"], "port": ETAT["port"],
            "cle_kie": bool(os.environ.get("KIE_API_KEY")), "messagerie": False,
            "lecteur": "http://127.0.0.1:8765/"}


# --------------------------------------------------------------------------- générations

@app.get("/api/generations")
def route_generations():
    liste = generations.lister()
    return {"liste": liste, "compteurs": generations.compteurs(liste), "phrase": generations.PHRASE}


@app.post("/api/generations/preparer")
async def route_preparer(request: Request):
    d = await request.json()
    return generations.preparer(d.get("id"), d.get("prompt") or "")


@app.post("/api/generations/lancer")
async def route_lancer_gen(request: Request):
    d = await request.json()
    return generations.lancer(d.get("id"), d.get("prompt") or "", d.get("phrase") or "")


# --------------------------------------------------------------------------- projets

@app.get("/api/projets")
def route_projets():
    return projets.lister()


@app.post("/api/projets")
async def route_creer(request: Request):
    d = await request.json()
    try:
        pid = projets.creer(d.get("nom") or "Nouveau projet", d.get("medias") or [], d.get("sons") or [])
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"id": pid}


@app.get("/api/projets/{pid}")
def route_projet(pid: str, version: str = None):
    try:
        p = projets.charger(pid, version)
    except (FileNotFoundError, ValueError):
        raise HTTPException(404, "projet introuvable")
    for pl in p.get("plans", []):
        if pl.get("type") != "image":
            info = probe_cache(chemin_media(pl["source"]))
            pl["duree_source"] = round(info.get("duree") or pl.get("fin", 0), 3)
            pl["a_son"] = "audio_hz" in info
    return {"projet": p, "disposition": rendu.disposition(p), "reperes": projets.reperes(pid)}


@app.post("/api/projets/{pid}/enregistrer")
async def route_enregistrer(pid: str, request: Request):
    d = await request.json()
    try:
        v = projets.enregistrer(pid, d["projet"], d.get("note", ""))
    except (ValueError, KeyError) as e:
        raise HTTPException(400, str(e))
    return {"version": v}


@app.post("/api/disposition")
async def route_disposition(request: Request):
    return rendu.disposition(await request.json())


@app.get("/api/projets/{pid}/reperes")
def route_reperes(pid: str):
    return projets.reperes(pid)


@app.post("/api/projets/{pid}/reperes")
async def route_ajout_repere(pid: str, request: Request):
    d = await request.json()
    r = projets.ajouter_repere(pid, d.get("t", 0), d.get("texte", ""), d.get("plan"))
    ordres.ajouter(f"REPÈRE : {r['texte']}", projet=pid, timecode=r["t"], plan=r["plan"], nature="repère")
    return r


@app.delete("/api/projets/{pid}/reperes/{rid}")
def route_suppr_repere(pid: str, rid: str):
    projets.retirer_repere(pid, rid)
    return {"ok": True}


# --------------------------------------------------------------------------- rendus et exports

@app.post("/api/rendu")
async def route_rendu(request: Request):
    d = await request.json()
    try:
        t = rendu.lancer(d["projet"], d.get("preset", "apercu"), float(d.get("extrait_debut") or 0))
    except (ValueError, KeyError) as e:
        raise HTTPException(400, str(e))
    return t.dict()


@app.post("/api/projets/{pid}/script")
def route_script(pid: str):
    return rendu.lancer_script(projets.charger(pid)).dict()


@app.get("/api/rendus")
def route_rendus():
    return sorted((t.dict() for t in rendu.TRAVAUX.values()), key=lambda t: t["debut"], reverse=True)


@app.get("/api/rendus/{tid}/journal")
def route_journal_rendu(tid: str):
    t = rendu.TRAVAUX.get(tid)
    if not t:
        raise HTTPException(404)
    return {"texte": t.log.read_text()[-6000:] if t.log.exists() else ""}


@app.post("/api/rendus/{tid}/{action}")
def route_pause(tid: str, action: str):
    if action not in ("pause", "reprendre"):
        raise HTTPException(400)
    return {"ok": rendu.mettre_en_pause(tid, action == "pause")}


@app.get("/api/exports")
def route_exports():
    sortie = []
    for f in sorted(EXPORTS.rglob("*.mp4"), key=lambda f: -f.stat().st_mtime):
        info = probe_cache(f)
        sortie.append({"chemin": relatif(f), "nom": f.name, "projet": f.parent.name, "duree": round(info.get("duree", 0), 2),
                       "dimensions": f"{info.get('largeur')}×{info.get('hauteur')}", "taille_mo": round(f.stat().st_size / 1048576, 2),
                       "date": f.stat().st_mtime})
    return sortie


# --------------------------------------------------------------------------- catalogue et aperçus

@app.get("/api/catalogue")
def route_catalogue():
    return {"transitions": {k: {"nom": v["nom"], "aide": v["aide"]} for k, v in rendu.TRANSITIONS.items()},
            "effets": rendu.EFFETS, "masques": rendu.MASQUES,
            "looks": {k: {"nom": v["nom"], "aide": v["aide"]} for k, v in luts.LOOKS.items()},
            "styles": {k: v["nom"] for k, v in textes.STYLES.items()}, "animations": textes.ANIMATIONS,
            "presets": {k: v["nom"] for k, v in rendu.PRESETS.items()}, "zone_sure": textes.ZONE_SURE}


@app.get("/apercu/transition")
def apercu_transition(type: str, a: str, b: str):
    return FileResponse(rendu.apercu_transition(type, _image_de(a), _image_de(b)), headers={"Cache-Control": "max-age=86400"})


def _image_de(chemin: str, t: float = 0.5) -> Path:
    p = _media(chemin)
    return p if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} else vignette(p, t, 540)


@app.get("/apercu/look")
def apercu_look(chemin: str, look: str, force: float = 1.0, t: float = 0.5):
    if look not in luts.LOOKS:
        raise HTTPException(404)
    return FileResponse(luts.apercu(_image_de(chemin, t), look, force, 0.0), headers={"Cache-Control": "max-age=86400"})


@app.get("/apercu/effet")
def apercu_effet(chemin: str, type: str, force: float = 0.6, t: float = 0.5):
    effet = {"type": type, "force": force, "x": 0.25, "y": 0.3, "l": 0.5, "h": 0.3}
    return FileResponse(rendu.apercu_effet(effet, _image_de(chemin, t)), headers={"Cache-Control": "max-age=86400"})


@app.get("/apercu/texte")
def apercu_texte(texte: str, style: str = "sous-titre", l: int = 1080, h: int = 1920, ancien: str = ""):
    return FileResponse(textes.rendre({"texte": texte, "style": style, "ancien": ancien}, l, h))


@app.get("/api/looks/test")
def route_test_peau(projet: str = None):
    """Planche chiffrée : échelle de peaux + 3 images du projet ouvert."""
    images = []
    try:
        for pl in projets.charger(projet).get("plans", [])[:3] if projet else []:
            t = 0 if pl.get("type") == "image" else (float(pl["debut"]) + float(pl["fin"])) / 2
            images.append(_image_de(pl["source"], t))
    except (FileNotFoundError, ValueError):
        pass
    return luts.test_peau(images)


@app.get("/cache/{sous}/{nom}")
def fichier_cache(sous: str, nom: str):
    if sous not in ("test_peau",) or "/" in nom or ".." in nom:
        raise HTTPException(404)
    f = CACHE / sous / nom
    if not f.exists():
        raise HTTPException(404)
    return FileResponse(f)


# --------------------------------------------------------------------------- ordres, références, bibliothèque

@app.get("/api/ordres")
def route_ordres():
    return ordres.lister()


@app.post("/api/ordres")
async def route_ajout_ordre(request: Request):
    d = await request.json()
    if not (d.get("texte") or "").strip():
        raise HTTPException(400, "message vide")
    return ordres.ajouter(d["texte"], d.get("projet"), d.get("timecode"), d.get("plan"), d.get("pieces"))


@app.post("/api/ordres/{oid}/statut")
async def route_statut(oid: str, request: Request):
    d = await request.json()
    return {"ok": ordres.changer_statut(oid, d.get("statut"))}


@app.get("/api/references")
def route_references():
    return bibliotheque.references()


@app.post("/api/references")
async def route_deposer(fichiers: list[UploadFile] = File(...), note: str = Form("")):
    dossier = bibliotheque.nouveau_dossier_reference(fichiers[0].filename if fichiers else "reference")
    for f in fichiers:
        nom = Path(f.filename or "video").name
        if Path(nom).suffix.lower() not in {".mp4", ".mov", ".m4v", ".webm", ".png", ".jpg", ".jpeg", ".webp"}:
            continue
        sous = Path(f.filename or nom).parent   # dossier glissé : on garde sa structure
        cible = dossier / Path(*[bibliotheque._propre(p) for p in sous.parts if p not in ("", ".", "..")]) / bibliotheque._propre(nom)
        cible.parent.mkdir(parents=True, exist_ok=True)
        with cible.open("wb") as out:
            while bloc := await f.read(1 << 20):
                out.write(bloc)
    return bibliotheque.enregistrer_reference(dossier, [], note)


@app.get("/api/creas")
def route_creas():
    liste = bibliotheque.creas()
    verdicts = {}
    for c in liste:
        if c["dossier"] not in verdicts:
            verdicts[c["dossier"]] = bibliotheque.lisezmoi(c["dossier"])
        c["controle"] = verdicts[c["dossier"]]
    return liste


@app.get("/api/fiches")
def route_fiches():
    return bibliotheque.fiches()


@app.get("/api/sons")
def route_sons():
    return bibliotheque.sons()


@app.post("/api/sons/importer")
async def route_importer_son(request: Request):
    d = await request.json()
    try:
        return {"chemin": bibliotheque.importer_son(d.get("chemin", ""))}
    except ValueError as e:
        raise HTTPException(400, str(e))


# --------------------------------------------------------------------------- démarrage

def ip_locale():
    r = subprocess.run(["route", "-n", "get", "default"], capture_output=True, text=True)
    defaut = [l.split(":")[1].strip() for l in r.stdout.splitlines() if "interface:" in l]
    for iface in defaut + ["en0", "en1"]:
        r = subprocess.run(["ipconfig", "getifaddr", iface], capture_output=True, text=True)
        if r.stdout.strip():
            return r.stdout.strip()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["mac", "iphone"], default="mac")
    ap.add_argument("--port", type=int, default=7880)
    a = ap.parse_args()
    ETAT.update(mode=a.mode, port=a.port)
    hote = "127.0.0.1"
    if a.mode == "iphone":
        ETAT["ip"] = ip_locale()
        hote = ETAT["ip"] or "127.0.0.1"
        code_acces()
    projets.importer_b0002()
    stop = threading.Event()
    threading.Thread(target=generations.boucle_suivi, args=(stop,), daemon=True).start()
    threading.Thread(target=luts.generer_pack, daemon=True).start()
    if a.mode == "iphone" and hote != "127.0.0.1":
        # le Mac lui-même garde l'accès sans code via 127.0.0.1
        cfg_local = uvicorn.Config(app, host="127.0.0.1", port=a.port, log_level="warning")
        threading.Thread(target=uvicorn.Server(cfg_local).run, daemon=True).start()
    uvicorn.run(app, host=hote, port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
