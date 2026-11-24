"""Titres, sous-titres et graphismes dessinés en PNG transparents (ffmpeg de cette machine n'a pas
drawtext) puis posés par-dessus la vidéo avec overlay."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .commun import CACHE, POLICES, empreinte

# Zone sûre Reels / Stories (en fraction de la hauteur) : rien d'important dans le haut 14 %
# (nom du compte) ni dans le bas 30 % (légende, boutons). Côtés : 6 %.
ZONE_SURE = {"haut": 0.14, "bas": 0.70, "cote": 0.06}

STYLES = {
    "sous-titre": {"nom": "Sous-titre majuscules (blanc, contour noir)", "police": "black", "taille": 0.048,
                   "couleur": "#FFFFFF", "contour": "#000000", "epaisseur": 0.11, "maj": True, "pos": "sous-titre"},
    "sous-titre-boite": {"nom": "Sous-titre en boîte noire", "police": "bold", "taille": 0.042,
                         "couleur": "#FFFFFF", "boite": "#000000CC", "pos": "sous-titre"},
    "sous-titre-jaune": {"nom": "Sous-titre jaune", "police": "black", "taille": 0.048, "couleur": "#FFD84D",
                         "contour": "#000000", "epaisseur": 0.11, "maj": True, "pos": "sous-titre"},
    "titre": {"nom": "Gros titre", "police": "black", "taille": 0.07, "couleur": "#FFFFFF", "contour": "#000000",
              "epaisseur": 0.08, "maj": True, "pos": "milieu"},
    "hook": {"nom": "Bandeau de hook (haut)", "police": "black", "taille": 0.05, "couleur": "#111111",
             "boite": "#FFFFFFF2", "maj": False, "pos": "haut"},
    "cta": {"nom": "Carton CTA", "police": "black", "taille": 0.055, "couleur": "#FFFFFF", "boite": "#E8472BFF",
            "maj": True, "pos": "bas-sur"},
    "prix": {"nom": "Prix barré", "police": "black", "taille": 0.06, "couleur": "#FFFFFF", "contour": "#000000",
             "epaisseur": 0.08, "pos": "milieu", "prix": True},
    "nom": {"nom": "Bandeau nom", "police": "bold", "taille": 0.036, "couleur": "#FFFFFF", "boite": "#1B1E24E6",
            "pos": "bas-gauche"},
    "pastille": {"nom": "Pastille (ex. −16 %)", "police": "black", "taille": 0.05, "couleur": "#FFFFFF",
                 "boite": "#E8472BFF", "pos": "haut-droite", "rond": True},
}

ANIMATIONS = {"aucune": "Aucune", "fondu": "Fondu", "glisse": "Glisse du bas", "pop": "Pop"}


def _rgba(h):
    h = h.lstrip("#")
    if len(h) == 6:
        h += "FF"
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))


def _couper(texte, police, largeur_max, dessin):
    lignes = []
    for para in texte.split("\n"):
        mots, courante = para.split(), ""
        for m in mots:
            essai = (courante + " " + m).strip()
            if dessin.textlength(essai, font=police) <= largeur_max or not courante:
                courante = essai
            else:
                lignes.append(courante)
                courante = m
        lignes.append(courante)
    return lignes


def position(style: dict, l: int, h: int, w: int, hh: int):
    """Coin haut-gauche du bloc texte (w×hh) dans une image l×h, en restant en zone sûre."""
    cote = int(l * ZONE_SURE["cote"])
    pos = style.get("pos", "milieu")
    if pos == "haut":
        return (l - w) // 2, int(h * ZONE_SURE["haut"])
    if pos == "sous-titre":   # centre du bloc à 62 % de la hauteur, au-dessus de la zone basse
        return (l - w) // 2, min(int(h * 0.62) - hh // 2, int(h * ZONE_SURE["bas"]) - hh)
    if pos == "bas-sur":
        return (l - w) // 2, int(h * ZONE_SURE["bas"]) - hh
    if pos == "bas-gauche":
        return cote, int(h * ZONE_SURE["bas"]) - hh
    if pos == "haut-droite":
        return l - cote - w, int(h * ZONE_SURE["haut"]) + 10
    return (l - w) // 2, (h - hh) // 2


def rendre(item: dict, l: int, h: int) -> Path:
    """item = {texte, style, [ancien] (prix barré)} → PNG plein cadre transparent."""
    style = {**STYLES.get(item.get("style", "sous-titre"), STYLES["sous-titre"]), **(item.get("reglages") or {})}
    cle = empreinte(item.get("texte"), item.get("ancien"), style, l, h)
    sortie = CACHE / "textes" / f"{cle}.png"
    if sortie.exists():
        return sortie
    sortie.parent.mkdir(parents=True, exist_ok=True)
    texte = item.get("texte") or ""
    if style.get("maj"):
        texte = texte.upper()
    taille = max(12, int(h * style["taille"] * (9 / 16 if l > h else 1)))
    police = ImageFont.truetype(POLICES.get(style["police"], POLICES["bold"]), taille)
    img = Image.new("RGBA", (l, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    largeur_max = int(l * (1 - 2 * ZONE_SURE["cote"])) - (40 if style.get("boite") else 0)
    if style.get("prix"):
        ancien = item.get("ancien") or ""
        petite = ImageFont.truetype(POLICES["bold"], int(taille * 0.6))
        wa = d.textlength(ancien, font=petite) if ancien else 0
        wn = d.textlength(texte, font=police)
        w, hh = int(wa + (30 if ancien else 0) + wn), int(taille * 1.25)
        x, y = position(style, l, h, w, hh)
        ep = max(2, int(taille * style.get("epaisseur", 0.08)))
        if ancien:
            ya = y + int(taille * 0.35)
            d.text((x, ya), ancien, font=petite, fill=(230, 230, 230, 255), stroke_width=ep // 2, stroke_fill=(0, 0, 0, 255))
            d.line([(x - 4, ya + int(taille * 0.33)), (x + wa + 4, ya + int(taille * 0.33))], fill=(232, 71, 43, 255), width=max(3, taille // 12))
        d.text((x + wa + (30 if ancien else 0), y), texte, font=police, fill=_rgba(style["couleur"]),
               stroke_width=ep, stroke_fill=_rgba(style.get("contour", "#000000")))
        img.save(sortie)
        return sortie

    lignes = _couper(texte, police, largeur_max, d)
    interligne = int(taille * 1.18)
    w = int(max(d.textlength(li, font=police) for li in lignes)) if lignes else 0
    hh = interligne * len(lignes)
    pad = int(taille * 0.45) if style.get("boite") else 0
    if style.get("rond"):
        cote_rond = max(w, hh) + 2 * pad + 10
        x, y = position(style, l, h, cote_rond, cote_rond)
        d.ellipse([x, y, x + cote_rond, y + cote_rond], fill=_rgba(style["boite"]))
        d.text((x + cote_rond // 2, y + cote_rond // 2), lignes[0] if lignes else "", font=police,
               fill=_rgba(style["couleur"]), anchor="mm")
        img.save(sortie)
        return sortie
    x, y = position(style, l, h, w + 2 * pad, hh + 2 * pad)
    if style.get("boite"):
        d.rounded_rectangle([x, y, x + w + 2 * pad, y + hh + 2 * pad], radius=int(taille * 0.3), fill=_rgba(style["boite"]))
    ep = int(taille * style.get("epaisseur", 0)) if style.get("contour") else 0
    for i, li in enumerate(lignes):
        lw = d.textlength(li, font=police)
        d.text((x + pad + (w - lw) / 2, y + pad + i * interligne), li, font=police, fill=_rgba(style["couleur"]),
               stroke_width=ep, stroke_fill=_rgba(style.get("contour", "#000000")))
    img.save(sortie)
    return sortie
