# ERGO_ID: DETECT_DOCUMENT
"""
detect_document_type.py
=======================
ERGO KOS_COMPTA — Stage DETECT

Identifie le type de chaque document déposé dans E3.1_Dropzone_Factures
en lisant le frontmatter YAML, puis produit un fichier dotenv pour transmettre
les variables au stage suivant via GitLab CI/CD artifacts:reports:dotenv.

ERGO_REGISTRY:
    version      : 1.0.0
    auteur       : ERGO Capital / Adam
    dependances  : (aucune — lecture seule)
    entrees      : E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/*.md
    sorties      : document_type.env (dotenv GitLab CI/CD)

Variables dotenv produites :
    DOCUMENT_TYPE    : facture_fournisseur | note_de_frais | ecriture | bilan | inconnu
    DOCUMENT_FILE    : nom du premier fichier détecté
    DOCUMENT_TAGS    : tags extraits du frontmatter
    DOCUMENT_COUNT   : nombre total de documents dans la dropzone
    DOCUMENT_N_FILE  : nom du document N (pour chaque document)
    DOCUMENT_N_TYPE  : type du document N
"""

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime


TYPES_VALIDES: dict[str, str] = {
    "soumission_facture":   "facture_fournisseur",
    "facture_fournisseur":  "facture_fournisseur",
    "note_de_frais":        "note_de_frais",
    "ecriture_comptable":   "ecriture",
    "ecriture":             "ecriture",
    "bilan":                "bilan",
    "grand_livre":          "grand_livre",
}


def lire_frontmatter(chemin: Path) -> dict:
    """Extrait les paires clé/valeur du bloc frontmatter YAML d'un fichier Markdown.

    Args:
        chemin: Chemin absolu vers le fichier .md.

    Returns:
        Dictionnaire des champs YAML extraits (valeurs en chaîne brute).
    """
    contenu = chemin.read_text(encoding="utf-8")
    fm: dict = {}
    match = re.search(r"^---\n(.*?)\n---", contenu, re.DOTALL)
    if match:
        for ligne in match.group(1).split("\n"):
            if ":" in ligne:
                cle, _, val = ligne.partition(":")
                fm[cle.strip()] = val.strip()
    return fm


def detecter_type(fm: dict) -> str:
    """Mappe le champ 'type' du frontmatter vers un type de document normalisé.

    Args:
        fm: Dictionnaire frontmatter produit par lire_frontmatter().

    Returns:
        Type normalisé (str) selon TYPES_VALIDES, ou "inconnu" si absent.
    """
    return TYPES_VALIDES.get(fm.get("type", "").lower(), "inconnu")


def scanner_dropzone(dropzone: Path) -> list[dict]:
    """Scanne tous les fichiers .md dans la dropzone et retourne leurs métadonnées.

    Args:
        dropzone: Chemin vers E3.1_Dropzone_Factures.

    Returns:
        Liste de dictionnaires, un par fichier trouvé, contenant :
            - fichier (str)  : nom du fichier
            - type (str)     : type normalisé
            - tags (str)     : tags bruts du frontmatter
            - statut (str)   : valeur du champ 'statut' du frontmatter
            - id (str)       : valeur du champ 'id' ou nom du fichier
    """
    documents: list[dict] = []
    for fichier in sorted(dropzone.glob("*.md")):
        fm        = lire_frontmatter(fichier)
        doc_type  = detecter_type(fm)
        tags      = fm.get("tags", "[]").strip("[]").replace("'", "").replace('"', "")
        documents.append({
            "fichier": fichier.name,
            "type":    doc_type,
            "tags":    tags,
            "statut":  fm.get("statut", "inconnu"),
            "id":      fm.get("id", fichier.stem),
        })
        print(f"  ✓ {fichier.name} → type={doc_type} | tags={tags}")
    return documents


def ecrire_dotenv(documents: list[dict], output: Path) -> None:
    """Produit le fichier dotenv pour GitLab CI/CD artifacts:reports:dotenv.

    Args:
        documents: Liste produite par scanner_dropzone().
        output:    Chemin du fichier .env à écrire.
    """
    if not documents:
        output.write_text(
            "DOCUMENT_TYPE=none\nDOCUMENT_FILE=none\nDOCUMENT_TAGS=\nDOCUMENT_COUNT=0\n",
            encoding="utf-8",
        )
        print("  ⚠ Aucun document trouvé dans la dropzone.")
        return

    premier = documents[0]
    lignes  = [
        f"DOCUMENT_TYPE={premier['type']}",
        f"DOCUMENT_FILE={premier['fichier']}",
        f"DOCUMENT_TAGS={premier['tags']}",
        f"DOCUMENT_COUNT={len(documents)}",
    ]
    for i, doc in enumerate(documents):
        lignes.append(f"DOCUMENT_{i}_FILE={doc['fichier']}")
        lignes.append(f"DOCUMENT_{i}_TYPE={doc['type']}")

    output.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"  ✓ dotenv écrit → {output.name} ({len(documents)} document(s))")


def main() -> None:
    """Point d'entrée CLI du stage DETECT."""
    parser = argparse.ArgumentParser(
        description="ERGO KOS_COMPTA — Stage DETECT : identifie le type de document entrant"
    )
    parser.add_argument("--path",   type=str, required=True, help="Chemin vers E3.1_Dropzone_Factures")
    parser.add_argument("--output", type=str, default="document_type.env", help="Fichier dotenv de sortie")
    args = parser.parse_args()

    dropzone = Path(args.path)
    output   = Path(args.output)

    print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] [DETECT] Scan dropzone → {dropzone}")

    if not dropzone.exists():
        print(f"  [ERROR] Dropzone introuvable : {dropzone}", file=sys.stderr)
        output.write_text("DOCUMENT_TYPE=none\nDOCUMENT_FILE=none\nDOCUMENT_TAGS=\nDOCUMENT_COUNT=0\n")
        sys.exit(0)

    documents = scanner_dropzone(dropzone)
    ecrire_dotenv(documents, output)

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [DETECT] Terminé — {len(documents)} document(s)\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
