"""
CONTRÔLEUR VIDÉO — fail-closed sur la mise en page.

Pourquoi il existe
------------------
Constat (source réelle, anonymisée) : « pourquoi il met du texte sur le produit, ça ça doit être
red flag, jamais surtout qu'on a de la place au-dessus ; y a beaucoup de vide dans les vidéos, à
chaque fois il fait ça, j'ai l'impression il sait pas utiliser l'espace. »

Constaté sur un livrable d'exemple : le cartouche de texte était posé SUR le <PRODUIT> sur la
quasi-totalité du film, pendant que le tiers supérieur du cadre était un aplat de fond vide. Ce
n'est pas une erreur de goût, c'est une faute mesurable — et une faute mesurable se refuse par un
contrôleur, pas par un rappel dans une fiche qu'on relira mal.

Même doctrine que pour les statics : « un contrôleur numérique attrape ce que l'œil rate ; jamais
l'inverse. »

Ce qu'il vérifie, image par image
---------------------------------
1. TEXTE SUR PRODUIT     — un cartouche ne doit jamais recouvrir le produit.
2. ESPACE GASPILLÉ       — si le cartouche est en bas et que le haut du cadre
                           est vide, la place était au-dessus.
3. ZONES DE SÉCURITÉ META— rien d'écrit dans les bandes que Meta recouvre.

Il sort en code 1 dès qu'une règle tombe, et il écrit des images annotées pour
qu'on VOIE la faute au lieu de la lire.

    python controle_video.py "<chemin.mp4>"
    python controle_video.py "<dossier>"    # tout le batch

Réglages
--------
Les seuils de luminance (couleurs de fond/produit/cartouche) et les zones de sécurité sont calibrés
pour UN produit et UN habillage donnés — ils se lisent dans `../config/ziad.example.json`
(clé `controle_video`) et retombent sur des valeurs par défaut sûres si le fichier est absent.
**Recalibre-les sur tes propres visuels avant de faire confiance au verdict** : mesure la luminance
réelle de ton fond, de ton produit et de ton cartouche (un simple pipette sur une image suffit).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "ziad.example.json"


def _charger_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


_C = _charger_config().get("controle_video", {})

# --- Seuils, à recalibrer sur ton propre produit/habillage (voir docstring + config) --------------
L_PRODUIT = _C.get("l_produit", 95)         # en dessous : matière sombre = produit sombre (exemple)
# Certains produits changent de couleur en cours de vie de la boîte : si un seul seuil sombre laisse
# passer un cartouche posé EN PLEIN sur un produit clair (parce que le produit clair est plus lumineux
# que le seuil), on ajoute un second seuil plus haut. Tout ce qui est plus sombre que le fond clair de
# la planche et qui n'est pas un cartouche compte alors comme « occupé » : le texte ne s'y pose pas.
# C'est plus strict (un décor sombre compte aussi) — c'est voulu, un contrôleur se trompe dans le sens
# du refus.
L_PRODUIT_CLAIR = _C.get("l_produit_clair", 200)
PRODUIT_MIN = _C.get("produit_min", 0.005)   # part du cadre : en dessous, indécidable
PRODUIT_MAX = _C.get("produit_max", 0.92)    # part du cadre : au-dessus, indécidable
# Le fond clair de la planche a une luminance mesurée qu'il faut connaître précisément (formule :
# 0.299*R + 0.587*G + 0.114*B). Avec un seuil trop bas, tout aplat de fond clair — c'est-à-dire
# exactement le « vide en haut » que la règle demande de laisser libre pour le texte — se ferait
# détecter comme un faux cartouche géant partant de y=0, et donc refusé pour débordement de zone
# sûre. Un vrai cartouche est en blanc pur. Choisis un seuil qui sépare proprement ton fond clair
# (jamais un cartouche) de ton blanc de cartouche (toujours un cartouche), sans laisser passer un
# cartouche gris clair pour autant.
L_CARTE = _C.get("l_carte", 250)             # au-dessus : cartouche — PAS le fond clair de la planche
MIN_CARTE_PX = _C.get("min_carte_px", 1500)  # une tache blanche plus petite n'est pas un cartouche
# Un reflet vif dans le DÉCOR (jour par une porte, un highlight de lumière) peut lui aussi dépasser
# L_CARTE de luminance et couvrir plus de MIN_CARTE_PX si la tache est haute et étroite. Un vrai
# cartouche de mise en page couvre presque toute la largeur sûre du cadre — jamais un reflet ponctuel.
# La largeur minimale ci-dessous doit rester confortablement sous la largeur d'un vrai cartouche et
# au-dessus de ce type d'artefact.
MIN_CARTE_W = _C.get("min_carte_w", 200)

# Zones que Meta recouvre de son interface, en 1080x1920 (exemple de départ, à vérifier sur les
# specs Meta à jour pour ton format — Reels/Stories publient parfois des marges plus larges que la
# marge basse ci-dessous).
META_HAUT = _C.get("meta_haut", 250)
META_BAS = _C.get("meta_bas", 440)
META_COTE = _C.get("meta_cote", 80)
META_BAS_REELS = _C.get("meta_bas_reels", 672)

# Tolérances. Elles sont volontairement serrées : le but n'est pas de laisser
# passer « un peu » de texte sur le produit, c'est de n'en laisser passer aucun.
TOLERANCE_RECOUVREMENT = _C.get("tolerance_recouvrement", 0.015)  # % de la SURFACE du cartouche sur le produit
FRANGE_MAX = _C.get("frange_max", 0.02)          # part de la boîte touchée par la marge de respiration
MARGE_MIN_PX = _C.get("marge_min_px", 12)        # le cartouche doit respirer autour du produit
# Le pendant statique refuse au-delà d'un certain % de vide ; aligne ce seuil vidéo avec ton
# contrôleur de statics si tu en as un.
VIDE_HAUT_MAX = _C.get("vide_haut_max", 0.55)
VIDE_HAUT_ALERTE = _C.get("vide_haut_alerte", 0.30)
# La bande « au-dessus du cartouche » ne s'évalue que si elle est assez haute pour accueillir un
# cartouche — sinon un cartouche posé juste sous la zone Meta se ferait refuser pour « espace perdu »
# sur une bande trop fine pour contenir quoi que ce soit d'utile.
VIDE_BANDE_MIN = _C.get("vide_bande_min", 0.12)  # part de la hauteur du cadre
FPS = _C.get("fps", 4)                            # un fps trop bas laisse passer un cartouche bref


def frames(video: Path, fps: int = FPS) -> list[Path]:
    """Extrait les images en pleine résolution. Sans elles, on ne mesure rien."""
    d = Path(tempfile.mkdtemp(prefix="ctrl-video-"))
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
         "-vf", f"fps={fps}", str(d / "f%03d.png"), "-y"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg a echoue sur {video.name} :\n{r.stderr.strip()}")
    return sorted(d.glob("*.png"))


def boites(masque: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Boîtes englobantes des zones blanches, par projection.

    Pas de scipy : on regroupe les lignes contiguës qui contiennent du blanc,
    puis les colonnes contiguës dans chaque bande. Sur des cartouches
    rectangulaires posés à plat, c'est exact — et ça n'ajoute aucune dépendance.
    """
    out = []
    lignes = masque.any(axis=1)
    y = 0
    H = len(lignes)
    while y < H:
        if not lignes[y]:
            y += 1
            continue
        y0 = y
        while y < H and lignes[y]:
            y += 1
        bande = masque[y0:y]
        cols = bande.any(axis=0)
        x = 0
        W = len(cols)
        while x < W:
            if not cols[x]:
                x += 1
                continue
            x0 = x
            while x < W and cols[x]:
                x += 1
            if bande[:, x0:x].sum() >= MIN_CARTE_PX and (x - x0) >= MIN_CARTE_W:
                out.append((x0, y0, x, y))
    return out


def dilate(masque: np.ndarray, r: int) -> np.ndarray:
    """Épaissit un masque de r pixels, par décalages successifs. La marge de
    respiration se mesure ainsi sans dépendance supplémentaire."""
    m = masque.copy()
    for _ in range(r):
        m[1:, :] |= masque[:-1, :]
        m[:-1, :] |= masque[1:, :]
        m[:, 1:] |= masque[:, :-1]
        m[:, :-1] |= masque[:, 1:]
        masque = m.copy()
    return m


def controler_image(p: Path, sortie: Path | None) -> dict:
    """Renvoie {"fautes": [...], "avertissements": [...], "cartes": n}."""
    im = Image.open(p).convert("RGB")
    W, H = im.size
    L = np.asarray(im.convert("L")).astype(np.int16)

    cartes = boites(L > L_CARTE)
    carte_masque = np.zeros_like(L, dtype=bool)
    for (x0, y0, x1, y1) in cartes:
        carte_masque[y0:y1, x0:x1] = True
    # Occupé = produit sombre OU toute matière plus sombre que le fond clair, hors cartouches.
    produit = ((L < L_PRODUIT) | (L < L_PRODUIT_CLAIR)) & ~carte_masque
    fautes: list[str] = []
    avertissements: list[str] = []

    # Si on ne sait pas séparer produit et fond, on ne dit pas « conforme ».
    part = float(produit.mean())
    if cartes and not (PRODUIT_MIN <= part <= PRODUIT_MAX):
        fautes.append(
            f"INDECIDABLE — {part*100:.0f} % du cadre est lu comme « occupé » (seuils L<{L_PRODUIT_CLAIR}) : "
            f"impossible de dire si le cartouche est sur le produit, refus par défaut"
        )

    # Échelle des zones Meta si la vidéo n'est pas en 1080x1920 (les côtés suivent la largeur).
    k = H / 1920
    haut, bas, cote = META_HAUT * k, META_BAS * k, META_COTE * (W / 1080)
    bas_reels = META_BAS_REELS * k

    # Un cartouche est un aplat OPAQUE (fond plein + son propre texte) : rien du produit ne peut
    # apparaître dans son propre rectangle sur l'image finale, seulement son fond clair et SON PROPRE
    # TEXTE. Or le texte est écrit en encre sombre, donc < L_PRODUIT — sans cette exclusion, chaque
    # cartouche se ferait détecter comme posé sur le produit à cause de ses propres lettres. On
    # retire donc l'intérieur de chaque cartouche du masque produit AVANT dilatation ; le texte posé
    # sur le VRAI produit reste détecté, lui, puisque ce recouvrement vient de pixels situés HORS de
    # tout cartouche qui débordent dans sa boîte.
    # Le calcul mesure deux choses distinctes : le VRAI recouvrement (matière occupée SOUS la boîte,
    # lue avec une marge de 1 px autour, puisque l'intérieur d'un cartouche opaque ne montre que son
    # fond et son encre) et la FRANGE de respiration.
    produit_gros = dilate(produit, MARGE_MIN_PX) if produit.any() else produit

    annot = ImageDraw.Draw(im) if sortie else None

    for (x0, y0, x1, y1) in cartes:
        aire = max(1, (x1 - x0) * (y1 - y0))
        # Recouvrement réel : ce que la boîte cache se lit sur son pourtour immédiat (2 px
        # autour) — un cartouche opaque posé sur le produit est bordé de produit sur tout
        # son périmètre, un cartouche dans le vide est bordé de fond.
        y0e, y1e, x0e, x1e = max(0, y0 - 2), min(H, y1 + 2), max(0, x0 - 2), min(W, x1 + 2)
        pourtour = produit[y0e:y1e, x0e:x1e].copy()
        pourtour[(y0 - y0e):(y0 - y0e) + (y1 - y0), (x0 - x0e):(x0 - x0e) + (x1 - x0)] = False
        perimetre = max(1, pourtour.size - aire)
        recouvre = pourtour.sum() / perimetre
        frange = produit_gros[y0:y1, x0:x1].sum() / aire
        ok = True

        # 1. le texte ne se pose jamais sur le produit
        if recouvre > 0.25:
            fautes.append(
                f"TEXTE SUR PRODUIT — cartouche ({x0},{y0})-({x1},{y1}) : "
                f"{recouvre*100:.0f} % de son pourtour est sur de la matière occupée"
            )
            ok = False
        elif frange > FRANGE_MAX:
            fautes.append(
                f"MARGE INSUFFISANTE — moins de {MARGE_MIN_PX} px entre le cartouche "
                f"({x0},{y0})-({x1},{y1}) et le produit ({frange*100:.1f} % de la boîte touchée)"
            )
            ok = False

        # 2. zones de securite Meta
        if y0 < haut or y1 > H - bas or x0 < cote or x1 > W - cote:
            fautes.append(
                f"ZONE DE SECURITE META — cartouche ({x0},{y0})-({x1},{y1}) "
                f"deborde (haut {haut:.0f}, bas {H-bas:.0f}, cotes {cote:.0f})"
            )
            ok = False
        elif y1 > H - bas_reels:
            avertissements.append(
                f"ZONE REELS (non bloquant) — cartouche ({x0},{y0})-({x1},{y1}) descend sous "
                f"y={H-bas_reels:.0f} : vérifie les marges Reels/Stories à jour sur ton format"
            )

        # 3. de la place perdue au-dessus
        # On regarde la bande utile entre la zone Meta haute et le cartouche :
        # si elle est vide de produit ET de texte, la place etait la.
        # Un second cartouche empilé (ex. un sous-titre au-dessus d'une carte) doit compter comme
        # non-vide au même titre que le produit pour ce calcul précis, sinon la bande au-dessus se
        # ferait juger comme si le premier cartouche n'existait pas.
        yh = int(haut)
        if y0 - yh > VIDE_BANDE_MIN * H:
            bande = slice(yh, y0)
            occupe = produit.copy()
            for (ax0, ay0, ax1, ay1) in cartes:
                if (ax0, ay0, ax1, ay1) != (x0, y0, x1, y1):
                    occupe[ay0:ay1, ax0:ax1] = True
            # La bande utile exclut les marges latérales Meta, sinon le vide est surestimé.
            xc0, xc1 = int(cote), int(W - cote)
            vide = 1.0 - (occupe[bande, xc0:xc1].sum() / max(1, (y0 - yh) * (xc1 - xc0)))
            if vide > VIDE_HAUT_MAX:
                fautes.append(
                    f"ESPACE PERDU — {vide*100:.0f} % de vide entre le haut du cadre "
                    f"et le cartouche pose a y={y0}. La place etait au-dessus."
                )
                ok = False
            elif vide > VIDE_HAUT_ALERTE:
                avertissements.append(
                    f"VIDE (non bloquant) — {vide*100:.0f} % de vide au-dessus du cartouche y={y0} "
                    f"(aligne ce seuil avec ton contrôleur de statics si tu en as un)"
                )

        if annot:
            annot.rectangle([x0, y0, x1, y1], outline=(255, 60, 60) if not ok else (60, 220, 120), width=4)

    if annot:
        # Le produit en surbrillance, pour qu'on voie ce que le cartouche mord.
        md = np.zeros((H, W, 4), dtype=np.uint8)
        md[produit] = (60, 140, 255, 70)
        masque_img = Image.fromarray(md, "RGBA")
        im = Image.alpha_composite(im.convert("RGBA"), masque_img).convert("RGB")
        d2 = ImageDraw.Draw(im)
        d2.rectangle([0, 0, W, haut], outline=(255, 200, 0), width=3)
        d2.rectangle([0, H - bas, W, H], outline=(255, 200, 0), width=3)
        d2.line([0, H - bas_reels, W, H - bas_reels], fill=(255, 120, 0), width=2)
        im.save(sortie, quality=88)

    return {"fautes": fautes, "avertissements": avertissements, "cartes": len(cartes)}


def controler(video: Path) -> int:
    dossier = video.parent / "_controle" / video.stem
    dossier.mkdir(parents=True, exist_ok=True)
    imgs = frames(video)
    if not imgs:
        print(f"\n=== {video.name} — AUCUNE image extraite : fichier sans piste vidéo ou tronqué → REFUS")
        return 1
    total, avec_faute, avec_carte = 0, 0, 0
    resume: dict[str, int] = {}
    avert: dict[str, int] = {}

    print(f"\n=== {video.name} — {len(imgs)} images controlees ===")
    try:
        for i, p in enumerate(imgs, 1):
            r = controler_image(p, dossier / f"{i:03d}.jpg")
            total += 1
            if r["cartes"]:
                avec_carte += 1
            for x in r["avertissements"]:
                cle = x.split(" —")[0]
                avert[cle] = avert.get(cle, 0) + 1
            if r["fautes"]:
                avec_faute += 1
                for x in r["fautes"]:
                    cle = x.split(" —")[0]
                    resume[cle] = resume.get(cle, 0) + 1
                if avec_faute <= 3:      # on montre les trois premieres en detail
                    print(f"\n  image {i} :")
                    for x in r["fautes"]:
                        print("    -", x)
    finally:
        shutil.rmtree(imgs[0].parent, ignore_errors=True)

    print(f"\n  {avec_faute}/{total} images en faute")
    for k, n in sorted(resume.items(), key=lambda kv: -kv[1]):
        print(f"    {k} : {n} images")
    for k, n in sorted(avert.items(), key=lambda kv: -kv[1]):
        print(f"    avertissement {k} : {n} images")
    print(f"  images annotees : {dossier}")
    # « aucun cartouche vu » n'est pas « conforme » — soit la vidéo n'a pas de texte (un livrable en
    # a toujours : mot-symbole, titre), soit L_CARTE ne le voit pas (cartouche d'une couleur que le
    # seuil ne capte pas). On refuse et on demande l'œil.
    if avec_carte == 0:
        print(f"  REFUS — aucun cartouche detecte sur AUCUNE image (seuil L_CARTE={L_CARTE}) : "
              "soit la video n'a pas de texte, soit le controleur ne le voit pas. Regarde les images.")
        return 1
    return 1 if avec_faute else 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cible = Path(sys.argv[1])
    extensions = ("*.mp4", "*.mov", "*.webm", "*.m4v", "*.MP4", "*.MOV")
    videos = sorted({v for e in extensions for v in cible.rglob(e)
                     if "_controle" not in v.parts and "_pipeline" not in v.parts}) \
        if cible.is_dir() else [cible]
    if not videos:
        print(f"Aucune video dans {cible}")
        return 1
    code = 0
    for v in videos:
        code |= controler(v)
    print("\nVERDICT :", "REFUSE — corrige avant de livrer." if code else "conforme.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
