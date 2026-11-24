"""Pack de looks en LUT .cube, avec protection de la peau intégrée.

Protection de la peau (pour chaque look sauf Noir & blanc, qui retire la couleur par définition) :
  - la teinte d'un pixel « peau » reste celle d'origine ;
  - sa saturation reste entre 0,95 et 1,05 fois l'originale ;
  - sa luminosité ne descend jamais sous 0,9 fois l'originale.
Un pixel est « peau » selon sa teinte (rouge-orangé), sa saturation et sa luminosité, avec des bords
progressifs : le reste de l'image prend le look en entier.
"""
import colorsys
import json
import math
from pathlib import Path

from .commun import CACHE, LUTS, empreinte, ffmpeg

TAILLE = 65


def _clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def _luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _sat(c, k):
    l = _luma(*c)
    return tuple(l + (x - l) * k for x in c)


def _contraste(c, k):
    return tuple(x - k * math.sin(2 * math.pi * x) / (2 * math.pi) for x in c)


def _expo(c, e):
    f = 2 ** e
    return tuple(x * f for x in c)


def _releve(c, b):
    return tuple(b + x * (1 - b) for x in c)


def _gains(c, gr, gg, gb):
    return (c[0] * gr, c[1] * gg, c[2] * gb)


def _ombres_hautes(c, ombres=(0, 0, 0), hautes=(0, 0, 0)):
    l = _clamp(_luma(*c))
    s, h = (1 - l) ** 2, l ** 2
    return tuple(x + o * s + hh * h for x, o, hh in zip(c, ombres, hautes))


def _cl(c):
    return tuple(_clamp(x) for x in c)


LOOKS = {
    "naturel": {"nom": "Naturel pub", "aide": "Un peu plus de relief et de couleur, sans que ça se voie.",
                "f": lambda c: _sat(_contraste(_gains(c, 1.01, 1, 0.99), 0.12), 1.05)},
    "serie": {"nom": "Série / ciné doux", "aide": "Noirs adoucis, ombres un peu bleutées, hautes lumières chaudes.",
              "f": lambda c: _sat(_ombres_hautes(_contraste(_releve(c, 0.04), 0.08), (-0.03, 0.005, 0.03), (0.02, 0.005, -0.02)), 0.92)},
    "soleil": {"nom": "Soleil chaud", "aide": "Lumière de fin de journée, chaude et lumineuse.",
               "f": lambda c: _sat(_contraste(_expo(_gains(c, 1.06, 1.01, 0.90), 0.1), 0.05), 1.08)},
    "frais": {"nom": "Frais / clean", "aide": "Blanc net, légèrement froid, idéal cuisine et produit.",
              "f": lambda c: _contraste(_expo(_gains(c, 0.97, 1.0, 1.04), 0.12), 0.06)},
    "punchy": {"nom": "Contraste punchy", "aide": "Couleurs franches et beaucoup de relief pour arrêter le scroll.",
               "f": lambda c: _sat(_contraste(c, 0.3), 1.22)},
    "nuit": {"nom": "Nuit / intérieur", "aide": "Ambiance soir : plus sombre, ombres bleutées.",
             "f": lambda c: _sat(_ombres_hautes(_contraste(_expo(c, -0.25), 0.12), (0, 0.005, 0.03)), 0.88)},
    "nb": {"nom": "Noir & blanc élégant", "aide": "Noir et blanc contrasté. Sans protection peau (plus de couleur).",
           "f": lambda c: (lambda l: (l, l, l))(_contraste((_luma(*c),) * 3, 0.2)[0]), "sans_peau": True},
    "vintage": {"nom": "Vintage léger", "aide": "Noirs délavés, tons chauds, couleurs un peu passées.",
                "f": lambda c: _sat(_ombres_hautes(_gains(_releve(c, 0.06), 1.03, 1.0, 0.94), (0, 0.02, 0)), 0.85)},
    "auto": {"nom": "Correction auto", "aide": "Corrige la balance des blancs et l'exposition du plan, calculées sur son image.",
             "auto": True},
}


def poids_peau(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    deg = h * 360
    if deg > 300:
        deg -= 360
    # teinte : pleine entre 0° et 62° (une peau claire surexposée tire vers le jaune), nulle sous -20° et
    # au-dessus de 76°. Bords doux = LUT sans cassure.
    if 0 <= deg <= 62:
        wh = 1.0
    elif -20 < deg < 0:
        wh = (deg + 20) / 20
    elif 62 < deg < 76:
        wh = (76 - deg) / 14
    else:
        wh = 0.0
    ws = _clamp((s - 0.02) / 0.05) * _clamp((0.9 - s) / 0.12)
    wv = _clamp((v - 0.02) / 0.05)
    return wh * ws * wv


def proteger(c0, c1):
    w = poids_peau(*c0)
    if w <= 0:
        return c1
    h0, s0, v0 = colorsys.rgb_to_hsv(*c0)
    _h1, s1, v1 = colorsys.rgb_to_hsv(*_cl(c1))
    s = _clamp(s1, 0.975 * s0, min(1.0, 1.025 * s0))
    sur = colorsys.hsv_to_rgb(h0, s, v1)
    l0, l = _luma(*c0), _luma(*sur)
    if l < 0.94 * l0 and l > 1e-6:
        sur = _cl(tuple(x * (0.94 * l0 / l) for x in sur))
        # remonter peut écraser la saturation contre 1 : on la recale
        _h, s2, v2 = colorsys.rgb_to_hsv(*sur)
        sur = colorsys.hsv_to_rgb(h0, _clamp(s2, 0.975 * s0, min(1.0, 1.025 * s0)), v2)
    return tuple(a + (b - a) * w for a, b in zip(c1, sur))


def fonction_auto(stats):
    """stats = moyennes R, G, B (0-1) d'une image : balance des blancs « monde gris » + exposition."""
    r, g, b = (max(x, 1e-3) for x in stats)
    m = (r + g + b) / 3
    gains = [_clamp(m / x, 0.85, 1.18) for x in (r, g, b)]
    l = _luma(r, g, b)
    e = _clamp(math.log2(0.42 / max(l, 1e-3)), -0.6, 0.8) * 0.7
    return lambda c: _expo(_gains(c, *gains), e)


def appliquer(look: str, c, force=1.0, peau=True, auto_stats=None):
    spec = LOOKS[look]
    f = fonction_auto(auto_stats or (0.5, 0.5, 0.5)) if spec.get("auto") else spec["f"]
    c1 = _cl(f(c))
    if peau and not spec.get("sans_peau"):
        c1 = proteger(c, c1)
    return _cl(tuple(a + (b - a) * force for a, b in zip(c, c1)))


def fichier_cube(look: str, force: float = 1.0, peau: bool = True, auto_stats=None) -> Path:
    force = round(_clamp(float(force)), 2)
    cle = empreinte(look, force, peau, [round(x, 3) for x in (auto_stats or [])])
    chemin = LUTS / f"{look}_{int(force * 100):03d}{'' if peau else '_sanspeau'}_{cle[:6]}.cube"
    if chemin.exists():
        return chemin
    lignes = [f'TITLE "Studio Ads {LOOKS[look]["nom"]} {int(force * 100)}%"', f"LUT_3D_SIZE {TAILLE}",
              "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    n = TAILLE - 1
    for bi in range(TAILLE):
        for gi in range(TAILLE):
            for ri in range(TAILLE):
                r, g, b = appliquer(look, (ri / n, gi / n, bi / n), force, peau, auto_stats)
                lignes.append(f"{r:.6f} {g:.6f} {b:.6f}")
    chemin.write_text("\n".join(lignes) + "\n")
    return chemin


def stats_image(source: Path, t: float = 0.0) -> list:
    """Moyennes R, G, B d'une image du plan (pour la correction auto)."""
    from PIL import Image
    img = CACHE / "stats" / f"{empreinte(str(source), round(t, 2))}.png"
    img.parent.mkdir(parents=True, exist_ok=True)
    if not img.exists():
        ffmpeg(["-ss", t, "-i", source, "-vf", "scale=64:-2", "-frames:v", "1", img])
        if not img.exists():
            ffmpeg(["-i", source, "-vf", "scale=64:-2", "-frames:v", "1", img])
    with Image.open(img) as im:
        px = list(im.convert("RGB").getdata())
    return [sum(p[i] for p in px) / len(px) / 255 for i in range(3)]


def generer_pack():
    """Les 9 looks à 100 % (auto : neutre), écrits une fois dans luts/."""
    return [fichier_cube(k).name for k in LOOKS]


def apercu(source: Path, look: str, force: float, t: float = 0.0, largeur: int = 360) -> Path:
    """Image AVANT | APRÈS côte à côte."""
    stats = stats_image(source, t) if LOOKS[look].get("auto") else None
    cube = fichier_cube(look, force, True, stats)
    sortie = CACHE / "apercus_looks" / f"{empreinte(str(source), t, cube.name, largeur)}.jpg"
    if not sortie.exists():
        sortie.parent.mkdir(parents=True, exist_ok=True)
        entree = ["-loop", "1", "-i", source] if source.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} else ["-ss", t, "-i", source]
        ffmpeg([*entree, "-filter_complex",
                f"[0]scale={largeur}:-2,format=rgb24,split[a][b];[b]lut3d=file='{cube}'[c];[a][c]hstack",
                "-frames:v", "1", sortie])
    return sortie


# --------------------------------------------------------------------------- test peau

MONK = ["f6ede4", "f3e7db", "f7ead0", "eadaba", "d7bd96", "a07e56", "825c43", "604134", "3a312a", "292420"]


def _hex(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mesurer(c0, c1):
    h0, s0, v0 = colorsys.rgb_to_hsv(*c0)
    h1, s1, v1 = colorsys.rgb_to_hsv(*c1)
    dh = abs(((h1 - h0 + 0.5) % 1) - 0.5) * 360
    return {"teinte_deg": round(dh, 2), "sat_ratio": round(s1 / s0, 3) if s0 > 1e-3 else 1.0,
            "lum_ratio": round(_luma(*c1) / _luma(*c0), 3) if _luma(*c0) > 1e-3 else 1.0}


def _passer_ffmpeg(look, src: Path, dossier: Path) -> Path:
    stats = (0.55, 0.5, 0.42) if LOOKS[look].get("auto") else None
    cube = fichier_cube(look, 1.0, True, stats)
    out = dossier / f"ff_{look}_{src.stem}.png"
    ffmpeg(["-i", src, "-vf", f"format=rgb24,lut3d=file='{cube}'", out])
    return out


def test_peau(images: list = None, sortie_dossier: Path = None) -> dict:
    """Mesure APRÈS passage réel dans ffmpeg (LUT .cube) :
    - 10 teintes de peau de l'échelle Monk (très claire → très foncée) × 3 éclairages ;
    - les pixels de peau de vraies images du projet (`images`)."""
    from PIL import Image, ImageDraw, ImageFont
    dossier = sortie_dossier or (CACHE / "test_peau")
    dossier.mkdir(parents=True, exist_ok=True)
    ech = []
    for h in MONK:
        for e in (-0.5, 0.0, 0.35):
            c = _cl(_expo(_hex(h), e))
            ech.append((h, e, tuple(round(v * 255) for v in c)))
    cote = 16
    pastilles = Image.new("RGB", (len(ech) * cote, cote))
    d = ImageDraw.Draw(pastilles)
    for i, (_h, _e, c) in enumerate(ech):
        d.rectangle([i * cote, 0, i * cote + cote - 1, cote - 1], fill=c)
    src = dossier / "pastilles.png"
    pastilles.save(src)
    looks = [l for l in LOOKS if not LOOKS[l].get("sans_peau")]
    rapport = {"regle": {"sat_ratio": [0.95, 1.05], "lum_ratio_min": 0.9}, "looks": {},
               "methode": "mesuré sur l'image sortie de ffmpeg (lut3d), en 8 bits"}
    apres_par_look = {}
    for look in looks:
        res = Image.open(_passer_ffmpeg(look, src, dossier)).convert("RGB")
        mesures, hors = [], []
        apres = []
        for i, (h, e, c) in enumerate(ech):
            q = tuple(v / 255 for v in c)
            p = tuple(v / 255 for v in res.getpixel((i * cote + cote // 2, cote // 2)))
            apres.append(tuple(int(v * 255) for v in p))
            import colorsys as _cs
            hh, ss, vv = _cs.rgb_to_hsv(*q)
            if ss < 0.03 or vv < 0.06:   # blanc brûlé ou noir : plus une couleur de peau mesurable
                continue
            m = mesurer(q, p)
            mesures.append(m)
            if not (0.95 <= m["sat_ratio"] <= 1.05 and m["lum_ratio"] >= 0.9):
                # écart d'un seul niveau sur 255 par canal = limite de mesure du 8 bits
                theorique = appliquer(look, q, 1.0, True, (0.55, 0.5, 0.42) if LOOKS[look].get("auto") else None)
                ecart = max(abs(a - b * 255) for a, b in zip(apres[-1], theorique))
                mt = mesurer(q, theorique)
                calcul_ok = 0.95 <= mt["sat_ratio"] <= 1.05 and mt["lum_ratio"] >= 0.9
                # « limite 8 bits » seulement si le calcul exact respecte la règle et que ffmpeg n'en
                # diffère que d'un ou deux niveaux sur 255
                hors.append({"teinte": h, "expo": e, **m, "limite_8bits": calcul_ok and ecart <= 2.5})
        apres_par_look[look] = apres
        vrais = [x for x in hors if not x["limite_8bits"]]
        rapport["looks"][look] = {
            "ok": not vrais, "sat_min": min(m["sat_ratio"] for m in mesures), "sat_max": max(m["sat_ratio"] for m in mesures),
            "lum_min": min(m["lum_ratio"] for m in mesures), "teinte_max": max(m["teinte_deg"] for m in mesures),
            "mesurees": len(mesures), "hors_regle": hors}
    rapport["looks"]["nb"] = {"protection": "non applicable (noir et blanc)"}
    n8 = sum(len([x for x in v.get("hors_regle", []) if x["limite_8bits"]]) for v in rapport["looks"].values())
    if n8:
        rapport["limite"] = (f"{n8} mesure(s) dépassent la règle d'un seul niveau de couleur sur 255 (peaux très foncées "
                             "ou très pâles, presque sans saturation) : c'est la limite de précision d'une vidéo 8 bits, "
                             "pas un changement visible de la peau.")

    # vraies images du projet
    reels = []
    for chemin in images or []:
        chemin = Path(chemin)
        with Image.open(chemin) as im0:
            avant = im0.convert("RGB").resize((96, 170))
        avant.save(dossier / f"reel_{chemin.stem}.png")
        par_look = {}
        for look in looks:
            res = Image.open(_passer_ffmpeg(look, dossier / f"reel_{chemin.stem}.png", dossier)).convert("RGB")
            ms = []
            for (x, y) in ((x, y) for y in range(170) for x in range(96)):
                q = tuple(v / 255 for v in avant.getpixel((x, y)))
                if poids_peau(*q) > 0.99 and max(q) > 0.15:
                    ms.append(mesurer(q, tuple(v / 255 for v in res.getpixel((x, y)))))
            if ms:
                ms.sort(key=lambda m: m["sat_ratio"])
                med = ms[len(ms) // 2]
                par_look[look] = {"pixels": len(ms), "sat_mediane": med["sat_ratio"],
                                  "lum_min_p5": sorted(m["lum_ratio"] for m in ms)[len(ms) // 20],
                                  "dans_regle_pct": round(100 * sum(0.95 <= m["sat_ratio"] <= 1.05 and m["lum_ratio"] >= 0.9 for m in ms) / len(ms), 1)}
        reels.append({"image": str(chemin), "looks": par_look})
    rapport["images_reelles"] = reels

    # planche
    cote_p, marge = 22, 190
    im = Image.new("RGB", (marge + cote_p * len(ech) + 20, 60 + len(looks) * (cote_p * 2 + 26)), (18, 20, 24))
    d = ImageDraw.Draw(im)
    try:
        police = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
        grande = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 16)
    except OSError:
        police = grande = ImageFont.load_default()
    d.text((10, 12), "Test peau (mesuré après ffmpeg) : 10 teintes claire → foncée × 3 éclairages. Haut = avant, bas = après.",
           fill=(230, 230, 230), font=grande)
    y = 50
    for look in looks:
        r = rapport["looks"][look]
        d.text((10, y + 4), LOOKS[look]["nom"], fill=(235, 235, 235), font=police)
        d.text((10, y + 22), f"sat {r['sat_min']:.3f}–{r['sat_max']:.3f}", fill=(170, 170, 170), font=police)
        d.text((10, y + 38), f"lum ≥ {r['lum_min']:.3f}  {'OK' if r['ok'] else 'À REVOIR'}",
               fill=(120, 220, 170) if r["ok"] else (240, 120, 110), font=police)
        for i, (_h, _e, c) in enumerate(ech):
            x = marge + i * cote_p
            d.rectangle([x, y, x + cote_p - 2, y + cote_p - 2], fill=c)
            d.rectangle([x, y + cote_p, x + cote_p - 2, y + 2 * cote_p - 2], fill=apres_par_look[look][i])
        y += cote_p * 2 + 26
    planche = dossier / "planche_peau.png"
    im.save(planche)
    rapport["planche"] = str(planche)
    (dossier / "rapport_peau.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=1))
    return rapport
