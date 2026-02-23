# ERGO_ID: SHADOW_CLONE
"""
shadow_clone.py
===============
ERGO KOS_COMPTA — Système de Shadow Cloning

Crée des snapshots immuables et versionnés de l'état du code à chaque run CI/CD.
Permet de rejouer n'importe quelle version du pipeline, de tracer l'évolution du code
de manière indépendante de Git, et de détecter toute dérive entre versions.

Structure produite :
    .shadow_clone/
    ├── SHADOW_INDEX.json            ← index global de tous les clones
    └── SHADOW_YYYYMMDD_HHMMSS_xxxx/
        ├── CLONE_MANIFEST.json      ← métadonnées + SHA-256 de chaque fichier
        └── E0_MOTEUR_AGENTIQUE/
            ├── agent_compliance.py
            └── ...

ERGO_REGISTRY:
    role         : Snapshots immuables et versionnés du code a chaque run CI/CD
    version      : 1.0.0
    auteur       : ERGO Capital / Adam
    dependances  : (aucune — stdlib uniquement)
    entrees      : fichiers listés dans FICHIERS_CIBLES
    sorties      : .shadow_clone/SHADOW_INDEX.json
                   .shadow_clone/<clone_id>/CLONE_MANIFEST.json
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


BASE_DIR     = Path(__file__).parent.parent
SHADOW_DIR   = BASE_DIR / ".shadow_clone"
SHADOW_INDEX = SHADOW_DIR / "SHADOW_INDEX.json"

FICHIERS_CIBLES: list[str] = [
    "E0_MOTEUR_AGENTIQUE/agent_compliance.py",
    "E0_MOTEUR_AGENTIQUE/detect_document_type.py",
    "E0_MOTEUR_AGENTIQUE/publish_report.py",
    "E0_MOTEUR_AGENTIQUE/shadow_clone.py",
    "E0_MOTEUR_AGENTIQUE/ergo_core_system.py",
    "E0_MOTEUR_AGENTIQUE/system_code_register.py",
    "E0_MOTEUR_AGENTIQUE/kos_registrar.py",
    "E0_MOTEUR_AGENTIQUE/KOS_COMPTA_Taxonomie.json",
    "E0_MOTEUR_AGENTIQUE/KOS_COMPTA_Agentique.json",
    ".gitlab-ci.yml",
    "requirements.txt",
]


def sha256_fichier(chemin: Path) -> str:
    """Calcule un SHA-256 tronqué (16 chars) d'un fichier pour détecter les changements.

    Args:
        chemin: Chemin absolu vers le fichier à hasher.

    Returns:
        16 premiers caractères du SHA-256 hexadécimal, ou "ABSENT" si le fichier n'existe pas.
    """
    if not chemin.exists():
        return "ABSENT"
    h = hashlib.sha256()
    h.update(chemin.read_bytes())
    return h.hexdigest()[:16]


def generer_clone_id() -> str:
    """Génère un identifiant unique pour le clone basé sur l'horodatage.

    Returns:
        Identifiant au format "SHADOW_YYYYMMDD_HHMMSS_xxxx".
    """
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    token = hashlib.sha256(ts.encode()).hexdigest()[:4]
    return f"SHADOW_{ts}_{token}"


def lire_index() -> list[dict]:
    """Charge l'index global des shadow clones.

    Returns:
        Liste des entrées d'index, ou liste vide si absent ou corrompu.
    """
    if not SHADOW_INDEX.exists():
        return []
    try:
        return json.loads(SHADOW_INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def ecrire_index(index: list[dict]) -> None:
    """Écrit l'index global dans SHADOW_INDEX.json.

    Args:
        index: Liste complète des entrées d'index à persister.
    """
    SHADOW_DIR.mkdir(parents=True, exist_ok=True)
    SHADOW_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def creer_clone(label: str = "", auteur: str = "CI/CD", pipeline_id: str = "") -> str:
    """Crée un snapshot immuable de tous les fichiers cibles.

    Args:
        label:       Label descriptif du clone (ex: "pre-audit A102").
        auteur:      Identité de l'émetteur (ex: "gitlab-ci", "Adam").
        pipeline_id: Identifiant du pipeline CI/CD si disponible.

    Returns:
        Identifiant unique du clone créé (clone_id).
    """
    clone_id  = generer_clone_id()
    clone_dir = SHADOW_DIR / clone_id
    clone_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    manifest: dict = {
        "clone_id":    clone_id,
        "timestamp":   timestamp,
        "label":       label,
        "auteur":      auteur,
        "pipeline_id": pipeline_id,
        "fichiers":    {},
    }

    print(f"  [SHADOW] Création clone → {clone_id}")

    for relatif in FICHIERS_CIBLES:
        source = BASE_DIR / relatif
        dest   = clone_dir / relatif
        if source.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            sha    = sha256_fichier(source)
            taille = source.stat().st_size
            manifest["fichiers"][relatif] = {"statut": "CLONE", "sha256": sha, "taille_bytes": taille}
            print(f"    ✓ {relatif} [{sha}]")
        else:
            manifest["fichiers"][relatif] = {"statut": "ABSENT", "sha256": "ABSENT", "taille_bytes": 0}
            print(f"    ⚠ {relatif} [ABSENT]")

    nb_clones = sum(1 for m in manifest["fichiers"].values() if m["statut"] == "CLONE")
    (clone_dir / "CLONE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    index = lire_index()
    index.append({
        "clone_id":    clone_id,
        "timestamp":   timestamp,
        "label":       label,
        "auteur":      auteur,
        "pipeline_id": pipeline_id,
        "nb_fichiers": nb_clones,
    })
    ecrire_index(index)

    print(f"  [SHADOW] Clone créé : {clone_id} ({nb_clones} fichiers)\n")
    return clone_id


def lister_clones(n: Optional[int] = None) -> None:
    """Affiche l'index des shadow clones du plus récent au plus ancien.

    Args:
        n: Nombre maximum de clones à afficher. None = tous.
    """
    index = lire_index()
    if not index:
        print("  [SHADOW] Aucun clone trouvé.")
        return

    affichage = index[-n:] if n else index
    print(f"\n{'─'*64}")
    print(f"  SHADOW INDEX — {len(index)} clone(s) total")
    print(f"{'─'*64}")
    for entry in reversed(affichage):
        label    = f" — {entry['label']}"       if entry.get("label")       else ""
        pipeline = f" [pipeline={entry['pipeline_id']}]" if entry.get("pipeline_id") else ""
        print(f"  {entry['clone_id']}{label}{pipeline}")
        print(f"    {entry['timestamp'][:19]} · {entry.get('nb_fichiers', '?')} fichier(s) · {entry.get('auteur', '?')}")
        print()


def diff_clone(clone_id: str) -> None:
    """Compare un clone avec l'état actuel des fichiers cibles.

    Args:
        clone_id: Identifiant du clone à comparer (format SHADOW_YYYYMMDD_HHMMSS_xxxx).
    """
    manifest_path = SHADOW_DIR / clone_id / "CLONE_MANIFEST.json"
    if not manifest_path.exists():
        print(f"  [SHADOW] Clone introuvable : {clone_id}", file=sys.stderr)
        sys.exit(1)

    manifest    = json.loads(manifest_path.read_text(encoding="utf-8"))
    changements = 0

    print(f"\n{'─'*64}")
    print(f"  DIFF — {clone_id} vs état actuel")
    print(f"  Clone créé : {manifest['timestamp'][:19]}")
    print(f"{'─'*64}\n")

    for relatif, info in manifest["fichiers"].items():
        sha_clone  = info.get("sha256", "ABSENT")
        sha_actuel = sha256_fichier(BASE_DIR / relatif)

        if sha_clone == sha_actuel:
            print(f"  ✓ IDENTIQUE  {relatif}")
        elif sha_actuel == "ABSENT":
            print(f"  ✗ SUPPRIMÉ   {relatif} (était {sha_clone})")
            changements += 1
        elif sha_clone == "ABSENT":
            print(f"  + AJOUTÉ     {relatif} (maintenant {sha_actuel})")
            changements += 1
        else:
            print(f"  ≠ MODIFIÉ    {relatif}  clone={sha_clone} → actuel={sha_actuel}")
            changements += 1

    print(f"\n  → {changements} fichier(s) modifié(s) depuis ce clone\n")


def restaurer_clone(clone_id: str, dry_run: bool = True) -> None:
    """Restaure l'état des fichiers depuis un clone shadow.

    Args:
        clone_id: Identifiant du clone à restaurer.
        dry_run:  Si True (défaut), simule sans écrire. Si False, écrase les fichiers actuels.
    """
    manifest_path = SHADOW_DIR / clone_id / "CLONE_MANIFEST.json"
    if not manifest_path.exists():
        print(f"  [SHADOW] Clone introuvable : {clone_id}", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mode     = "DRY-RUN" if dry_run else "RESTAURATION RÉELLE"

    print(f"\n  [SHADOW] {mode} — {clone_id}")
    print(f"  Clone du : {manifest['timestamp'][:19]}\n")

    for relatif, info in manifest["fichiers"].items():
        source = SHADOW_DIR / clone_id / relatif
        dest   = BASE_DIR / relatif

        if info["statut"] != "CLONE":
            print(f"  ⚠ IGNORÉ (absent dans clone) : {relatif}")
            continue

        if dry_run:
            print(f"  → RESTAURERAIT : {relatif}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            print(f"  ✓ RESTAURÉ : {relatif}")

    if dry_run:
        print(f"\n  → Utilisez --no-dry-run pour la restauration réelle.\n")
    else:
        print(f"\n  ✓ Restauration terminée.\n")


def main() -> None:
    """Point d'entrée CLI du système de shadow cloning."""
    parser = argparse.ArgumentParser(
        description="ERGO KOS_COMPTA — Shadow Clone System : snapshots immuables du code"
    )
    parser.add_argument("--action",      choices=["create", "list", "diff", "restore"], required=True)
    parser.add_argument("--label",       type=str,  default="")
    parser.add_argument("--auteur",      type=str,  default="CI/CD")
    parser.add_argument("--pipeline-id", type=str,  default=os.environ.get("CI_PIPELINE_ID", ""))
    parser.add_argument("--clone-id",    type=str,  default="")
    parser.add_argument("--last",        type=int,  default=10)
    parser.add_argument("--no-dry-run",  action="store_true")
    args = parser.parse_args()

    if args.action == "create":
        clone_id = creer_clone(label=args.label, auteur=args.auteur, pipeline_id=args.pipeline_id)
        print(f"SHADOW_CLONE_ID={clone_id}")
    elif args.action == "list":
        lister_clones(args.last)
    elif args.action == "diff":
        if not args.clone_id:
            parser.error("--clone-id requis pour diff")
        diff_clone(args.clone_id)
    elif args.action == "restore":
        if not args.clone_id:
            parser.error("--clone-id requis pour restore")
        restaurer_clone(args.clone_id, dry_run=not args.no_dry_run)

    sys.exit(0)


if __name__ == "__main__":
    main()
