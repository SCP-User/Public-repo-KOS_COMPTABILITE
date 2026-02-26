# ERGO_ID: CORE_BOOTSTRAP
"""
ergo_core_system.py
Bootstrap script — crée l'environnement virtuel, installe les dépendances,
initialise les dossiers d'infrastructure KOS_COMPTA.
Appelé en stage 'setup' du pipeline GitLab CI/CD.
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

BASE_DIR       = Path(__file__).parent.parent
VENV_DIR       = BASE_DIR / ".venv_compta"
REQUIREMENTS   = BASE_DIR / "requirements.txt"
CHROMA_STORAGE = BASE_DIR / "chroma_db_storage"
SYSTEM_LOG     = BASE_DIR / "E0_MOTEUR_AGENTIQUE" / "logs" / "SYSTEM_LOG.json"

DOSSIERS_REQUIS = [
    BASE_DIR / "E1_CORPUS_LEGAL_ETAT",
    BASE_DIR / "E2_SOP_INTERNE_ET_ERP",
    BASE_DIR / "E3_INTERFACES_ACTEURS" / "E3.1_Dropzone_Factures",
    BASE_DIR / "E3_INTERFACES_ACTEURS" / "E3.2_Requetes_Assistants",
    BASE_DIR / "E4_AUDIT_ET_ROUTAGE" / "E4.1_Rapports_Conformite",
    BASE_DIR / "E4_AUDIT_ET_ROUTAGE" / "E4.2_Payloads_ERP",
    CHROMA_STORAGE,
]

# ─────────────────────────────────────────────
# LOGGER STRUCTURÉ
# ─────────────────────────────────────────────

def log(niveau: str, message: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{niveau}] {message}", flush=True)

def log_system(action: str, statut: str, detail: str = ""):
    """Écrit une entrée dans SYSTEM_LOG.json."""
    entrees = []
    if SYSTEM_LOG.exists():
        try:
            entrees = json.loads(SYSTEM_LOG.read_text())
        except json.JSONDecodeError:
            entrees = []
    entrees.append({
        "timestamp": datetime.now().isoformat(),
        "fichier": "ergo_core_system.py",
        "action": action,
        "statut": statut,
        "detail": detail
    })
    SYSTEM_LOG.write_text(json.dumps(entrees, ensure_ascii=False, indent=2))

# ─────────────────────────────────────────────
# ÉTAPES BOOTSTRAP
# ─────────────────────────────────────────────

def creer_venv():
    log("INFO", f"Création environnement virtuel → {VENV_DIR}")
    if VENV_DIR.exists():
        log("INFO", "Environnement virtuel déjà existant — skip")
        return
    result = subprocess.run(
        [sys.executable, "-m", "venv", str(VENV_DIR)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Échec création venv : {result.stderr}")
    log("OK", "Environnement virtuel créé")


def installer_dependances():
    log("INFO", "Installation des dépendances depuis requirements.txt")
    if not REQUIREMENTS.exists():
        raise FileNotFoundError(f"requirements.txt introuvable : {REQUIREMENTS}")

    pip = VENV_DIR / "bin" / "pip"
    if not pip.exists():
        pip = VENV_DIR / "Scripts" / "pip.exe"  # Windows fallback

    result = subprocess.run(
        [str(pip), "install", "-r", str(REQUIREMENTS), "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Échec installation dépendances : {result.stderr}")
    log("OK", "Dépendances installées")


def initialiser_dossiers():
    log("INFO", "Initialisation de l'arborescence KOS_COMPTA")
    for dossier in DOSSIERS_REQUIS:
        dossier.mkdir(parents=True, exist_ok=True)
        log("OK", f"Dossier vérifié → {dossier.relative_to(BASE_DIR)}")


def verifier_variables_env():
    log("INFO", "Vérification variables d'environnement")
    manquantes = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        manquantes.append("ANTHROPIC_API_KEY")
    if manquantes:
        log("WARN", f"Variables manquantes : {', '.join(manquantes)} — pipeline analyse indisponible")
    else:
        log("OK", "ANTHROPIC_API_KEY présente")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    log("INFO", "=======================================")
    log("INFO", "  ERGO KOS_COMPTA -- Bootstrap START")
    log("INFO", "=======================================")

    try:
        creer_venv()
        log_system("creer_venv", "OK")

        installer_dependances()
        log_system("installer_dependances", "OK")

        initialiser_dossiers()
        log_system("initialiser_dossiers", "OK")

        verifier_variables_env()
        log_system("verifier_variables_env", "OK")

        log("INFO", "=======================================")
        log("INFO", "  Bootstrap SUCCES -- infrastructure prete")
        log("INFO", "=======================================")
        log_system("bootstrap_complet", "SUCCES")
        sys.exit(0)

    except Exception as e:
        log("ERROR", f"Bootstrap ÉCHEC : {e}")
        log_system("bootstrap_complet", "ECHEC", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
