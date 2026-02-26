---
ergo_id: EXPORT_ERP
doc_id: DOC_0011
fichier: export_erp.py
version: 2.0.0
doc_revision: 1
sha256_source: 1042ac12
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-26
---

# EXPORT_ERP — `export_erp.py`

## Rôle

Transformation Payloads JSON conformes en CSV import ERP (CEGID)

---

## Description

export_erp.py
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

---

## Entrées / Sorties

**Entrées :**

`[E4_AUDIT_ET_ROUTAGE/E4.2_Payloads_ERP/*.json]`

**Sorties :**

`[E4_AUDIT_ET_ROUTAGE/E4.3_Imports_ERP/IMPORT_CEGID_*.csv]`

**Variables d'environnement requises :**

`[]`

**Dépendances :**

`[agent_compliance.py]`

---

## Fonctions publiques

### `valider_structure_json(data: dict, chemin_fichier: Path) → dict | None`

Valide la structure du payload JSON et extrait le bloc d'imputation.

**Paramètres :**

```
    data: Dictionnaire JSON parsé du payload.
    chemin_fichier: Chemin du fichier source (utilisé pour les logs).
```

**Retourne :**

Dictionnaire d'imputation si la structure est valide, None sinon.

---

### `verifier_integrite_comptable(montant_ht: float, tva: float, montant_ttc: float, chemin_fichier: Path) → bool`

Contrôle de sécurité : vérifie que HT + TVA ≈ TTC.

**Paramètres :**

```
    montant_ht: Montant hors taxe.
    tva: TVA déductible (peut être 0).
    montant_ttc: Montant toutes taxes comprises.
    chemin_fichier: Chemin du fichier source (utilisé pour les logs).
```

**Retourne :**

True si l'intégrité est vérifiée, False sinon.

---

## Point d'entrée — `main()`

Point d'entrée principal — Version 2.0 Production-Ready.

---

## Fonctions internes

| Fonction | Rôle |
|---|---|
| `_extraire_depuis_ergo_pgi()` | Extrait les données d'imputation depuis le format ergo_pgi_export_v1. |

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `EXPORT_ERP` |
| DOC_ID | `DOC_0011` |
| Révision doc | `1` |
| SHA-256 source | `1042ac12` |
| Fichier source | `export_erp.py` |
| Généré le | 2026-02-26 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*