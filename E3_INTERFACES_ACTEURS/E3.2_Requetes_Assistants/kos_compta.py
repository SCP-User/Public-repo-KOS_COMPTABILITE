"""
╔══════════════════════════════════════════════════════════════╗
║  KOS_COMPTA : Générateur d'Écritures Comptables pour ERP   ║
║  Pipeline E4 : Payloads JSON → CSV Import CEGID             ║
║  Version : 2.0.0 — Production-Ready                         ║
╚══════════════════════════════════════════════════════════════╝

CONTEXTE :
    Ce script est le maillon final du pipeline KOS_COMPTA.
    Il transforme les verdicts JSON produits par l'agent de conformité
    (étape E4.2) en un fichier CSV normalisé, prêt à être importé
    dans un ERP comptable type CEGID.

PIPELINE KOS_COMPTA (vue macro) :
    ┌─────────────┐     ┌──────────────┐     ┌────────────────┐
    │ E4.1 Audit  │ ──► │ E4.2 Payload │ ──► │ E4.3 Import    │
    │ (Verdict IA)│     │ (JSON struct)│     │ (CSV → CEGID)  │
    └─────────────┘     └──────────────┘     └────────────────┘
                                                   ▲
                                              CE SCRIPT

ARCHITECTURE DES ÉCRITURES GÉNÉRÉES :
    Pour chaque facture validée, le script produit jusqu'à 3 lignes :

    1. Ligne HT   (Débit)  → Compte de charge (ex: 62888)
    2. Ligne TVA  (Débit)  → Compte 44566 (TVA déductible sur ABS)
    3. Ligne TTC  (Crédit) → Compte fournisseur (ex: 401)

    Contrôle de sécurité : HT + TVA ≈ TTC (math.isclose)

GARANTIES v2.0 :
    ✅ Contrôle d'intégrité comptable (partie double vérifiée)
    ✅ Archivage transactionnel (aucune perte de donnée en cas de crash)
    ✅ Validation de structure JSON (batch résilient, pas de crash total)

FICHIERS MANIPULÉS :
    Entrée  : E4_AUDIT_ET_ROUTAGE/E4.2_Payloads_ERP/*.json
    Sortie  : E4_AUDIT_ET_ROUTAGE/E4.3_Imports_ERP/IMPORT_CEGID_<timestamp>.csv
    Archive : E4_AUDIT_ET_ROUTAGE/E4.2_Payloads_ERP/archive/  (JSONs traités)

STATUT  : Production-Ready (E2.1.1_SCRIPTS_TESTS)
VERSION : 2.0.0
AUTEUR  : KOS_COMPTA / ERGO
"""

import json
import csv
import math
import logging
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# SECTION 0 : CONFIGURATION DU LOGGER
# ═══════════════════════════════════════════════════════════
# On utilise le module logging natif Python plutôt que de
# simples print() pour permettre la redirection vers fichier,
# le filtrage par sévérité, et l'intégration future avec
# registrar.py (le Greffier KOS).

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("KOS_COMPTA")


# ═══════════════════════════════════════════════════════════
# SECTION 1 : CHEMINS DU SYSTÈME DE FICHIERS KOS
# ═══════════════════════════════════════════════════════════
# Résolution dynamique des chemins via Path(__file__).parent.parent
# pour rester agnostique à l'emplacement d'installation.
#
# Arborescence attendue :
#   KOS ERGO/
#   ├── E4_AUDIT_ET_ROUTAGE/
#   │   ├── E4.2_Payloads_ERP/       ← JSONs verdicts (entrée)
#   │   │   └── archive/             ← JSONs déjà exportés
#   │   └── E4.3_Imports_ERP/        ← CSVs générés (sortie)
#   └── E2_INGÉNIERIE & DATA/
#       └── E2.1_GENIE_LOGICIEL/
#           └── E2.1.1_SCRIPTS_TESTS/
#               └── kos_compta/       ← CE SCRIPT

BASE_DIR = Path(__file__).parent.parent
PAYLOADS_DIR = BASE_DIR / "E4_AUDIT_ET_ROUTAGE" / "E4.2_Payloads_ERP"
EXPORT_DIR = BASE_DIR / "E4_AUDIT_ET_ROUTAGE" / "E4.3_Imports_ERP"
ARCHIVE_DIR = PAYLOADS_DIR / "archive"

# ═══════════════════════════════════════════════════════════
# SECTION 2 : TOLÉRANCE POUR LE CONTRÔLE D'INTÉGRITÉ
# ═══════════════════════════════════════════════════════════
# Tolérance en euros pour la vérification de la partie double.
# On utilise une tolérance absolue de 0.01€ (1 centime) pour
# absorber les erreurs d'arrondi flottant classiques.
# Ex: 100.00 + 20.00 devrait donner 120.00, mais en float
#     on peut obtenir 119.99999999999999 — d'où la tolérance.

TOLERANCE_EUROS = 0.01


def valider_structure_json(data: dict, chemin_fichier: Path) -> dict | None:
    """
    Valide la structure du payload JSON et extrait le bloc d'imputation.

    Vérifie :
        1. Présence de la clé "verdict"
        2. Présence de la clé "imputation_recommandee" dans le verdict
        3. Présence des champs obligatoires (montant_ht, montant_ttc)

    Args:
        data: Le dictionnaire JSON parsé.
        chemin_fichier: Le Path du fichier source (pour les logs).

    Returns:
        Le dictionnaire d'imputation si valide, None sinon.
    """
    # ── Vérification niveau 1 : bloc verdict ──
    verdict_bloc = data.get("verdict")
    if not isinstance(verdict_bloc, dict):
        logger.warning(
            "⚠️  IGNORÉ [%s] : Clé 'verdict' absente ou invalide.",
            chemin_fichier.name
        )
        return None

    # ── Vérification niveau 2 : bloc imputation ──
    imputation = verdict_bloc.get("imputation_recommandee")
    if not isinstance(imputation, dict) or not imputation:
        logger.warning(
            "⚠️  IGNORÉ [%s] : Clé 'imputation_recommandee' absente ou vide.",
            chemin_fichier.name
        )
        return None

    # ── Vérification niveau 3 : champs obligatoires ──
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
    """
    Contrôle de sécurité : vérifie que HT + TVA ≈ TTC.

    Utilise math.isclose() avec une tolérance absolue de 0.01€
    pour absorber les erreurs d'arrondi flottant.

    Règle comptable fondamentale de la partie double :
        Somme(Débits) = Somme(Crédits)
        ⟹ HT + TVA = TTC

    Args:
        montant_ht: Montant hors taxe.
        tva: TVA déductible (peut être 0).
        montant_ttc: Montant toutes taxes comprises.
        chemin_fichier: Le Path du fichier source (pour les logs).

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


def main():
    """
    Point d'entrée principal — Version 2.0 Production-Ready.
    Orchestre le pipeline : Scan JSON → Validation → Génération CSV → Archivage.

    Flow :
        1. Créer les dossiers de sortie s'ils n'existent pas
        2. Scanner les payloads JSON dans E4.2
        3. Pour chaque JSON :
           a. Valider la structure (try/except + validation logique)
           b. Vérifier l'intégrité comptable HT + TVA ≈ TTC
           c. Générer les écritures comptables (HT/TVA/TTC)
        4. Écrire et fermer le fichier CSV
        5. Archiver en bloc les JSONs traités (transactionnel)
        6. Afficher le rapport de synthèse
    """
    print("═" * 60)
    print(" 🏭 KOS_COMPTA v2.0 : GÉNÉRATION DU FICHIER ERP")
    print("═" * 60)

    # ── Étape 1 : Initialisation des répertoires ──
    # mkdir(parents=True) crée toute la chaîne de dossiers si nécessaire
    # exist_ok=True évite l'erreur si le dossier existe déjà
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # ── Étape 2 : Découverte des payloads à traiter ──
    # On ne prend que les .json à la racine de E4.2 (pas dans /archive)
    fichiers_json = list(PAYLOADS_DIR.glob("*.json"))

    if not fichiers_json:
        logger.info("⚠️ Aucun nouveau payload JSON à exporter vers l'ERP.")
        return

    logger.info("📥 %d payload(s) JSON détecté(s) dans E4.2.", len(fichiers_json))

    # ── Étape 3 : Création du fichier CSV d'export ──
    # Le timestamp garantit l'unicité du fichier et la traçabilité temporelle
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = EXPORT_DIR / f"IMPORT_CEGID_{timestamp}.csv"

    # ═══════════════════════════════════════════════════════
    # COMPTEURS DE SYNTHÈSE
    # ═══════════════════════════════════════════════════════
    lignes_exportees = 0
    fichiers_rejetes = 0
    fichiers_ignores = 0

    # ═══════════════════════════════════════════════════════
    # LISTE D'ARCHIVAGE TRANSACTIONNEL
    # ═══════════════════════════════════════════════════════
    # On NE déplace PAS les fichiers pendant la boucle de lecture.
    # On stocke les chemins des fichiers traités avec succès,
    # et on les archive EN BLOC à la fin, après fermeture du CSV.
    # Garantie : si le script plante mid-loop, aucun JSON n'est
    # déplacé → on peut relancer sans perte de données.
    fichiers_a_archiver: list[Path] = []

    # ── Étape 4 : Génération des écritures comptables ──
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')

        # En-tête CSV normalisé pour import ERP
        # DATE      : Date de l'écriture (JJ/MM/AAAA)
        # JOURNAL   : Code journal comptable (ACH = Achats)
        # COMPTE    : Numéro de compte PCG
        # SENS      : D = Débit, C = Crédit
        # MONTANT   : Montant en euros
        # LIBELLE   : Description de l'opération
        # STATUT_KOS: Verdict de l'agent IA (CONFORME / A_VALIDER / REJET)
        writer.writerow([
            "DATE", "JOURNAL", "COMPTE", "SENS",
            "MONTANT", "LIBELLE", "STATUT_KOS"
        ])

        for path in fichiers_json:
            # ─────────────────────────────────────────────
            # GARDE 1 : Validation de lecture JSON
            # ─────────────────────────────────────────────
            # try/except empêche un JSON malformé de faire
            # crasher le batch entier. On log et on continue.
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

            # ─────────────────────────────────────────────
            # GARDE 2 : Validation de structure JSON
            # ─────────────────────────────────────────────
            # Vérifie la présence et la validité des clés
            # obligatoires (verdict, imputation, montants).
            imputation = valider_structure_json(data, path)
            if imputation is None:
                fichiers_ignores += 1
                continue

            # Extraction des données validées
            verdict_bloc = data["verdict"]
            action_erp = verdict_bloc.get("action_erp", "A_VALIDER")

            montant_ht = float(imputation.get("montant_ht", 0))
            tva = float(imputation.get("tva_deductible", 0))
            montant_ttc = float(imputation.get("montant_ttc", 0))

            # ─────────────────────────────────────────────
            # GARDE 3 : Contrôle d'intégrité comptable
            # ─────────────────────────────────────────────
            # Vérifie la règle fondamentale de la partie double :
            #   Σ Débits = Σ Crédits  ⟹  HT + TVA ≈ TTC
            # Si cette règle est violée, la facture est
            # mathématiquement fausse → on ne l'écrit PAS.
            if not verifier_integrite_comptable(montant_ht, tva, montant_ttc, path):
                fichiers_rejetes += 1
                continue

            # ═══════════════════════════════════════════════
            # GÉNÉRATION DES ÉCRITURES (3 gardes passées ✓)
            # ═══════════════════════════════════════════════

            date_jour = datetime.now().strftime("%d/%m/%Y")
            libelle = f"Achat - {path.stem.replace('PAYLOAD_', '')}"

            # ── Écriture 1 : Ligne HT (Débit charge) ──
            # Débite le compte de charge du montant HT
            # Valeur par défaut 62888 si aucun compte spécifié par l'IA
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

            # ── Écriture 2 : Ligne TVA déductible (Débit) ──
            # Compte 44566 = TVA déductible sur autres biens et services
            # N'écrit la ligne QUE si TVA > 0 (principe de non-écriture à zéro)
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

            # ── Écriture 3 : Ligne TTC (Crédit fournisseur) ──
            # Crédite le fournisseur du montant TTC
            # Valeur par défaut 401 (Fournisseurs) si non spécifié
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

            # ── Marquer pour archivage (PAS de rename ici !) ──
            fichiers_a_archiver.append(path)

    # ═══════════════════════════════════════════════════════
    # ÉTAPE 5 : ARCHIVAGE TRANSACTIONNEL
    # ═══════════════════════════════════════════════════════
    # Le CSV est maintenant fermé (context manager `with` terminé).
    # On peut archiver les JSONs en toute sécurité : si le script
    # avait planté pendant l'écriture CSV, les JSONs seraient
    # restés en place pour une nouvelle tentative.

    archives_reussies = 0
    for path in fichiers_a_archiver:
        try:
            path.rename(ARCHIVE_DIR / path.name)
            archives_reussies += 1
        except OSError as e:
            logger.error(
                "⚠️  ARCHIVAGE ÉCHOUÉ [%s] : %s",
                path.name, str(e)
            )

    # ═══════════════════════════════════════════════════════
    # ÉTAPE 6 : RAPPORT DE SYNTHÈSE
    # ═══════════════════════════════════════════════════════
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
