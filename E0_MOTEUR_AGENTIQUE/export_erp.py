# ERGO_ID: EXPORT_ERP
"""
export_erp.py
=============
KOS_COMPTA — Pipeline E4 : Payloads JSON → CSV Import CEGID

Maillon final du pipeline KOS_COMPTA. Transforme les verdicts JSON produits
par l'agent de conformité (E4.2) en un fichier CSV normalisé, prêt à être
importé dans un ERP comptable type CEGID.

Pipeline KOS_COMPTA (vue macro) :
    E4.1 Audit (Verdict IA) → E4.2 Payload (JSON struct) → E4.3 Import (CSV → CEGID)
                                                                  ▲
                                                             CE SCRIPT

Architecture des écritures générées :
    Pour chaque facture validée, le script produit jusqu'à 3 lignes :
        1. Ligne HT   (Débit)  → Compte de charge (ex: 62888)
        2. Ligne TVA  (Débit)  → Compte 44566 (TVA déductible sur ABS)
        3. Ligne TTC  (Crédit) → Compte fournisseur (ex: 401)

Garanties v2.0 :
    - Contrôle d'intégrité comptable (partie double vérifiée)
    - Archivage transactionnel (aucune perte de donnée en cas de crash)
    - Validation de structure JSON (batch résilient, pas de crash total)

ERGO_REGISTRY:
    role         : Transformation Payloads JSON conformes en CSV import ERP (CEGID)
    version      : 2.0.0
    auteur       : ERGO Capital / Adam
    dependances  : [agent_compliance.py]
    entrees      : [E4_AUDIT_ET_ROUTAGE/E4.2_Payloads_ERP/*.json]
    sorties      : [E4_AUDIT_ET_ROUTAGE/E4.3_Imports_ERP/IMPORT_CEGID_*.csv]
    variable_env : []
"""

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import json
import csv
import math
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("EXPORT_ERP")

BASE_DIR = Path(__file__).parent.parent
PAYLOADS_DIR = BASE_DIR / "E4_AUDIT_ET_ROUTAGE" / "E4.2_Payloads_ERP"
EXPORT_DIR = BASE_DIR / "E4_AUDIT_ET_ROUTAGE" / "E4.3_Imports_ERP"
ARCHIVE_DIR = PAYLOADS_DIR / "archive"

TOLERANCE_EUROS = 0.01


def _extraire_depuis_ergo_pgi(data: dict, chemin_fichier: Path) -> dict | None:
    """Extrait les données d'imputation depuis le format ergo_pgi_export_v1.

    Format produit par ``agent_compliance.py`` → ``router_verdict()`` :
        ergo_pgi_export_v1.ecriture.lignes[0] = débit HT (compte charge)
        ergo_pgi_export_v1.ecriture.lignes[1] = débit TVA (44566)
        ergo_pgi_export_v1.ecriture.lignes[2] = crédit TTC (fournisseur)

    Args:
        data: Dictionnaire JSON contenant la clé ``ergo_pgi_export_v1``.
        chemin_fichier: Chemin du fichier source (utilisé pour les logs).

    Returns:
        Dictionnaire d'imputation reconstruit, ou None si invalide.
    """
    export_bloc = data["ergo_pgi_export_v1"]
    ecriture = export_bloc.get("ecriture", {})
    lignes = ecriture.get("lignes", [])

    if len(lignes) < 2:
        logger.warning(
            "⚠️  IGNORÉ [%s] : Bloc ergo_pgi_export_v1 avec moins de 2 lignes.",
            chemin_fichier.name
        )
        return None

    ligne_ht = lignes[0]
    ligne_tva = lignes[1] if len(lignes) >= 3 else {"compte": "44566", "debit": 0}
    ligne_ttc = lignes[-1]

    montant_ht = float(ligne_ht.get("debit", 0))
    tva = float(ligne_tva.get("debit", 0))
    montant_ttc = float(ligne_ttc.get("credit", 0))

    compte_debit = str(ligne_ht.get("compte", "62888")).split(" —")[0].split(" –")[0].strip()
    compte_credit = str(ligne_ttc.get("compte", "401")).split(" —")[0].split(" –")[0].strip()

    return {
        "compte_debit": compte_debit,
        "compte_credit": compte_credit,
        "montant_ht": montant_ht,
        "tva_deductible": tva,
        "montant_ttc": montant_ttc,
        "action_erp": export_bloc.get("compliance_status", "A_VALIDER").upper(),
    }


def valider_structure_json(data: dict, chemin_fichier: Path) -> dict | None:
    """Valide la structure du payload JSON et extrait le bloc d'imputation.

    Supporte deux formats d'entrée :
        1. Format verdict brut : ``verdict.imputation_recommandee``
        2. Format ergo_pgi_export_v1 : produit par ``agent_compliance.py``

    Args:
        data: Dictionnaire JSON parsé du payload.
        chemin_fichier: Chemin du fichier source (utilisé pour les logs).

    Returns:
        Dictionnaire d'imputation si la structure est valide, None sinon.
    """
    if "ergo_pgi_export_v1" in data:
        return _extraire_depuis_ergo_pgi(data, chemin_fichier)

    verdict_bloc = data.get("verdict")
    if not isinstance(verdict_bloc, dict):
        logger.warning(
            "⚠️  IGNORÉ [%s] : Clé 'verdict' absente ou invalide.",
            chemin_fichier.name
        )
        return None

    imputation = verdict_bloc.get("imputation_recommandee")
    if not isinstance(imputation, dict) or not imputation:
        logger.warning(
            "⚠️  IGNORÉ [%s] : Clé 'imputation_recommandee' absente ou vide.",
            chemin_fichier.name
        )
        return None

    champs_requis = ["montant_ht", "montant_ttc"]
    for champ in champs_requis:
        if champ not in imputation or imputation[champ] is None:
            logger.warning(
                "⚠️  IGNORÉ [%s] : Champ obligatoire '%s' manquant.",
                chemin_fichier.name, champ
            )
            return None

    return imputation


def verifier_integrite_comptable(
    montant_ht: float,
    tva: float,
    montant_ttc: float,
    chemin_fichier: Path
) -> bool:
    """Contrôle de sécurité : vérifie que HT + TVA ≈ TTC.

    Applique la règle fondamentale de la partie double :
        Somme(Débits) = Somme(Crédits) ⟹ HT + TVA = TTC

    Utilise ``math.isclose()`` avec une tolérance absolue de 0.01€
    pour absorber les erreurs d'arrondi flottant.

    Args:
        montant_ht: Montant hors taxe.
        tva: TVA déductible (peut être 0).
        montant_ttc: Montant toutes taxes comprises.
        chemin_fichier: Chemin du fichier source (utilisé pour les logs).

    Returns:
        True si l'intégrité est vérifiée, False sinon.
    """
    somme_debits = montant_ht + tva
    if not math.isclose(somme_debits, montant_ttc, abs_tol=TOLERANCE_EUROS):
        ecart = abs(somme_debits - montant_ttc)
        logger.error(
            "🚫 REJETÉ [%s] : Intégrité comptable violée ! "
            "HT(%.2f) + TVA(%.2f) = %.2f ≠ TTC(%.2f) — Écart: %.2f€",
            chemin_fichier.name,
            montant_ht, tva, somme_debits, montant_ttc, ecart
        )
        return False
    return True


def main() -> None:
    """Point d'entrée principal — Version 2.0 Production-Ready.

    Orchestre le pipeline complet :
        1. Créer les dossiers de sortie (E4.3, archive) s'ils n'existent pas
        2. Scanner les payloads JSON dans E4.2
        3. Pour chaque JSON : valider structure → vérifier intégrité → générer écritures
        4. Écrire et fermer le fichier CSV
        5. Archiver en bloc les JSONs traités (transactionnel)
        6. Afficher le rapport de synthèse
    """
    print("═" * 60)
    print(" 🏭 KOS_COMPTA v2.0 : GÉNÉRATION DU FICHIER ERP")
    print("═" * 60)

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    fichiers_json = list(PAYLOADS_DIR.glob("*.json"))

    if not fichiers_json:
        logger.info("⚠️ Aucun nouveau payload JSON à exporter vers l'ERP.")
        return

    logger.info("📥 %d payload(s) JSON détecté(s) dans E4.2.", len(fichiers_json))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = EXPORT_DIR / f"IMPORT_CEGID_{timestamp}.csv"

    lignes_exportees: int = 0
    fichiers_rejetes: int = 0
    fichiers_ignores: int = 0
    fichiers_a_archiver: list[Path] = []

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')

        writer.writerow([
            "DATE", "JOURNAL", "COMPTE", "SENS",
            "MONTANT", "LIBELLE", "STATUT_KOS"
        ])

        for path in fichiers_json:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(
                    "🚫 ERREUR [%s] : JSON malformé — %s",
                    path.name, str(e)
                )
                fichiers_rejetes += 1
                continue
            except OSError as e:
                logger.error(
                    "🚫 ERREUR [%s] : Impossible de lire le fichier — %s",
                    path.name, str(e)
                )
                fichiers_rejetes += 1
                continue

            imputation = valider_structure_json(data, path)
            if imputation is None:
                fichiers_ignores += 1
                continue

            verdict_bloc = data.get("verdict", {})
            action_erp = imputation.pop("action_erp", None) or verdict_bloc.get("action_erp", "A_VALIDER")

            montant_ht = float(imputation.get("montant_ht", 0))
            tva = float(imputation.get("tva_deductible", 0))
            montant_ttc = float(imputation.get("montant_ttc", 0))

            if not verifier_integrite_comptable(montant_ht, tva, montant_ttc, path):
                fichiers_rejetes += 1
                continue

            date_jour = datetime.now().strftime("%d/%m/%Y")
            libelle = f"Achat - {path.stem.replace('PAYLOAD_', '')}"

            if montant_ht:
                writer.writerow([
                    date_jour,
                    "ACH",
                    imputation.get("compte_debit", "62888"),
                    "D",
                    f"{montant_ht:.2f}",
                    libelle,
                    action_erp
                ])
                lignes_exportees += 1

            if tva > 0:
                writer.writerow([
                    date_jour,
                    "ACH",
                    "44566",
                    "D",
                    f"{tva:.2f}",
                    libelle,
                    action_erp
                ])
                lignes_exportees += 1

            if montant_ttc:
                writer.writerow([
                    date_jour,
                    "ACH",
                    imputation.get("compte_credit", "401"),
                    "C",
                    f"{montant_ttc:.2f}",
                    libelle,
                    action_erp
                ])
                lignes_exportees += 1

            fichiers_a_archiver.append(path)

    archives_reussies: int = 0
    for path in fichiers_a_archiver:
        try:
            path.rename(ARCHIVE_DIR / path.name)
            archives_reussies += 1
        except OSError as e:
            logger.error(
                "⚠️  ARCHIVAGE ÉCHOUÉ [%s] : %s",
                path.name, str(e)
            )

    print()
    print("═" * 60)
    print(" 📊 RAPPORT D'EXÉCUTION KOS_COMPTA v2.0")
    print("═" * 60)
    print(f"  📥 Payloads détectés   : {len(fichiers_json)}")
    print(f"  ✅ Écritures générées  : {lignes_exportees}")
    print(f"  📦 Fichiers archivés   : {archives_reussies}")
    print(f"  ⚠️  Fichiers ignorés    : {fichiers_ignores}")
    print(f"  🚫 Fichiers rejetés    : {fichiers_rejetes}")
    print(f"  📂 Fichier ERP         : {csv_filename.name}")
    print("═" * 60)

    if fichiers_rejetes > 0:
        logger.warning(
            "⚠️  %d fichier(s) rejeté(s) — consultez les logs ci-dessus.",
            fichiers_rejetes
        )


if __name__ == "__main__":
    main()
