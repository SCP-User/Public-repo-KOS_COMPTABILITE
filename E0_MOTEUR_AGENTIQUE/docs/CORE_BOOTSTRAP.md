---
ergo_id: CORE_BOOTSTRAP
doc_id: DOC_0004
fichier: ergo_core_system.py
version: 1.0.0
doc_revision: 1
sha256_source: 77fb7563
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-23
---

# CORE_BOOTSTRAP — `ergo_core_system.py`

## Rôle

—

---

## Description

ergo_core_system.py
Bootstrap script — crée l'environnement virtuel, installe les dépendances,
initialise les dossiers d'infrastructure KOS_COMPTA.
Appelé en stage 'setup' du pipeline GitLab CI/CD.

---

## Entrées / Sorties

**Entrées :**

`—`

**Sorties :**

`—`

---

## Fonctions publiques

### `log(niveau: str, message: str)`

—

---

### `log_system(action: str, statut: str, detail: str)`

Écrit une entrée dans SYSTEM_LOG.json.

---

### `creer_venv()`

—

---

### `installer_dependances()`

—

---

### `initialiser_dossiers()`

—

---

### `verifier_variables_env()`

—

---

## Point d'entrée — `main()`

—

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `CORE_BOOTSTRAP` |
| DOC_ID | `DOC_0004` |
| Révision doc | `1` |
| SHA-256 source | `77fb7563` |
| Fichier source | `ergo_core_system.py` |
| Généré le | 2026-02-23 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*