# ERGO_ID: DOC_GENERATOR
"""
doc_generator.py
================
ERGO KOS_COMPTA — Générateur de Documentation Markdown

Lit chaque fichier Python portant un header `# ERGO_ID:` dans E0_MOTEUR_AGENTIQUE,
extrait la structure du code (module docstring, ERGO_REGISTRY, fonctions + docstrings,
signatures typées), et génère un fichier `.md` de documentation par composant
dans le dossier `docs/`.

Les fichiers générés suivent un template fixe lisible par un humain ET par un LLM.
Ils servent de référence documentaire versionnable, indépendante du code source.

Chaque doc reçoit un identifiant unique `DOC_XXXX` tracé dans `DOC_INDEX.json`.
La révision s'incrémente automatiquement quand le SHA-256 de la source change.

ERGO_REGISTRY:
    role         : Genere la documentation Markdown versionnee des composants ERGO_ID
    version      : 1.1.0
    auteur       : ERGO Capital / Adam
    dependances  : (stdlib uniquement — ast, re, hashlib, json)
    entrees      : E0_MOTEUR_AGENTIQUE/*.py avec header ERGO_ID
    sorties      : E0_MOTEUR_AGENTIQUE/docs/<ergo_id>.md, E0_MOTEUR_AGENTIQUE/docs/DOC_INDEX.json

Usage :
    python doc_generator.py               # génère tous les docs
    python doc_generator.py --ergo-id COMPLIANCE_AGENT   # un seul composant
    python doc_generator.py --output-dir ./mes_docs       # dossier personnalisé
"""

import argparse
import ast
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


BASE_DIR       = Path(__file__).parent.parent
E0_DIR         = Path(__file__).parent
DOCS_DIR       = E0_DIR / "docs"
DOC_INDEX_FILE = DOCS_DIR / "DOC_INDEX.json"

ERGO_ID_PATTERN  = re.compile(r"^#\s*ERGO_ID:\s*(\w+)", re.MULTILINE)
REGISTRY_PATTERN = re.compile(r"ERGO_REGISTRY:(.*?)(?:\n\n|\Z)", re.DOTALL)
REGISTRY_KV      = re.compile(r"^\s{4}(\w+)\s*:\s*(.+)$", re.MULTILINE)


def sha256_fichier(chemin: Path) -> str:
    """Calcule un SHA-256 tronqué (8 chars) du contenu d'un fichier.

    Args:
        chemin: Chemin absolu vers le fichier à hasher.

    Returns:
        8 premiers caractères du SHA-256 hexadécimal, ou "ABSENT" si le fichier n'existe pas.
    """
    if not chemin.exists():
        return "ABSENT"
    return hashlib.sha256(chemin.read_bytes()).hexdigest()[:8]


def charger_doc_index(docs_dir: Path) -> list[dict]:
    """Charge le DOC_INDEX.json existant depuis le dossier docs/.

    Args:
        docs_dir: Dossier docs/ contenant DOC_INDEX.json.

    Returns:
        Liste des entrées de l'index, ou liste vide si absent ou corrompu.
    """
    index_path = docs_dir / "DOC_INDEX.json"
    if not index_path.exists():
        return []
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        return data.get("docs", [])
    except (json.JSONDecodeError, KeyError):
        return []


def sauvegarder_doc_index(docs_dir: Path, docs: list[dict]) -> None:
    """Persiste le DOC_INDEX.json avec métadonnées globales.

    Args:
        docs_dir: Dossier docs/ cible.
        docs:     Liste complète des entrées de documentation à sauvegarder.
    """
    index_path = docs_dir / "DOC_INDEX.json"
    payload = {
        "generated_at": datetime.now().isoformat(),
        "generateur":   "DOC_GENERATOR",
        "total_docs":   len(docs),
        "docs":         docs,
    }
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def prochain_doc_id(index: list[dict]) -> str:
    """Calcule le prochain identifiant DOC_XXXX séquentiel.

    Args:
        index: Liste actuelle des entrées DOC.

    Returns:
        Identifiant au format "DOC_XXXX" (ex: "DOC_0001").
    """
    if not index:
        return "DOC_0001"
    max_n = 0
    for entree in index:
        try:
            n = int(entree.get("doc_id", "DOC_0000").split("_")[1])
            if n > max_n:
                max_n = n
        except (IndexError, ValueError):
            pass
    return f"DOC_{max_n + 1:04d}"


def mettre_a_jour_index(
    index: list[dict],
    ergo_id: str,
    chemin_source: Path,
    chemin_doc: Path,
    sha256: str,
    source_version: str,
) -> tuple[dict, bool]:
    """Met à jour ou crée l'entrée DOC pour un composant dans l'index.

    Si l'entrée existe et que le SHA-256 a changé, incrémente la révision.
    Si l'entrée est nouvelle, l'enregistre avec le prochain DOC_XXXX et révision 1.

    Args:
        index:          Index courant des DOC.
        ergo_id:        ERGO_ID du composant.
        chemin_source:  Chemin vers le fichier .py source.
        chemin_doc:     Chemin vers le fichier .md généré.
        sha256:         SHA-256 tronqué (8 chars) du fichier source.
        source_version: Version extraite de ERGO_REGISTRY.

    Returns:
        Tuple (entree, est_nouvelle) — l'entrée mise à jour et True si elle est nouvelle.
    """
    ts = datetime.now().isoformat()
    for entree in index:
        if entree.get("ergo_id") == ergo_id:
            if entree.get("sha256_source") != sha256:
                entree["doc_revision"]       += 1
                entree["sha256_source"]        = sha256
                entree["source_version"]       = source_version
                entree["derniere_mise_a_jour"] = ts
            return entree, False

    nouvelle_entree = {
        "doc_id":               prochain_doc_id(index),
        "ergo_id":              ergo_id,
        "fichier_source":       chemin_source.name,
        "fichier_doc":          str(chemin_doc.relative_to(BASE_DIR)).replace("\\", "/"),
        "sha256_source":        sha256,
        "source_version":       source_version,
        "doc_revision":         1,
        "premiere_generation":  ts,
        "derniere_mise_a_jour": ts,
    }
    index.append(nouvelle_entree)
    return nouvelle_entree, True


def extraire_ergo_id(contenu: str) -> Optional[str]:
    """Extrait le ERGO_ID depuis le header d'un fichier Python.

    Args:
        contenu: Contenu texte complet du fichier.

    Returns:
        Valeur du ERGO_ID ou None si absent.
    """
    match = ERGO_ID_PATTERN.search(contenu)
    return match.group(1) if match else None


def extraire_registry(contenu: str) -> dict:
    """Parse la section ERGO_REGISTRY de la docstring d'un fichier.

    Args:
        contenu: Contenu texte complet du fichier.

    Returns:
        Dictionnaire des métadonnées ERGO_REGISTRY.
    """
    match = REGISTRY_PATTERN.search(contenu)
    if not match:
        return {}
    resultat: dict = {}
    CHAMPS_LISTE = {"dependances", "entrees", "sorties", "variable_env"}
    for kv in REGISTRY_KV.finditer(match.group(1)):
        cle = kv.group(1).strip()
        val = kv.group(2).strip()
        if cle in CHAMPS_LISTE and "," in val:
            resultat[cle] = [v.strip() for v in val.split(",") if v.strip()]
        else:
            resultat[cle] = val
    return resultat


def extraire_module_description(contenu: str) -> str:
    """Extrait la description principale du module depuis sa docstring.

    Retourne le bloc de texte entre le titre et la section ERGO_REGISTRY.

    Args:
        contenu: Contenu texte complet du fichier.

    Returns:
        Description lisible du module (texte brut).
    """
    match = re.search(r'"""(.*?)"""', contenu, re.DOTALL)
    if not match:
        return ""
    docstring = match.group(1)
    partie = re.split(r"ERGO_REGISTRY:", docstring)[0]
    lignes = partie.strip().split("\n")
    result = []
    for ligne in lignes:
        stripped = ligne.strip()
        if stripped.startswith(("=", "-")) and len(set(stripped)) == 1:
            continue
        result.append(stripped)
    description = "\n".join(result).strip()
    description = re.sub(r"\n{3,}", "\n\n", description)
    return description


def extraire_fonctions(contenu: str, chemin: Path) -> list[dict]:
    """Extrait toutes les fonctions d'un fichier Python via AST.

    Args:
        contenu: Contenu texte complet du fichier Python.
        chemin:  Chemin du fichier (pour les messages d'erreur).

    Returns:
        Liste de dictionnaires décrivant chaque fonction :
            - nom, signature, docstring_titre, docstring_args,
              docstring_returns, docstring_raises, est_privee, ligne
    """
    try:
        arbre = ast.parse(contenu)
    except SyntaxError:
        return []

    fonctions: list[dict] = []
    for noeud in ast.walk(arbre):
        if not isinstance(noeud, ast.FunctionDef):
            continue

        docstring_brut  = ast.get_docstring(noeud) or ""
        titre           = docstring_brut.split("\n")[0].strip() if docstring_brut else ""
        args_section    = _extraire_section_docstring(docstring_brut, "Args")
        returns_section = _extraire_section_docstring(docstring_brut, "Returns")
        raises_section  = _extraire_section_docstring(docstring_brut, "Raises")

        args_sig = []
        for arg in noeud.args.args:
            if arg.arg == "self":
                continue
            annotation = f": {ast.unparse(arg.annotation)}" if arg.annotation else ""
            args_sig.append(f"{arg.arg}{annotation}")

        retour_sig = f" → {ast.unparse(noeud.returns)}" if noeud.returns else ""

        fonctions.append({
            "nom":               noeud.name,
            "signature":         f"{noeud.name}({', '.join(args_sig)}){retour_sig}",
            "docstring_titre":   titre,
            "docstring_args":    args_section,
            "docstring_returns": returns_section,
            "docstring_raises":  raises_section,
            "est_privee":        noeud.name.startswith("_"),
            "ligne":             noeud.lineno,
        })

    return fonctions


def _extraire_section_docstring(docstring: str, section: str) -> str:
    """Extrait une section nommée (Args, Returns, Raises) d'une docstring Google-style.

    Args:
        docstring: Texte complet de la docstring.
        section:   Nom de la section à extraire.

    Returns:
        Contenu de la section ou chaîne vide si absente.
    """
    pattern = re.compile(rf"{section}:\n(.*?)(?=\n\s*\w+:\n|\Z)", re.DOTALL)
    match = pattern.search(docstring)
    return match.group(1).rstrip() if match else ""


def formater_liste_md(items) -> str:
    """Formate une valeur (str ou list) en liste Markdown.

    Args:
        items: Chaîne simple ou liste de chaînes.

    Returns:
        Bloc Markdown avec items sur des lignes séparées ou valeur brute.
    """
    if isinstance(items, list):
        return "\n".join(f"- `{i}`" for i in items if i)
    return f"`{items}`" if items else "—"


def generer_md(chemin: Path, meta_doc: Optional[dict] = None) -> Optional[tuple[str, str]]:
    """Génère le contenu Markdown de documentation pour un fichier Python.

    Args:
        chemin:   Chemin absolu vers le fichier .py à documenter.
        meta_doc: Métadonnées DOC (doc_id, doc_revision, sha256_source) ou None.

    Returns:
        Tuple (ergo_id, contenu_markdown) ou None si le fichier n'a pas d'ERGO_ID.
    """
    contenu  = chemin.read_text(encoding="utf-8")
    ergo_id  = extraire_ergo_id(contenu)
    if not ergo_id:
        return None

    registry    = extraire_registry(contenu)
    description = extraire_module_description(contenu)
    fonctions   = extraire_fonctions(contenu, chemin)
    ts          = datetime.now().strftime("%Y-%m-%d")

    doc_id       = meta_doc.get("doc_id", "DOC_????")  if meta_doc else "DOC_????"
    doc_revision = meta_doc.get("doc_revision", 1)      if meta_doc else 1
    sha256       = meta_doc.get("sha256_source", "????????") if meta_doc else "????????"

    publiques = [f for f in fonctions if not f["est_privee"] and f["nom"] != "main"]
    privees   = [f for f in fonctions if f["est_privee"]]
    main_fn   = next((f for f in fonctions if f["nom"] == "main"), None)

    lignes: list[str] = [
        "---",
        f"ergo_id: {ergo_id}",
        f"doc_id: {doc_id}",
        f"fichier: {chemin.name}",
        f"version: {registry.get('version', '1.0.0')}",
        f"doc_revision: {doc_revision}",
        f"sha256_source: {sha256}",
        f"auteur: {registry.get('auteur', 'ERGO Capital / Adam')}",
        f"derniere_mise_a_jour: {ts}",
        "---",
        "",
        f"# {ergo_id} — `{chemin.name}`",
        "",
        "## Rôle",
        "",
        f"{registry.get('role', '—')}",
        "",
        "---",
        "",
        "## Description",
        "",
        f"{description}",
        "",
        "---",
        "",
        "## Entrées / Sorties",
        "",
        "**Entrées :**",
        "",
        formater_liste_md(registry.get("entrees", "—")),
        "",
        "**Sorties :**",
        "",
        formater_liste_md(registry.get("sorties", "—")),
        "",
    ]

    env_vars = registry.get("variable_env", [])
    if env_vars:
        lignes += [
            "**Variables d'environnement requises :**",
            "",
            formater_liste_md(env_vars),
            "",
        ]

    deps = registry.get("dependances", [])
    if deps:
        lignes += [
            "**Dépendances :**",
            "",
            formater_liste_md(deps),
            "",
        ]

    lignes += ["---", "", "## Fonctions publiques", ""]

    if not publiques and not main_fn:
        lignes.append("*(aucune fonction publique détectée)*")
    else:
        for fn in publiques:
            lignes += [
                f"### `{fn['signature']}`",
                "",
                f"{fn['docstring_titre'] or '—'}",
                "",
            ]
            if fn["docstring_args"].strip():
                lignes += [
                    "**Paramètres :**",
                    "",
                    "```",
                    fn["docstring_args"].rstrip(),
                    "```",
                    "",
                ]
            if fn["docstring_returns"].strip():
                lignes += [
                    "**Retourne :**",
                    "",
                    fn["docstring_returns"].strip(),
                    "",
                ]
            if fn["docstring_raises"].strip():
                lignes += [
                    "**Lève :**",
                    "",
                    fn["docstring_raises"].strip(),
                    "",
                ]
            lignes.append("---")
            lignes.append("")

    if main_fn:
        lignes += [
            "## Point d'entrée — `main()`",
            "",
            f"{main_fn['docstring_titre'] or '—'}",
            "",
            "---",
            "",
        ]

    if privees:
        lignes += [
            "## Fonctions internes",
            "",
            "| Fonction | Rôle |",
            "|---|---|",
        ]
        for fn in privees:
            lignes.append(f"| `{fn['nom']}()` | {fn['docstring_titre'] or '—'} |")
        lignes += ["", "---", ""]

    lignes += [
        "## Traçabilité",
        "",
        "| Champ | Valeur |",
        "|---|---|",
        f"| ERGO_ID | `{ergo_id}` |",
        f"| DOC_ID | `{doc_id}` |",
        f"| Révision doc | `{doc_revision}` |",
        f"| SHA-256 source | `{sha256}` |",
        f"| Fichier source | `{chemin.name}` |",
        f"| Généré le | {ts} |",
        "| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |",
        "",
        "*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*",
        "*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*",
    ]

    return ergo_id, "\n".join(lignes)


def main() -> None:
    """Point d'entrée CLI du générateur de documentation Markdown versionné."""
    parser = argparse.ArgumentParser(
        description="ERGO KOS_COMPTA — Doc Generator : génère la documentation Markdown des composants"
    )
    parser.add_argument("--ergo-id",    type=str, default="", help="Génère uniquement ce composant")
    parser.add_argument("--output-dir", type=str, default="", help="Dossier de sortie (défaut: docs/)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else DOCS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] [DOC_GEN] Generation documentation Markdown")
    print(f"  -> Dossier de sortie : {output_dir.relative_to(BASE_DIR)}\n")

    index   = charger_doc_index(output_dir)
    cibles  = sorted(E0_DIR.glob("*.py"))
    generes = 0
    maj     = 0

    for chemin in cibles:
        contenu_raw = chemin.read_text(encoding="utf-8")
        ergo_id     = extraire_ergo_id(contenu_raw)
        if not ergo_id:
            continue
        if args.ergo_id and ergo_id != args.ergo_id:
            continue

        sha256         = sha256_fichier(chemin)
        registry       = extraire_registry(contenu_raw)
        source_version = registry.get("version", "1.0.0")
        nom_fichier    = output_dir / f"{ergo_id}.md"

        meta_doc, est_nouvelle = mettre_a_jour_index(
            index, ergo_id, chemin, nom_fichier, sha256, source_version
        )

        resultat = generer_md(chemin, meta_doc)
        if resultat is None:
            continue
        _, contenu_md = resultat

        nom_fichier.write_text(contenu_md, encoding="utf-8")

        if est_nouvelle:
            print(f"  + {ergo_id:30} [{meta_doc['doc_id']}] -> docs/{ergo_id}.md  (nouvelle)")
            generes += 1
        else:
            print(f"  ~ {ergo_id:30} [{meta_doc['doc_id']}] -> docs/{ergo_id}.md  (rev {meta_doc['doc_revision']})")
            maj += 1

    sauvegarder_doc_index(output_dir, index)

    print(f"\n  OK {generes} nouveau(x) + {maj} mis a jour")
    print(f"  OK DOC_INDEX.json sauvegarde ({len(index)} entrees)")
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [DOC_GEN] Termine\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
