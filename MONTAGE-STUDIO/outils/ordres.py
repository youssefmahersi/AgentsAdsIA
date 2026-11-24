#!/usr/bin/env python3
"""Boîte d'ordres de Studio Ads, côté agent.

  python3 outils/ordres.py liste            # ordres nouveaux et pris
  python3 outils/ordres.py liste --tout     # tous les ordres
  python3 outils/ordres.py pris <id>        # je prends l'ordre
  python3 outils/ordres.py fait <id>        # c'est fait
  python3 outils/ordres.py repondre <id> "texte"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from serveur import ordres  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description="Boîte d'ordres de Studio Ads")
    sp = p.add_subparsers(dest="cmd", required=True)
    l = sp.add_parser("liste")
    l.add_argument("--tout", action="store_true")
    for c in ("pris", "fait"):
        sp.add_parser(c).add_argument("id")
    r = sp.add_parser("repondre")
    r.add_argument("id")
    r.add_argument("texte")
    a = p.parse_args(argv)
    if a.cmd == "liste":
        for o in ordres.lister():
            if not a.tout and o["statut"] == "fait":
                continue
            tc = f" @ {o['timecode']:.2f}s" if o.get("timecode") is not None else ""
            plan = f" plan {o['plan']}" if o.get("plan") else ""
            print(f"[{o['statut']:7}] {o['id']}  {o['date']}  {o.get('nature', 'ordre').upper()}"
                  f"  {o.get('projet') or '-'}{tc}{plan}\n          {o['texte']}")
            for pc in o.get("pieces") or []:
                print(f"          pièce : {pc}")
            for rep in o.get("reponses", []):
                print(f"          ↳ {rep['auteur']} : {rep['texte'][:200]}")
        return 0
    if a.cmd in ("pris", "fait"):
        ok = ordres.changer_statut(a.id, a.cmd)
        print("OK" if ok else "Ordre introuvable.")
        return 0 if ok else 1
    if not any(o["id"] == a.id for o in ordres.lister()):
        print("Ordre introuvable.")
        return 1
    ordres.repondre(a.id, a.texte)
    print("Réponse ajoutée.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
