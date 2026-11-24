"""Boîte d'ordres (inbox/ordres.jsonl) et fil de réponses (inbox/reponses.jsonl), en ajout seul.
Le statut d'un ordre = sa dernière ligne d'événement {"id", "statut"} dans ordres.jsonl."""
from .commun import INBOX, ajouter_jsonl, lire_jsonl, maintenant, nouvel_id

ORDRES = INBOX / "ordres.jsonl"
REPONSES = INBOX / "reponses.jsonl"
STATUTS = ("nouveau", "pris", "fait")


def ajouter(texte: str, projet: str = None, timecode: float = None, plan: str = None,
            pieces: list = None, nature: str = "ordre") -> dict:
    o = {"id": nouvel_id("o-"), "date": maintenant(), "nature": nature, "projet": projet,
         "timecode": None if timecode is None else round(float(timecode), 3), "plan": plan,
         "texte": (texte or "").strip()[:4000], "pieces": pieces or [], "statut": "nouveau"}
    ajouter_jsonl(ORDRES, o)
    return o


def changer_statut(oid: str, statut: str) -> bool:
    if statut not in STATUTS or not any(o.get("id") == oid and "texte" in o for o in lire_jsonl(ORDRES)):
        return False
    ajouter_jsonl(ORDRES, {"id": oid, "statut": statut, "date": maintenant(), "evenement": True})
    return True


def repondre(oid: str, texte: str, auteur: str = "Claude") -> dict:
    r = {"id": nouvel_id("r-"), "ordre": oid, "date": maintenant(), "auteur": auteur, "texte": texte.strip()[:8000]}
    ajouter_jsonl(REPONSES, r)
    return r


def lister() -> list:
    ordres, ordre = {}, []
    for ligne in lire_jsonl(ORDRES):
        if ligne.get("evenement"):
            if ligne["id"] in ordres:
                ordres[ligne["id"]]["statut"] = ligne["statut"]
                ordres[ligne["id"]]["maj"] = ligne["date"]
        elif ligne.get("id"):
            ordres[ligne["id"]] = dict(ligne)
            ordre.append(ligne["id"])
    reponses = lire_jsonl(REPONSES)
    for o in ordres.values():
        o["reponses"] = [r for r in reponses if r.get("ordre") == o["id"]]
    return [ordres[i] for i in reversed(ordre)]
