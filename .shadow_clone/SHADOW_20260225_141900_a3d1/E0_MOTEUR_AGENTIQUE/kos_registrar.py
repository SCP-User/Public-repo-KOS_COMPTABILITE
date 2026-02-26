# ERGO_ID: KOS_REGISTRAR
"""
kos_registrar.py
================
ERGO KOS_COMPTA — Registre des Composants KOS

Scanne tous les fichiers Python du projet portant un header `# ERGO_ID: XXX`,
extrait les métadonnées de chaque composant depuis leur docstring (section ERGO_REGISTRY),
et génère/met à jour `KOS_ERGO_REGISTRY.json` — le registre central et versionné
de l'infrastructure KOS_COMPTA.

Appelé automatiquement en stage `setup` du pipeline GitLab CI/CD.
Peut aussi être exécuté localement pour inspecter ou documenter le projet.

ERGO_REGISTRY:
    role         : Registre des composants ERGO_ID - scan + generation KOS_ERGO_REGISTRY.json
    version      : 1.0.0
    auteur       : ERGO Capital / Adam
    dependances  : (stdlib uniquement)
    entrees      : tous les fichiers .py avec header # ERGO_ID:
    sorties      : E0_MOTEUR_AGENTIQUE/registry/KOS_ERGO_REGISTRY.json

Usage :
    python kos_registrar.py                         # scan + mise à jour registre
    python kos_registrar.py --list                  # affiche le registre en console
    python kos_registrar.py --ergo-id COMPLIANCE_AGENT  # détail d'un composant
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime


BASE_DIR   = Path(__file__).parent.parent
E0_DIR     = Path(__file__).parent
REGISTRY   = E0_DIR / "registry" / "KOS_ERGO_REGISTRY.json"

ERGO_ID_PATTERN    = re.compile(r"^#\s*ERGO_ID:\s*(\w+)", re.MULTILINE)
REGISTRY_PATTERN   = re.compile(r"ERGO_REGISTRY:(.*?)(?:\n\n|\Z)", re.DOTALL)
REGISTRY_KV        = re.compile(r"^\s+(\w+)\s*:\s*(.+)$", re.MULTILINE)


def extraire_ergo_id(contenu: str) -> str | None:
    """Extrait le ERGO_ID depuis la première ligne d'un fichier Python.

    Args:
        contenu: Contenu texte complet du fichier.

    Returns:
        Valeur de l'ERGO_ID (str) ou None si absent.
    """
    match = ERGO_ID_PATTERN.search(contenu)
    return match.group(1) if match else None


def extraire_registry_section(contenu: str) -> dict:
    """Extrait et parse la section ERGO_REGISTRY: de la docstring d'un fichier.

    La section ERGO_REGISTRY suit le format :
        ERGO_REGISTRY:
            cle1 : valeur1
            cle2 : valeur2

    Args:
        contenu: Contenu texte complet du fichier.

    Returns:
        Dictionnaire des clés/valeurs extraites de la section ERGO_REGISTRY.
    """
    match = REGISTRY_PATTERN.search(contenu)
    if not match:
        return {}
    section = match.group(1)
    resultat: dict = {}
    for kv in REGISTRY_KV.finditer(section):
        cle = kv.group(1).strip()
        val = kv.group(2).strip()
        CHAMPS_LISTE = {"dependances", "entrees", "sorties", "variable_env", "applicable_a"}
        if val.startswith("[") and val.endswith("]"):
            resultat[cle] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
        elif cle in CHAMPS_LISTE and "," in val:
            resultat[cle] = [v.strip() for v in val.split(",") if v.strip()]
        else:
            resultat[cle] = val
    return resultat


def scanner_composants(racines: list[Path]) -> list[dict]:
    """Scanne les dossiers fournis pour trouver tous les fichiers Python avec ERGO_ID.

    Args:
        racines: Liste de dossiers à scanner récursivement.

    Returns:
        Liste de dictionnaires décrivant chaque composant trouvé.
    """
    composants: list[dict] = []
    for racine in racines:
        for chemin in sorted(racine.rglob("*.py")):
            contenu  = chemin.read_text(encoding="utf-8")
            ergo_id  = extraire_ergo_id(contenu)
            if not ergo_id:
                continue
            meta     = extraire_registry_section(contenu)
            relatif  = str(chemin.relative_to(BASE_DIR)).replace("\\", "/")
            composant = {
                "ergo_id":     ergo_id,
                "fichier":     relatif,
                "role":        meta.get("role", meta.get("description", "Non renseigné")),
                "version":     meta.get("version", "1.0.0"),
                "auteur":      meta.get("auteur", "ERGO Capital / Adam"),
                "dependances": meta.get("dependances", []),
                "entrees":     meta.get("entrees", []),
                "sorties":     meta.get("sorties", []),
                "variable_env": meta.get("variable_env", []),
                "derniere_scan": datetime.now().isoformat(),
            }
            composants.append(composant)
            print(f"  ✓ {ergo_id:30} → {relatif}")
    return composants


def lire_registre() -> dict:
    """Charge le registre existant depuis KOS_ERGO_REGISTRY.json.

    Returns:
        Dictionnaire complet du registre, ou structure vide si absent.
    """
    if not REGISTRY.exists():
        return {"_meta": {}, "composants": []}
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_meta": {}, "composants": []}


def fusionner_composants(existants: list[dict], nouveaux: list[dict]) -> list[dict]:
    """Fusionne les composants existants avec les nouveaux en préservant l'historique.

    Les champs `enregistre_le` et `statut` des composants existants sont conservés.
    Les nouveaux composants non encore référencés sont ajoutés avec `statut: ACTIVE`.

    Args:
        existants: Liste des composants déjà dans le registre.
        nouveaux:  Liste produite par scanner_composants().

    Returns:
        Liste fusionnée et dédupliquée par ergo_id.
    """
    index_existants = {c["ergo_id"]: c for c in existants}
    fusionnes: list[dict] = []

    for nouveau in nouveaux:
        ergo_id = nouveau["ergo_id"]
        if ergo_id in index_existants:
            ancien = index_existants[ergo_id]
            nouveau["enregistre_le"]    = ancien.get("enregistre_le", nouveau["derniere_scan"])
            nouveau["statut"]           = ancien.get("statut", "ACTIVE")
            nouveau["nb_deployments"]   = ancien.get("nb_deployments", 0) + 1
        else:
            nouveau["enregistre_le"]  = nouveau["derniere_scan"]
            nouveau["statut"]         = "ACTIVE"
            nouveau["nb_deployments"] = 1
        fusionnes.append(nouveau)

    return fusionnes


def ecrire_registre(composants: list[dict]) -> None:
    """Sérialise et écrit le registre complet dans KOS_ERGO_REGISTRY.json.

    Args:
        composants: Liste fusionnée des composants à persister.
    """
    registre = {
        "_meta": {
            "schema":        "KOS_ERGO_REGISTRY_v1",
            "generated_by":  "kos_registrar.py",
            "last_updated":  datetime.now().isoformat(),
            "project":       "KOS_COMPTA",
            "nb_composants": len(composants),
        },
        "composants": composants,
    }
    REGISTRY.write_text(json.dumps(registre, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  ✓ Registre mis à jour → {REGISTRY.name} ({len(composants)} composant(s))")


def afficher_registre(registre: dict, ergo_id: str | None = None) -> None:
    """Affiche le registre ou un composant spécifique en console.

    Args:
        registre: Dictionnaire complet du registre.
        ergo_id:  Si fourni, affiche uniquement le composant correspondant.
    """
    composants = registre.get("composants", [])
    meta       = registre.get("_meta", {})

    if ergo_id:
        cible = next((c for c in composants if c["ergo_id"] == ergo_id), None)
        if not cible:
            print(f"  [REGISTRE] ERGO_ID '{ergo_id}' introuvable.", file=sys.stderr)
            return
        composants = [cible]

    print(f"\n{'─'*64}")
    print(f"  KOS_ERGO_REGISTRY — {len(composants)} composant(s)")
    if meta:
        print(f"  Dernière mise à jour : {meta.get('last_updated', '?')[:19]}")
    print(f"{'─'*64}\n")

    for c in composants:
        statut    = c.get("statut", "?")
        deployments = c.get("nb_deployments", 0)
        print(f"  [{c['ergo_id']}]  v{c.get('version', '?')}  statut={statut}  deployments={deployments}")
        print(f"  Fichier  : {c['fichier']}")
        print(f"  Rôle     : {c.get('role', '—')}")
        dep = c.get("dependances", [])
        env = c.get("variable_env", [])
        if dep:
            dep_str = ", ".join(dep) if isinstance(dep, list) else dep
            print(f"  Dépend.  : {dep_str}")
        if env:
            env_str = ", ".join(env) if isinstance(env, list) else env
            print(f"  Env vars : {env_str}")
        print()


def main() -> None:
    """Point d'entrée CLI du registre KOS."""
    parser = argparse.ArgumentParser(
        description="ERGO KOS_COMPTA — KOS Registrar : registre des composants ERGO_ID"
    )
    parser.add_argument("--list",     action="store_true", help="Affiche le registre courant")
    parser.add_argument("--ergo-id",  type=str, default="", help="Affiche un composant spécifique")
    parser.add_argument("--scan-dir", type=str, default="", help="Dossier supplémentaire à scanner")
    args = parser.parse_args()

    racines = [E0_DIR]
    if args.scan_dir:
        racines.append(Path(args.scan_dir))

    if args.list or args.ergo_id:
        registre = lire_registre()
        afficher_registre(registre, args.ergo_id or None)
        sys.exit(0)

    print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] [REGISTRAR] Scan des composants KOS")

    nouveaux   = scanner_composants(racines)
    existant   = lire_registre()
    fusionnes  = fusionner_composants(existant.get("composants", []), nouveaux)
    ecrire_registre(fusionnes)

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [REGISTRAR] Terminé\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
