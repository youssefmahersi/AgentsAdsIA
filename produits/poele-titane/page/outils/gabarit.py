"""Génère templates/product.titanixxx-poele.json (contenu de la page). Lancer : python3 gabarit.py"""
import json, pathlib

def blocs(liste):
    out, order = {}, []
    for i, (typ, settings) in enumerate(liste, 1):
        k = f"{typ}-{i}"
        out[k] = {"type": typ, "settings": settings}
        order.append(k)
    return out, order

COLLECTE = "Comment ces avis sont collectés : [À COMPLÉTER par l'utilisateur]"
INTITULE = "Avis clients recueillis par notre fabricant sur ce modèle de poêle"

def avis(nom, texte, titre="", note=5):
    return ("avis", {"nom": nom, "note": note, "titre": titre, "texte": texte})

sections = {}
order = []
def add(key, typ, settings, bl=None):
    s = {"type": typ, "settings": settings}
    if bl:
        s["blocks"], s["block_order"] = blocs(bl)
    sections[key] = s
    order.append(key)

add("annonce", "ttx-annonce", {}, [
    ("message", {"texte": "SANS PFAS — SANS REVÊTEMENT ANTIADHÉSIF"}),
    ("message", {"texte": "LOT DE 2 : ÉCONOMISEZ 20,00 €"}),
])

acc = lambda t, c: ("accordeon", {"titre": t, "contenu": c})
add("produit", "ttx-produit", {
    "offre_par_defaut": 1,
    "afficher_emplacements": True,
    "emplacements_galerie": "Image 1 : packshot + 1 à 4 badges vrais (Sans PFAS, Sans revêtement, Titane · Alu · Inox, 30 jours)\nComparatif : poêle à revêtement rayée / surface titane (sans bouton ni prix)\nManche : fixation réelle (fixe ou amovible, à vérifier)\nCoupe 3 couches : titane / aluminium / inox\nŒuf au plat dans la vraie poêle (sans bouton ni prix)\nLot de 2 poêles (sans prix)",
    "avis_intitule": INTITULE,
    "avis_collecte": COLLECTE,
}, [
    ("sur_titre", {"texte": "SANS PFAS · SANS REVÊTEMENT"}),
    ("titre", {"texte": "Poêle Surface Titane Pour Une Cuisine Sans PFAS"}),
    ("sous_titre", {"texte": "La surface en titane pour cuisiner sans revêtement antiadhésif au quotidien, pour toute votre famille."}),
    ("puce", {"texte": "Relief martelé <strong>sans revêtement antiadhésif</strong>"}),
    ("puce", {"texte": "Surface de cuisson <strong>sans PFAS</strong>"}),
    ("puce", {"texte": "Fabriquée en <strong>titane, aluminium et inox</strong>"}),
    ("puce", {"texte": "Garantie <strong>3 mois</strong> + garantie légale de 2 ans"}),
    ("encart", {"titre": "30 JOURS POUR CHANGER D'AVIS", "sous_titre": "REMBOURSÉ", "texte": "Conditions dans notre <a href=\"/policies/refund-policy\">politique de retour</a>."}),
    ("titre_offres", {"texte": "CHOISISSEZ VOTRE OFFRE"}),
    ("offre", {"titre": "1x Poêle Titanixxx", "variante": 1, "quantite_ref": 1, "afficher_pourcentage": True, "badge": "", "sous_titre": ""}),
    ("offre", {"titre": "Set 2 Poêles Titanixxx", "variante": 2, "quantite_ref": 2, "afficher_pourcentage": True, "badge": "", "sous_titre": ""}),
    ("badges", {"badge_1": "30 jours pour changer d'avis", "badge_2": "Sans PFAS"}),
    ("bouton", {"texte": "➜ AJOUTER AU PANIER"}),
    ("paiements", {}),
    ("avis_court", {"nom": "Catherine M.", "note": 5, "titre": "", "texte": "Premier poulet dans ma nouvelle poêle. J'avoue que j'avais un peu peur que ça accroche sans revêtement mais pas du tout. Même le nettoyage n'a pris que deux minutes. Ravie de mon achat."}),
    acc("RELIEF MARTELÉ SANS REVÊTEMENT", "<p>La surface de cuisson Titanixxx est en titane martelé, sans le moindre revêtement antiadhésif. Son relief en écailles est travaillé directement dans le métal.</p><p>✓ <strong>Aucun revêtement antiadhésif</strong> — rien n'est posé sur le titane</p><p>✓ <strong>Relief martelé</strong> — sur toute la surface de cuisson</p><p>✓ <strong>Sans PFAS</strong> — confirmé par un rapport de laboratoire</p>"),
    acc("SANS PFAS NI REVÊTEMENT", "<p>La plupart des poêles du commerce ont un revêtement antiadhésif. La poêle Titanixxx n'en a aucun : vous cuisinez directement sur le titane.</p><p>✓ <strong>Sans PFAS</strong> — confirmé par un rapport de laboratoire</p><p>✓ <strong>Sans revêtement antiadhésif</strong> — une surface en titane nu</p><p>✓ <strong>3 couches</strong> — titane, aluminium, inox</p>"),
    acc("TITANE, ALUMINIUM ET INOX", "<p>Une poêle en trois couches, chacune à sa place.</p><p>✓ <strong>Surface de cuisson en titane</strong> — martelée, sans revêtement</p><p>✓ <strong>Noyau en aluminium</strong> — au cœur de la poêle</p><p>✓ <strong>Base en inox</strong> — sous la poêle</p>"),
    acc("GARANTIE & LIVRAISON", "<p>✓ <strong>Garantie commerciale de 3 mois</strong> — en plus de la garantie légale de conformité de 2 ans</p><p>✓ <strong>30 jours pour changer d'avis</strong> — remboursé, conditions dans notre <a href=\"/policies/refund-policy\">politique de retour</a></p><p>✓ <strong>Suivi de commande</strong> — numéro de suivi envoyé par e-mail dès l'expédition</p><p>✓ <strong>Une question ?</strong> — écrivez-nous via notre formulaire de contact</p>"),
])

add("videos", "ttx-videos", {"titre": "TITANIXXX EN ACTION", "afficher_emplacements": True}, [
    ("video", {"legende": "", "brief": "Vidéo verticale : œuf au plat dans la vraie poêle"}),
    ("video", {"legende": "", "brief": "Vidéo verticale : steak saisi dans la vraie poêle"}),
    ("video", {"legende": "", "brief": "Vidéo verticale : nettoyage à l'éponge"}),
    ("video", {"legende": "", "brief": "Vidéo verticale : gros plan relief martelé"}),
])

add("avis_cartes", "ttx-avis", {
    "style": "cartes", "surtitre": "",
    "titre": "Ils ont retrouvé le plaisir <strong>de cuisiner sans revêtement</strong>",
    "intitule": INTITULE, "collecte": COLLECTE,
}, [
    avis("Véronique S.", "J'ai filmé ma première recette avec cette poêle. J'en pouvais plus de cuisiner avec un truc qui s'écaillait. Maintenant je peux cuisiner sereine et rien n'accroche. Je la recommande à 100% !!"),
    avis("Didier B.", "Rien n'accroche ! Je ne pensais pas que c'était possible sans revêtement et pourtant même les œufs se décollent sans le moindre effort. Agréablement surpris."),
    avis("Gérard P.", "C'est moi qui cuisine à la maison depuis que je suis à la retraite et franchement j'aurais dû l'avoir bien avant. Elle chauffe vite et rien n'accroche. On n'utilise plus aucune autre poêle chez nous."),
    avis("Jean-Marc D.", "Je cuisine depuis plus de trente ans et j'ai toujours travaillé avec de l'inox. Quand j'ai vu qu'elle saisissait mieux que mes vieilles poêles de métier j'étais sidéré. Le titane, c'est du sérieux."),
    avis("Éléna R.", "Ma spécialité c'est les boulettes de viande. Avec mes anciennes poêles ça collait et je devais toujours gratter le fond. Sur cette poêle ça glisse tout seul et la cuisson est toujours parfaite."),
])

add("raisons", "ttx-raisons", {
    "etiquette": "5 RAISONS",
    "titre": "Pourquoi choisir Titanixxx pour votre prochaine poêle",
    "intro": "La poêle à surface titane, sans revêtement et sans PFAS.",
    "cta": "JE COMMANDE MA POÊLE EN TITANE ➜", "cta_lien": "", "afficher_emplacements": True,
}, [
    ("raison", {"titre": "UNE SURFACE EN TITANE MARTELÉ", "texte": "<p>La surface de cuisson est en <strong>titane</strong>, avec un <strong>relief martelé</strong> en écailles travaillé dans le métal. Aucun revêtement antiadhésif n'est posé dessus.</p>", "image": "shopify://shop_images/04-detail-texture.webp", "brief": "Macro du relief martelé"}),
    ("raison", {"titre": "CUISINEZ SANS PFAS NI REVÊTEMENT", "texte": "<p>Aucun <strong>revêtement antiadhésif</strong> sur la surface de cuisson : vous cuisinez directement sur le <strong>titane</strong>. L'absence de PFAS est <strong>confirmée par un rapport de laboratoire</strong>.</p>", "brief": "Vraie poêle sur le feu, cuisson en cours, fond clair"}),
    ("raison", {"titre": "TITANE, ALUMINIUM ET INOX", "texte": "<p>Trois couches : une <strong>surface de cuisson en titane</strong>, un <strong>noyau en aluminium</strong> et une <strong>base en inox</strong>.</p>", "brief": "Coupe 3 couches titane / aluminium / inox (infographie, contain)"}),
    ("raison", {"titre": "30 JOURS POUR L'ESSAYER CHEZ VOUS", "texte": "<p>Vous la testez dans votre cuisine. Si elle ne vous convient pas, vous avez <strong>30 jours pour changer d'avis</strong> et être <strong>remboursé</strong>. Conditions dans notre <a href=\"/policies/refund-policy\">politique de retour</a>.</p>", "brief": "Vraie poêle dans une cuisine de particulier, lumière naturelle"}),
    ("raison", {"titre": "GARANTIE 3 MOIS + GARANTIE LÉGALE 2 ANS", "texte": "<p>Votre poêle est couverte par notre <strong>garantie commerciale de 3 mois</strong>, en plus de la <strong>garantie légale de conformité de 2 ans</strong> qui s'applique à tout achat en Europe.</p>", "brief": "Vraie poêle et son colis réel (boîte réelle ou sans boîte)"}),
])

add("probleme", "ttx-probleme", {
    "etiquette": "LE PROBLÈME", "afficher_emplacements": True,
    "titre": "Les poêles à revêtement finissent par s'user",
    "intro": "Derrière les belles promesses, le revêtement antiadhésif se raye, s'use, et la poêle se rachète.",
}, [
    ("carte", {"brief": "Aliments collés dans une poêle à revêtement usée (sans marque)", "titre": "Tout finit par coller", "texte": "<p>Le revêtement s'use à chaque cuisson. Les aliments accrochent, il faut toujours plus de gras, <strong>et le plat est quand même raté.</strong></p>"}),
    ("carte", {"brief": "Gros plan d'un revêtement antiadhésif rayé (sans marque)", "titre": "Un revêtement qui se raye", "texte": "<p>À force de spatules et de coups d'éponge, le revêtement antiadhésif se raye. <strong>C'est pour ça que beaucoup cherchent une poêle sans revêtement.</strong></p>"}),
    ("carte", {"brief": "Vieilles poêles usées empilées (sans marque)", "titre": "À racheter régulièrement", "texte": "<p>Le revêtement s'use, la poêle part à la poubelle. <strong>Pas chères à l'achat, elles se rachètent encore et encore.</strong></p>"}),
])

add("avis_bandeau", "ttx-avis", {
    "style": "bandeau", "surtitre": "AVIS CLIENTS", "titre": "",
    "intitule": INTITULE, "collecte": COLLECTE,
}, [
    avis("Nathalie P.", "Je ne suis pas du genre à me prendre la tête, mais là ça m'a marqué. Avant, je cuisinais sans vraiment réfléchir à la surface… maintenant je fais attention. C'est devenu automatique, et honnêtement ça change tout dans ma façon de voir la cuisine. Mille merci!!", "Je cuisine plus sereinement"),
    avis("Sabrina T.", "Je cuisine vite fait en rentrant du taf, et ça me saoulait que ça colle ou que ça brûle. Là c'est propre, rapide, efficace. J'ai gagné du temps et moins de prise de tête.", "Moins de prise de tête"),
    avis("Camille F.", "Honnêtement, ça m'a réconcilié avec la cuisine. C'est facile à utiliser, ça ne colle presque pas, et je n'ai pas besoin de réfléchir à chaque geste.", "Simple, rapide, sans stress."),
    avis("Elodie J.", "J'ai testé pas mal de poêles, et celle-ci est vraiment différente. La cuisson est plus régulière, plus propre, et surtout je sens mieux la maîtrise. Rien à voir avec les poêles revêtues.", "On sent la différence"),
])

add("rappel", "ttx-rappel-offre", {
    "titre_offres": "CHOISISSEZ VOTRE OFFRE", "offre_par_defaut": 1,
    "badge_1": "30 jours pour changer d'avis", "badge_2": "Sans PFAS", "cta": "➜ AJOUTER AU PANIER",
}, [
    ("offre", {"titre": "1x Poêle Titanixxx", "variante": 1, "quantite_ref": 1, "afficher_pourcentage": True, "badge": "", "sous_titre": ""}),
    ("offre", {"titre": "Set 2 Poêles Titanixxx", "variante": 2, "quantite_ref": 2, "afficher_pourcentage": True, "badge": "", "sous_titre": ""}),
])

q = lambda a, b: ("question", {"question": a, "reponse": b})
add("faq", "ttx-faq", {"titre": "FAQ – TITANIXXX"}, [
    q("Pourquoi le titane et pas une poêle antiadhésive classique ?", "<p>Parce qu'elle n'a <strong>aucun revêtement antiadhésif</strong>. Vous cuisinez directement sur une surface en titane martelé, posée sur un noyau en aluminium et une base en inox. Et elle est <strong>sans PFAS</strong> : c'est confirmé par un rapport de laboratoire.</p>"),
    q("De quoi est faite la poêle ?", "<p>De trois couches : une <strong>surface de cuisson en titane</strong> martelé, un <strong>noyau en aluminium</strong> et une <strong>base en inox</strong>. Sans revêtement antiadhésif.</p>"),
    q("Quelle est la garantie ?", "<p>Une <strong>garantie commerciale de 3 mois</strong>, en plus de la <strong>garantie légale de conformité de 2 ans</strong>. Si un défaut apparaît, écrivez-nous via notre formulaire de contact.</p>"),
    q("Elle contient vraiment zéro PFAS ?", "<p>Zéro PFAS : c'est <strong>confirmé par un rapport de laboratoire</strong>. Aucun revêtement antiadhésif sur la surface de cuisson.</p>"),
    q("Puis-je me faire rembourser ?", "<p>Oui. Vous avez <strong>30 jours pour changer d'avis</strong> et être remboursé. Les conditions sont détaillées dans notre <a href=\"/policies/refund-policy\">politique de retour</a>.</p>"),
    q("Quels sont les délais de livraison ?", "<p>Les délais varient selon la période et le stock, mais la commande est traitée rapidement après validation. Une fois expédiée, vous recevez une confirmation avec les informations de suivi.</p>"),
    q("Comment suivre ma commande ?", "<p>Dès l'expédition, vous recevez un e-mail avec votre <strong>numéro de suivi</strong>.</p>"),
])

add("reassurance", "ttx-reassurance", {}, [
    ("carte", {"icone": "colis", "titre": "Livraison offerte", "texte": "<p>Offerte sur votre commande.</p>"}),
    ("carte", {"icone": "contact", "titre": "Service client", "texte": "<p>Pour toute demande, écrivez-nous via notre <a href=\"/pages/contact\">formulaire de contact</a>.</p>"}),
    ("carte", {"icone": "garantie", "titre": "Garantie 3 mois", "texte": "<p>En plus de la garantie légale de 2 ans.</p>"}),
    ("carte", {"icone": "paiement", "titre": "Paiements sécurisés", "texte": "<p>Paiement chiffré, géré par Shopify.</p>"}),
])

tpl = {"sections": sections, "order": order}
assert set(sections) == set(order)
p = pathlib.Path(__file__).resolve().parent.parent / "theme/templates/product.titanixxx-poele.json"
p.write_text(json.dumps(tpl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("écrit", p, len(order), "sections")
