"""Aperçu local du gabarit (le vrai Liquid des sections, rendu avec python-liquid + filtres Shopify simulés).
Usage : PYTHONPATH=<python-liquid> python3.13 apercu.py
Sert uniquement aux captures quand aucun thème Shopify n'est accessible. Ne remplace pas la préversion Shopify."""
import json, re, shutil, html, pathlib
from liquid import Environment, FileSystemLoader

RACINE = pathlib.Path(__file__).resolve().parent.parent
THEME = RACINE / "theme"
SORTIE = RACINE / "preview"
PROJET = RACINE.parent  # produits/poele-titane
LIV = PROJET.parent.parent / "livraisons/2026-11-22/poele-titane"

(SORTIE / "img").mkdir(parents=True, exist_ok=True)
fichiers = {
    "packshot": PROJET / "packshots/gemini/02-packshot-fond-blanc.webp",
    "texture": PROJET / "packshots/gemini/04-detail-texture.webp",
    "s_usvsthem": LIV / "MOFU/B0001_02_PfasFree_HomeCooks_MOFU_Static_UsVsThem_1x1.jpg",
    "s_oeuf": LIV / "TOFU/B0001_01_EggTest_HomeCooks_TOFU_Static_Headline_1x1.jpg",
    "s_pack2": LIV / "BOFU/B0001_03_Pack2Gift_GiftBuyers_BOFU_Static_Offer_1x1.jpg",
}
img = {}
for k, f in fichiers.items():
    shutil.copy(f, SORTIE / "img" / f.name)
    img[k] = {"src": "img/" + f.name, "width": 1080, "height": 1080, "alt": "", "media_type": "image"}
for v in img.values():
    v["preview_image"] = dict(v)

product = {
    "title": "Poêle Titanixxx — surface titane, sans PFAS",
    "available": True,
    "featured_image": img["packshot"],
    "media": [img["packshot"], img["texture"]],
    "price_min": 5999,
    "variants": [
        {"id": 101, "price": 5999, "title": "1 poêle", "available": True},
        {"id": 102, "price": 9999, "title": "Lot de 2 poêles", "available": True},
    ],
}
product["selected_or_first_available_variant"] = product["variants"][0]

def money(c): 
    c = int(c); return f"{c // 100},{c % 100:02d} €"
def image_url(o, **kw): return o["src"] if isinstance(o, dict) else str(o)
def image_tag(url, **kw):
    kw.pop("widths", None)
    attrs = " ".join(f'{k}="{html.escape(str(v))}"' for k, v in kw.items() if v is not None)
    return f'<img src="{url}" {attrs}>'
def asset_url(n): return "../theme/assets/" + n
def stylesheet_tag(u): return f'<link rel="stylesheet" href="{u}">'
def payment_type_svg_tag(t, **kw):
    return f'<svg class="{kw.get("class","")}" viewBox="0 0 38 24" role="img" aria-label="{t}"><rect width="38" height="24" rx="3" fill="#eef1f5" stroke="#cfd5dd"/><text x="19" y="15" font-size="7" text-anchor="middle" fill="#46546a" font-family="sans-serif">{t[:6]}</text></svg>'
def video_tag(*a, **k): return ""

env = Environment(loader=FileSystemLoader(THEME / "snippets", ext=".liquid"))
for n, f in dict(money=money, image_url=image_url, image_tag=image_tag, asset_url=asset_url,
                 stylesheet_tag=stylesheet_tag, payment_type_svg_tag=payment_type_svg_tag,
                 video_tag=video_tag, external_video_tag=video_tag).items():
    env.filters[n] = (lambda fn: (lambda _ctx, *a, **k: fn(*a, **k)))(f)

def defauts(liste):
    return {s["id"]: s.get("default") for s in liste if "id" in s}

tpl = json.loads((THEME / "templates/product.titanixxx-poele.json").read_text())
css, corps = [], []
for cle in tpl["order"]:
    sec = tpl["sections"][cle]
    src = (THEME / "sections" / (sec["type"] + ".liquid")).read_text()
    schema = json.loads(re.search(r"{% schema %}(.*?){% endschema %}", src, re.S).group(1))
    m = re.search(r"{% stylesheet %}(.*?){% endstylesheet %}", src, re.S)
    if m and m.group(1) not in css: css.append(m.group(1))
    src = re.sub(r"{% schema %}.*?{% endschema %}", "", src, flags=re.S)
    src = re.sub(r"{% (stylesheet|javascript) %}.*?{% end\1 %}", "", src, flags=re.S)
    src = src.replace("{% render block %}", "")
    settings = defauts(schema.get("settings", [])); settings.update(sec.get("settings", {}))
    btypes = {b["type"]: b for b in schema.get("blocks", [])}
    blocks = []
    for bk in sec.get("block_order", []):
        b = sec["blocks"][bk]
        bs = defauts(btypes[b["type"]].get("settings", [])); bs.update(b.get("settings", {}))
        for k, v in list(bs.items()):
            if isinstance(v, str) and v.startswith("shopify://shop_images/"):
                nom = v.split("/")[-1]
                bs[k] = next((i for i in img.values() if i["src"].endswith(nom)), None)
        blocks.append({"type": b["type"], "settings": bs, "shopify_attributes": ""})
    section = {"id": cle, "settings": settings, "blocks": blocks}
    ctx = dict(section=section, product=product, routes={"cart_add_url": "/cart/add"},
               shop={"enabled_payment_types": ["visa", "master", "american_express", "paypal", "apple_pay", "google_pay", "shopify_pay"]})
    rendu = env.parse(src).render(ctx)
    classe = schema.get("class", "")
    corps.append(f'<{schema.get("tag","div")} id="shopify-section-{cle}" class="shopify-section {classe}">{rendu}</{schema.get("tag","div")}>')

page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>APERÇU LOCAL — Poêle Titanixxx</title>
<style>body{{margin:0}} .apercu-entete{{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid #e6e8ec;font:600 13px/1.3 system-ui;color:#46546a;background:#fafbfc}}
.apercu-pied{{padding:28px 16px;background:#010101;color:#9aa7b8;font:500 12px/1.4 system-ui;text-align:center}}
{''.join(css)}</style></head><body>
<header class="apercu-entete"><span>[En-tête du thème de la boutique, non modifié]</span><span>Panier</span></header>
{''.join(corps)}
<footer class="apercu-pied">[Pied de page du thème de la boutique, non modifié]</footer>
<script src="../theme/assets/ttx-base.js" defer></script>
</body></html>"""
(SORTIE / "index.html").write_text(page, encoding="utf-8")
print("aperçu écrit :", SORTIE / "index.html")
