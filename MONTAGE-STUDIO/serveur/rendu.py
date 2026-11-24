"""Rendu ffmpeg d'un projet : plans → transitions → textes → sons (voix, musique baissée sous la voix)
→ son normalisé à −14 LUFS → exports. Rien n'est jamais écrasé ; aucun processus n'est jamais tué
(pause / reprise seulement) ; deux rendus lourds au maximum en même temps."""
import json
import math
import os
import re
import signal
import subprocess
import threading
import time
from pathlib import Path

from . import luts, textes
from .commun import (CACHE, EXPORTS, EXT_IMAGE, PROJET_ADS, chemin_media, empreinte, ffprobe,
                     maintenant, nom_libre, nouvel_id, probe_cache, relatif)

TRANSITIONS = {
    "coupe": {"nom": "Coupe", "xfade": None, "aide": "Passage sec d'un plan à l'autre."},
    "fondu": {"nom": "Fondu", "xfade": "fade", "aide": "Les deux plans se mélangent doucement."},
    "noir": {"nom": "Fondu au noir", "xfade": "fadeblack", "aide": "Passe par le noir. Exemple : changement de scène."},
    "blanc": {"nom": "Flash blanc", "xfade": "fadewhite", "aide": "Éclair blanc, effet « révélation »."},
    "zoom": {"nom": "Zoom", "xfade": "zoomin", "aide": "On plonge dans le plan suivant."},
    "punch": {"nom": "Punch-in", "xfade": "zoomin", "duree": 0.15, "aide": "Zoom très rapide qui donne du rythme."},
    "push": {"nom": "Push", "xfade": "smoothleft", "aide": "Le nouveau plan pousse l'ancien vers la gauche."},
    "glisse": {"nom": "Glissé", "xfade": "slideleft", "aide": "Le nouveau plan glisse par-dessus."},
    "glisse-haut": {"nom": "Glissé vers le haut", "xfade": "slideup", "aide": "Comme un swipe TikTok."},
    "flou": {"nom": "Flou de mouvement", "xfade": "hblur", "aide": "Passage flou et rapide, effet vitesse."},
    "cercle": {"nom": "Ouverture en cercle", "xfade": "circleopen", "aide": "Le plan suivant s'ouvre en cercle."},
    "rideau": {"nom": "Volet", "xfade": "wipeleft", "aide": "Un volet balaie l'image."},
    "pixels": {"nom": "Pixels", "xfade": "pixelize", "aide": "Effet numérique pixelisé."},
    "dissous": {"nom": "Dissolution", "xfade": "dissolve", "aide": "Grain qui se dissout."},
}

EFFETS = {
    "flou": {"nom": "Flou", "aide": "Rend l'image floue. Exemple : fond derrière un texte."},
    "glow": {"nom": "Glow", "aide": "Halo lumineux doux sur les zones claires."},
    "grain": {"nom": "Grain", "aide": "Grain de pellicule, rend l'image plus « vraie »."},
    "leak": {"nom": "Light leak", "aide": "Fuite de lumière orangée sur le bord."},
    "aberration": {"nom": "Aberration chromatique", "aide": "Décalage rouge / bleu façon caméra cheap."},
    "vignette": {"nom": "Vignettage", "aide": "Assombrit les bords pour attirer l'œil au centre."},
    "nettete": {"nom": "Netteté", "aide": "Renforce les détails (utile sur une vidéo IA en 480p)."},
}

MASQUES = {"rect-flou": "Flou local (rectangle)", "ellipse-flou": "Flou local (ellipse)",
           "rect-pixels": "Pixeliser une zone", "recadrage": "Recadrer (zoom sur une zone)"}

PRESETS = {
    "reels": {"nom": "Reels / Stories 9:16", "largeur": 1080, "hauteur": 1920, "ips": 30, "debit": "10M"},
    "telephone": {"nom": "Version téléphone (< 30 Mo)", "largeur": 1080, "hauteur": 1920, "ips": 30, "max_mo": 29},
    "carre": {"nom": "Carré 1:1", "largeur": 1080, "hauteur": 1080, "ips": 30, "debit": "8M"},
    "portrait": {"nom": "Portrait 4:5", "largeur": 1080, "hauteur": 1350, "ips": 30, "debit": "9M"},
    "vitesse108": {"nom": "9:16 en vitesse 1,08x", "largeur": 1080, "hauteur": 1920, "ips": 30, "debit": "10M", "vitesse": 1.08},
    "vitesse112": {"nom": "9:16 en vitesse 1,12x", "largeur": 1080, "hauteur": 1920, "ips": 30, "debit": "10M", "vitesse": 1.12},
    "extrait": {"nom": "Extrait de 5 s", "largeur": 1080, "hauteur": 1920, "ips": 30, "debit": "10M", "extrait": 5},
    "apercu": {"nom": "Aperçu rapide (540p)", "largeur": 540, "hauteur": 960, "ips": 30, "crf": 28, "rapide": True},
}


# --------------------------------------------------------------------------- disposition

def duree_plan(p: dict) -> float:
    if p.get("type") == "image":
        return max(0.1, float(p.get("duree") or 2.0))
    return max(0.05, (float(p["fin"]) - float(p["debut"])) / max(0.1, float(p.get("vitesse") or 1)))


def transition_apres(projet: dict, cle: str):
    for t in projet.get("transitions", []):
        if t.get("apres") == cle and t.get("type") and t["type"] != "coupe":
            return t
    return None


def duree_transition(t, d1, d2):
    if not t:
        return 0.0
    d = float(t.get("duree") or TRANSITIONS.get(t["type"], {}).get("duree") or 0.4)
    return max(0.05, min(d, d1 * 0.9, d2 * 0.9))


def disposition(projet: dict) -> dict:
    """Début de chaque plan sur la timeline (les transitions font se chevaucher les plans)."""
    debuts, t = [], 0.0
    plans = projet.get("plans", [])
    for i, p in enumerate(plans):
        d = duree_plan(p)
        if i > 0:
            tr = transition_apres(projet, plans[i - 1]["id"])
            t -= duree_transition(tr, duree_plan(plans[i - 1]), d)
        debuts.append(round(t, 3))
        t += d
    return {"debuts": debuts, "total": round(t, 3)}


# --------------------------------------------------------------------------- filtres d'un plan

def _cadre(fmt, ajuster):
    l, h = fmt["largeur"], fmt["hauteur"]
    if ajuster == "contenir":
        return (f"scale={l}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,"
                f"pad={l}:{h}:(ow-iw)/2:(oh-ih)/2:color=black")
    return f"scale={l}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={l}:{h}"


def _atempo(v):
    morceaux = []
    while v > 2.0:
        morceaux.append("atempo=2.0")
        v /= 2.0
    while v < 0.5:
        morceaux.append("atempo=0.5")
        v /= 0.5
    morceaux.append(f"atempo={v:.4f}")
    return ",".join(morceaux)


def filtre_effet(e: dict, fmt: dict, duree: float) -> str:
    k = max(0.0, min(1.0, float(e.get("force", 0.5))))
    t = e.get("type")
    if t == "flou":
        return f"gblur=sigma={1 + 24 * k:.1f}"
    if t == "glow":
        return f"split[ga][gb];[gb]gblur=sigma=14[gg];[ga][gg]blend=all_mode=screen:all_opacity={0.15 + 0.5 * k:.2f}"
    if t == "grain":
        return f"noise=alls={int(6 + 26 * k)}:allf=t"
    if t == "aberration":
        d = int(2 + 8 * k)
        return f"rgbashift=rh=-{d}:bh={d}"
    if t == "vignette":
        return f"vignette=angle={0.3 + 0.6 * k:.2f}"
    if t == "nettete":
        return f"unsharp=5:5:{0.4 + 1.2 * k:.2f}:5:5:0.0"
    if t == "leak":
        l, h = fmt["largeur"], fmt["hauteur"]
        return (f"split[la][lb];[lb]drawbox=x=0:y=0:w=iw:h=ih:color=black@1:t=fill,"
                f"geq=r='255*{k:.2f}*exp(-((X-W*0.95)^2+(Y-H*(0.2+0.1*sin(T)))^2)/(2*(W*0.35)^2))':"
                f"g='150*{k:.2f}*exp(-((X-W*0.95)^2+(Y-H*(0.2+0.1*sin(T)))^2)/(2*(W*0.35)^2))':"
                f"b='40*{k:.2f}*exp(-((X-W*0.95)^2+(Y-H*(0.2+0.1*sin(T)))^2)/(2*(W*0.35)^2))'[lc];"
                f"[la][lc]blend=all_mode=screen")
    return "null"


def filtre_masque(m: dict, fmt: dict) -> str:
    l, h = fmt["largeur"], fmt["hauteur"]
    x, y = float(m.get("x", 0.25)), float(m.get("y", 0.25))
    w, hh = float(m.get("l", 0.5)), float(m.get("h", 0.5))
    t = m.get("type", "rect-flou")
    if t == "recadrage":
        return (f"crop=iw*{w:.3f}:ih*{hh:.3f}:iw*{x:.3f}:ih*{y:.3f},"
                f"scale={l}:{h}:force_original_aspect_ratio=increase,crop={l}:{h}")
    effet = "gblur=sigma=28" if t.endswith("flou") else f"scale=iw/24:ih/24,scale={l}:{h}:flags=neighbor"
    if t.startswith("ellipse"):
        cx, cy, rx, ry = x + w / 2, y + hh / 2, w / 2, hh / 2
        alpha = f"255*lte(pow((X/W-{cx:.3f})/{rx:.3f},2)+pow((Y/H-{cy:.3f})/{ry:.3f},2),1)"
    else:
        alpha = f"255*between(X/W,{x:.3f},{x + w:.3f})*between(Y/H,{y:.3f},{y + hh:.3f})"
    return (f"split[ma][mb];[mb]{effet},format=yuva420p,geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='{alpha}'[mc];"
            f"[ma][mc]overlay=0:0")


def preparer_plan(p: dict, fmt: dict, journal) -> Path:
    """Un plan → un clip mp4 normalisé (format, i/s, look, effets, son 48 kHz stéréo), mis en cache."""
    source = chemin_media(p["source"])
    d = duree_plan(p)
    look = p.get("look") or {}
    stats = None
    if look.get("id") == "auto":
        stats = luts.stats_image(source, float(p.get("debut") or 0) + 0.2) if source.suffix.lower() not in EXT_IMAGE else luts.stats_image(source)
    cle = empreinte(p, fmt, source.stat().st_mtime, stats, 3)
    sortie = CACHE / "plans" / f"{cle}.mp4"
    with _VERROUS_LOCK:
        verrou = _VERROUS_PLANS.setdefault(cle, threading.Lock())
    with verrou:   # deux rendus simultanés ne préparent jamais le même plan en même temps
        if sortie.exists() and sortie.stat().st_size > 0:
            return sortie
        return _preparer_plan(p, fmt, journal, source, d, look, stats, sortie)


_VERROUS_PLANS = {}
_VERROUS_LOCK = threading.Lock()


def _preparer_plan(p, fmt, journal, source, d, look, stats, sortie):
    sortie.parent.mkdir(parents=True, exist_ok=True)
    ips = fmt.get("ips", 30)
    v = float(p.get("vitesse") or 1)
    chaine = []
    if source.suffix.lower() in EXT_IMAGE:
        entree = ["-loop", "1", "-framerate", ips, "-t", f"{d:.3f}", "-i", source]
        chaine.append("setpts=PTS-STARTPTS")
    else:
        entree = ["-ss", f"{float(p['debut']):.3f}", "-t", f"{float(p['fin']) - float(p['debut']):.3f}", "-i", source]
        chaine.append(f"setpts=(PTS-STARTPTS)/{v:.4f}")
    chaine += [f"fps={ips}", _cadre(fmt, p.get("ajuster", "remplir")), "setsar=1", "format=rgb24"]
    if look.get("id") in luts.LOOKS:
        force = round(float(look.get("force", 1.0)) * 20) / 20
        if force > 0:
            cube = luts.fichier_cube(look["id"], force, True, stats)
            chaine.append(f"lut3d=file='{cube}'")
    graphe = ",".join(chaine)
    for e in p.get("effets") or []:
        graphe += "," + filtre_effet(e, fmt, d)
    if p.get("masque"):
        graphe += "," + filtre_masque(p["masque"], fmt)
    graphe = f"[0:v]{graphe},format=yuv420p,trim=duration={d:.3f}[v]"

    info = probe_cache(source)
    a_audio = "audio_hz" in info and source.suffix.lower() not in EXT_IMAGE
    if a_audio:
        af = [f"asetpts=PTS-STARTPTS", _atempo(v) if abs(v - 1) > 1e-3 else "anull",
              f"volume={float(p.get('volume', 1.0)):.3f}"]
        if p.get("voix_claire"):
            af += ["highpass=f=80", "afftdn=nf=-25", "acompressor=threshold=-20dB:ratio=3:attack=5:release=120",
                   "equalizer=f=3000:t=q:w=1:g=3"]
        af += ["aresample=48000", "aformat=sample_fmts=fltp:channel_layouts=stereo", "apad", f"atrim=duration={d:.3f}"]
        graphe += f";[0:a]{','.join(af)}[a]"
        entrees_audio = []
    else:
        graphe += f";[1:a]atrim=duration={d:.3f}[a]"
        entrees_audio = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    args = [*entree, *entrees_audio, "-filter_complex", graphe, "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "17" if fmt["largeur"] >= 1000 else "23",
            "-c:a", "pcm_s16le", "-t", f"{d:.3f}", sortie.with_suffix(".mov")]
    journal(f"Plan {p['id']} : préparation ({d:.2f} s)")
    temp = sortie.with_name(sortie.stem + f".{threading.get_ident()}.mov")
    args[-1] = temp
    executer(args, journal)
    temp.rename(sortie)
    return sortie


# --------------------------------------------------------------------------- exécution suivie

class Travail:
    def __init__(self, nature, projet_id, preset):
        self.id = nouvel_id("rendu-")
        self.nature, self.projet_id, self.preset = nature, projet_id, preset
        self.etat, self.progression, self.message = "en file", 0.0, ""
        self.sortie, self.verif, self.pid, self.debut = None, None, None, maintenant()
        self.log = CACHE / "rendus" / f"{self.id}.log"
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.en_pause = False

    def ecrire(self, texte):
        with self.log.open("a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {texte}\n")
        self.message = texte

    def dict(self):
        return {"id": self.id, "nature": self.nature, "projet": self.projet_id, "preset": self.preset,
                "etat": "en pause" if self.en_pause else self.etat, "progression": round(self.progression, 1),
                "message": self.message, "sortie": relatif(self.sortie) if self.sortie else None,
                "verif": self.verif, "debut": self.debut}


TRAVAUX = {}
LOURDS = threading.Semaphore(2)
_courant = threading.local()


def executer(args, journal, duree_attendue=None, travail=None, part=(0, 100)):
    """Lance ffmpeg avec suivi de progression. Ne tue jamais le processus."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-progress", "pipe:1", "-nostats", *map(str, args)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if travail:
        travail.pid = p.pid
    for ligne in p.stdout:
        if travail and duree_attendue and ligne.startswith("out_time_us="):
            try:
                t = int(ligne.split("=")[1]) / 1e6
                travail.progression = part[0] + (part[1] - part[0]) * min(1, t / duree_attendue)
            except ValueError:
                pass
    err = p.stderr.read()
    p.wait()
    if p.returncode != 0:
        journal("ERREUR ffmpeg : " + err[-1500:])
        utiles = [l for l in err.splitlines() if l.strip() and "Terminating" not in l and "Task finished" not in l]
        raise RuntimeError((utiles[0] if utiles else "ffmpeg a échoué")[:400])
    return p.returncode


def mettre_en_pause(tid, pause=True):
    t = TRAVAUX.get(tid)
    if not t or not t.pid or t.etat != "en cours":
        return False
    try:
        os.kill(t.pid, signal.SIGSTOP if pause else signal.SIGCONT)
        t.en_pause = pause
        return True
    except ProcessLookupError:
        return False


# --------------------------------------------------------------------------- assemblage

def assembler(projet: dict, preset_id: str, travail: Travail) -> Path:
    preset = PRESETS[preset_id]
    fmt = {"largeur": preset["largeur"], "hauteur": preset["hauteur"], "ips": preset["ips"]}
    if preset_id in ("reels", "telephone", "vitesse108", "vitesse112", "extrait", "apercu"):
        base = projet.get("format", {})
        if base.get("largeur") and base.get("hauteur") and base["largeur"] / base["hauteur"] != 9 / 16:
            ratio = base["largeur"] / base["hauteur"]
            fmt["hauteur"] = int(round(fmt["largeur"] / ratio / 2) * 2)
    plans = projet.get("plans", [])
    if not plans:
        raise RuntimeError("Le projet n'a aucun plan.")
    clips = []
    for i, p in enumerate(plans):
        travail.progression = 40 * i / len(plans)
        clips.append(preparer_plan(p, fmt, travail.ecrire))
    lay = disposition(projet)
    total = lay["total"]
    travail.ecrire(f"Assemblage : {len(clips)} plans, {total:.2f} s")

    entrees, graphe = [], []
    for k, c in enumerate(clips):
        entrees += ["-i", c]
        graphe.append(f"[{k}:v]settb=AVTB,setpts=PTS-STARTPTS[c{k}v]")
        graphe.append(f"[{k}:a]asetpts=PTS-STARTPTS[c{k}a]")
    cv, ca, long = "[c0v]", "[c0a]", duree_plan(plans[0])
    for i in range(1, len(plans)):
        d2 = duree_plan(plans[i])
        tr = transition_apres(projet, plans[i - 1]["id"])
        if not tr:
            graphe.append(f"{cv}{ca}[c{i}v][c{i}a]concat=n=2:v=1:a=1[k{i}][a{i}]")
            graphe.append(f"[k{i}]settb=AVTB[v{i}]")
            long += d2
        else:
            dt = duree_transition(tr, duree_plan(plans[i - 1]), d2)
            xf = TRANSITIONS.get(tr["type"], TRANSITIONS["fondu"])["xfade"] or "fade"
            graphe.append(f"{cv}[c{i}v]xfade=transition={xf}:duration={dt:.3f}:offset={long - dt:.3f}[v{i}]")
            graphe.append(f"{ca}[c{i}a]acrossfade=d={dt:.3f}:c1=tri:c2=tri[a{i}]")
            long += d2 - dt
        cv, ca = f"[v{i}]", f"[a{i}]"
    # fondus d'ouverture / de sortie
    fin_v = []
    t_debut = transition_apres(projet, "debut")
    t_fin = transition_apres(projet, "fin")
    if t_debut:
        dd = min(float(t_debut.get("duree") or 0.5), total / 2)
        coul = ":color=white" if t_debut["type"] == "blanc" else ""
        fin_v.append(f"fade=t=in:st=0:d={dd:.3f}{coul}")
    if t_fin:
        df = min(float(t_fin.get("duree") or 0.5), total / 2)
        coul = ":color=white" if t_fin["type"] == "blanc" else ""
        fin_v.append(f"fade=t=out:st={total - df:.3f}:d={df:.3f}{coul}")
    graphe.append(f"{cv}{','.join(fin_v) or 'null'},format=yuv420p[vb]")
    cv = "[vb]"
    n = len(clips)

    # textes et graphismes
    for j, tx in enumerate(projet.get("textes", [])):
        a, b = max(0.0, float(tx.get("debut", 0))), min(total, float(tx.get("fin", total)))
        if b <= a:
            continue
        if tx.get("image"):
            png = chemin_media(tx["image"])
            entrees += ["-loop", "1", "-t", f"{total:.3f}", "-i", png]
            pre = f"[{n}:v]scale={fmt['largeur']}:{fmt['hauteur']}:force_original_aspect_ratio=decrease,format=rgba"
        else:
            png = textes.rendre(tx, fmt["largeur"], fmt["hauteur"])
            entrees += ["-loop", "1", "-t", f"{total:.3f}", "-i", png]
            pre = f"[{n}:v]format=rgba"
        anim = tx.get("animation", "fondu")
        if anim in ("fondu", "glisse", "pop"):
            pre += f",fade=t=in:st={a:.3f}:d=0.25:alpha=1,fade=t=out:st={max(a, b - 0.2):.3f}:d=0.2:alpha=1"
        y = "0"
        if anim == "glisse":
            y = f"if(lt(t-{a:.3f},0.3),(1-(t-{a:.3f})/0.3)*{int(fmt['hauteur'] * 0.04)},0)"
        elif anim == "pop":
            y = f"if(lt(t-{a:.3f},0.18),-(1-(t-{a:.3f})/0.18)*{int(fmt['hauteur'] * 0.015)},0)"
        x = "(W-w)/2" if tx.get("image") else "0"
        graphe.append(f"{pre}[t{j}]")
        graphe.append(f"{cv}[t{j}]overlay=x='{x}':y='{y}':enable='between(t,{a:.3f},{b:.3f})':eval=frame[vt{j}]")
        cv = f"[vt{j}]"
        n += 1

    # sons : voix, bruitages, musique (baissée automatiquement sous le son principal)
    musiques, autres = [], []
    for s in projet.get("sons", []):
        src = chemin_media(s["source"])
        entrees += ["-ss", f"{float(s.get('coupe_debut', 0)):.3f}", "-i", src]
        retard = int(max(0.0, float(s.get("debut", 0))) * 1000)
        dur = s.get("duree")
        chaine = f"[{n}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
        if dur:
            chaine += f",atrim=duration={float(dur):.3f}"
        chaine += f",volume={float(s.get('volume', 1.0)):.3f},adelay={retard}|{retard},apad,atrim=duration={total:.3f}"
        graphe.append(f"{chaine}[s{n}]")
        (musiques if s.get("type") == "musique" else autres).append(f"[s{n}]")
        n += 1
    voix = [ca] + autres
    if len(voix) > 1:
        graphe.append(f"{''.join(voix)}amix=inputs={len(voix)}:normalize=0:duration=first[voix]")
    else:
        graphe.append(f"{ca}anull[voix]")
    if musiques:
        graphe.append(f"{''.join(musiques)}amix=inputs={len(musiques)}:normalize=0:duration=first[mus]")
        graphe.append("[voix]asplit=2[voix1][cle]")
        graphe.append("[mus][cle]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[musb]")
        graphe.append("[voix1][musb]amix=inputs=2:normalize=0:duration=first[mix]")
    else:
        graphe.append("[voix]anull[mix]")
    vitesse = preset.get("vitesse")
    if vitesse:
        graphe.append(f"{cv}setpts=PTS/{vitesse}[vv]")
        cv = "[vv]"
        graphe.append(f"[mix]{_atempo(vitesse)}[mixv]")
        mix = "[mixv]"
        total_sortie = total / vitesse
    else:
        mix, total_sortie = "[mix]", total
    graphe.append(f"{mix}aresample=48000[aout]")

    debut_extrait = float(projet.get("_extrait_debut", 0)) if preset.get("extrait") else 0
    duree_sortie = min(preset["extrait"], max(0.5, total_sortie - debut_extrait)) if preset.get("extrait") else total_sortie
    dossier = EXPORTS / projet.get("id", "projet")
    sortie = nom_libre(dossier, f"{projet.get('id', 'projet')}_{projet.get('version', 'v001')}_{preset_id}", ".mp4")
    video = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(fmt["ips"]), "-movflags", "+faststart",
             "-profile:v", "high"]
    if preset.get("rapide"):
        video += ["-preset", "ultrafast", "-crf", str(preset.get("crf", 28))]
    elif preset.get("max_mo"):
        kbps = int(preset["max_mo"] * 8 * 1024 * 0.93 / max(duree_sortie, 1)) - 160
        kbps = max(800, min(kbps, 9000))
        video += ["-preset", "medium", "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.2)}k", "-bufsize", f"{kbps * 2}k"]
    else:
        video += ["-preset", "medium", "-b:v", preset["debit"], "-maxrate", preset["debit"], "-bufsize", "20M"]
    coupe = []
    if preset.get("extrait"):
        coupe = ["-ss", f"{debut_extrait:.3f}", "-t", f"{duree_sortie:.3f}"]
    args = [*entrees, "-filter_complex", ";".join(graphe), "-map", cv, "-map", "[aout]", *video,
            "-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2",
            *(coupe or ["-t", f"{duree_sortie:.3f}"]), sortie]
    (CACHE / "rendus" / f"{travail.id}.graphe.txt").write_text(";\n".join(graphe))
    travail.ecrire("Rendu final en cours…")
    temp = CACHE / "rendus" / f"{travail.id}.mov"
    args[-1] = temp
    executer(args, travail.ecrire, duree_attendue=duree_sortie + debut_extrait, travail=travail, part=(40, 92))
    # Son : mesure de la sonie réelle puis gain exact vers −14 LUFS, avec limiteur (crêtes ≤ −1,5 dB)
    lufs = mesurer_lufs(temp)
    gain = max(-30.0, min(30.0, -14.0 - lufs)) if lufs is not None and lufs > -70 else 0.0
    travail.ecrire(f"Son mesuré à {lufs} LUFS → gain {gain:+.1f} dB vers −14 LUFS")
    try:
        executer(["-i", temp, "-map", "0:v", "-map", "0:a", "-c:v", "copy",
                  "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:level=false:attack=3:release=60",
                  "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", sortie],
                 travail.ecrire, duree_attendue=duree_sortie, travail=travail, part=(92, 98))
    finally:
        temp.unlink(missing_ok=True)
    return sortie


def mesurer_lufs(fichier: Path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(fichier), "-map", "0:a", "-af",
                        "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else None


def verifier(sortie: Path, preset_id: str) -> dict:
    """Contrôle ffprobe + mesure de sonie (ebur128)."""
    info = ffprobe(sortie)
    preset = PRESETS[preset_id]
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(sortie), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    lufs = float(m[-1]) if m else None
    controles = {
        "dimensions": f"{info.get('largeur')}×{info.get('hauteur')}",
        "ips": info.get("ips"), "audio_hz": info.get("audio_hz"), "codec": info.get("codec_video"),
        "duree": round(info.get("duree", 0), 2), "taille_mo": round(info.get("taille", 0) / 1048576, 2),
        "lufs": lufs,
    }
    ok = [info.get("audio_hz") == 48000, abs((info.get("ips") or 0) - preset["ips"]) < 0.01,
          info.get("codec_video") == "h264"]
    if not preset.get("rapide"):
        ok.append(info.get("largeur") == preset["largeur"])
        ok.append(lufs is not None and abs(lufs + 14) <= 1.0)
    if preset.get("max_mo"):
        ok.append(info.get("taille", 0) < 30 * 1048576)
    controles["ok"] = all(ok)
    return controles


def lancer(projet: dict, preset_id: str, extrait_debut: float = 0.0) -> Travail:
    if preset_id not in PRESETS:
        raise ValueError("Réglage d'export inconnu.")
    projet = json.loads(json.dumps(projet))
    projet["_extrait_debut"] = extrait_debut
    t = Travail("rendu", projet.get("id"), preset_id)
    TRAVAUX[t.id] = t

    def tourner():
        t.ecrire("En attente d'une place (2 rendus lourds maximum en même temps)")
        with LOURDS:
            t.etat = "en cours"
            try:
                t.sortie = assembler(projet, preset_id, t)
                t.ecrire("Vérification ffprobe et sonie…")
                t.verif = verifier(t.sortie, preset_id)
                t.etat, t.progression = "fini", 100
                t.ecrire("Terminé : " + relatif(t.sortie))
            except Exception as e:   # noqa: BLE001 — on remonte l'erreur à l'écran
                if t.sortie is None:
                    for f in (EXPORTS / str(projet.get("id"))).glob("*.mp4"):
                        if f.stat().st_size == 0:
                            f.unlink()
                t.etat = "échec"
                t.ecrire(f"Échec : {e}")

    threading.Thread(target=tourner, daemon=True).start()
    return t


def lancer_script(projet: dict) -> Travail:
    """Si le projet déclare un script de rendu complet (champ script_rendu), on le lance tel quel."""
    script = projet.get("script_rendu")
    t = Travail("script", projet.get("id"), "script")
    TRAVAUX[t.id] = t
    chemin = (PROJET_ADS / script).resolve() if script else None
    if not chemin or not chemin.exists() or PROJET_ADS not in chemin.parents:
        t.etat = "échec"
        t.ecrire("Aucun script de rendu déclaré pour ce projet.")
        return t

    def tourner():
        with LOURDS:
            t.etat = "en cours"
            p = subprocess.Popen(["bash", str(chemin)], cwd=chemin.parent, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True)
            t.pid = p.pid
            for ligne in p.stdout:
                t.ecrire(ligne.rstrip()[:300])
            p.wait()
            t.etat = "fini" if p.returncode == 0 else "échec"
            t.progression = 100

    threading.Thread(target=tourner, daemon=True).start()
    return t


# --------------------------------------------------------------------------- aperçus de la bibliothèque

def apercu_transition(type_: str, a: Path, b: Path) -> Path:
    """Petite boucle animée (mp4 muet) montrant la transition entre deux images du projet."""
    xf = TRANSITIONS.get(type_, TRANSITIONS["fondu"])["xfade"]
    sortie = CACHE / "apercus_transitions" / f"{empreinte(type_, str(a), str(b), 2)}.mp4"
    if sortie.exists():
        return sortie
    sortie.parent.mkdir(parents=True, exist_ok=True)
    base = "scale=180:320:force_original_aspect_ratio=increase,crop=180:320,fps=25,format=yuv420p,setsar=1"
    if xf:
        f = f"[0]{base}[a];[1]{base}[b];[a][b]xfade=transition={xf}:duration=0.6:offset=0.7[v]"
    else:
        f = f"[0]{base}[a];[1]{base}[b];[a][b]concat=n=2:v=1[v]"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-t", "1.3", "-i", str(a),
                    "-loop", "1", "-t", "1.3", "-i", str(b), "-filter_complex", f, "-map", "[v]", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "30", "-an", str(sortie)], capture_output=True)
    return sortie


def apercu_effet(effet: dict, image: Path) -> Path:
    fmt = {"largeur": 270, "hauteur": 480, "ips": 25}
    sortie = CACHE / "apercus_effets" / f"{empreinte(effet, str(image), 2)}.jpg"
    if sortie.exists():
        return sortie
    sortie.parent.mkdir(parents=True, exist_ok=True)
    if effet.get("type") in MASQUES:
        f = filtre_masque(effet, fmt)
    else:
        f = filtre_effet(effet, fmt, 1)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-t", "1", "-i", str(image),
                    "-filter_complex", f"[0]{_cadre(fmt, 'remplir')},format=yuv420p,{f}",
                    "-frames:v", "1", str(sortie)], capture_output=True)
    return sortie
