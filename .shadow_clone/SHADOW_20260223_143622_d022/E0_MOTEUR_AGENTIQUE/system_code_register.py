# ERGO_ID: CODE_REGISTER
"""
system_code_register.py
Greffier CLI — enregistre chaque action de code dans SYSTEM_LOG.json.
Traçabilité complète de l'infrastructure : qui a créé quoi, quand, pourquoi.
Appelable directement en CI/CD sans intervention humaine.

Usage :
    python system_code_register.py --fichier agent.py --action CREATED --detail "Pipeline principal"
    python system_code_register.py --fichier .gitlab-ci.yml --action UPDATED --detail "Ajout stage audit"
    python system_code_register.py --list
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent.parent
SYSTEM_LOG = Path(__file__).parent / "SYSTEM_LOG.json"

ACTIONS_VALIDES = [
    "CREATED",      # fichier créé pour la première fois
    "UPDATED",      # fichier modifié
    "DELETED",      # fichier supprimé
    "TESTED",       # fichier testé avec succès
    "FAILED",       # fichier testé avec échec
    "DEPLOYED",     # fichier déployé en CI/CD
    "REVIEWED",     # fichier relu et validé
    "DEPRECATED",   # fichier marqué obsolète
]

# ─────────────────────────────────────────────
# LECTURE / ÉCRITURE LOG
# ─────────────────────────────────────────────

def lire_log() -> list:
    if not SYSTEM_LOG.exists():
        return []
    try:
        return json.loads(SYSTEM_LOG.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[ERROR] SYSTEM_LOG.json corrompu — réinitialisation", file=sys.stderr)
        return []


def ecrire_log(entrees: list):
    SYSTEM_LOG.write_text(
        json.dumps(entrees, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def ajouter_entree(fichier: str, action: str, detail: str, auteur: str) -> dict:
    entrees = lire_log()
    iteration = len(entrees) + 1
    entree = {
        "iteration": iteration,
        "timestamp": datetime.now().isoformat(),
        "fichier": fichier,
        "action": action,
        "detail": detail,
        "auteur": auteur,
        "ergo_id": f"ERGO_{iteration:04d}"
    }
    entrees.append(entree)
    ecrire_log(entrees)
    return entree


# ─────────────────────────────────────────────
# AFFICHAGE
# ─────────────────────────────────────────────

def afficher_log(n: int = None):
    entrees = lire_log()
    if not entrees:
        print("[INFO] SYSTEM_LOG.json vide — aucune entrée.")
        return

    affichees = entrees[-n:] if n else entrees
    print(f"\n{'─'*60}")
    print(f"  SYSTEM_LOG — {len(entrees)} entrées totales")
    print(f"{'─'*60}")
    for e in affichees:
        print(f"  [{e['ergo_id']}] {e['timestamp'][:19]}")
        print(f"  {e['action']:12} → {e['fichier']}")
        if e.get('detail'):
            print(f"  {'':12}   {e['detail']}")
        print()


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ERGO Code Register — traçabilité infrastructure KOS_COMPTA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Actions valides : {', '.join(ACTIONS_VALIDES)}"
    )
    parser.add_argument("--fichier",  type=str, help="Nom du fichier concerné")
    parser.add_argument("--action",   type=str, choices=ACTIONS_VALIDES, help="Type d'action")
    parser.add_argument("--detail",   type=str, default="", help="Description de l'action")
    parser.add_argument("--auteur",   type=str, default="CI/CD", help="Auteur (défaut: CI/CD)")
    parser.add_argument("--list",     action="store_true", help="Afficher les dernières entrées")
    parser.add_argument("--last",     type=int, default=10, help="Nombre d'entrées à afficher avec --list")

    args = parser.parse_args()

    # Affichage du log
    if args.list:
        afficher_log(args.last)
        sys.exit(0)

    # Validation ajout entrée
    if not args.fichier or not args.action:
        parser.error("--fichier et --action sont obligatoires pour enregistrer une entrée")

    entree = ajouter_entree(
        fichier=args.fichier,
        action=args.action,
        detail=args.detail,
        auteur=args.auteur
    )

    print(f"[{entree['ergo_id']}] {entree['action']} → {entree['fichier']} — enregistré", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
