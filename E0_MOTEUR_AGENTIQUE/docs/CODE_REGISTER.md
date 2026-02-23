---
ergo_id: CODE_REGISTER
doc_id: DOC_0008
fichier: system_code_register.py
version: 1.0.0
doc_revision: 2
sha256_source: f9e3b415
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-23
---

# CODE_REGISTER — `system_code_register.py`

## Rôle

—

---

## Description

system_code_register.py
Greffier CLI — enregistre chaque action de code dans SYSTEM_LOG.json.
Traçabilité complète de l'infrastructure : qui a créé quoi, quand, pourquoi.
Appelable directement en CI/CD sans intervention humaine.

Usage :
python system_code_register.py --fichier agent.py --action CREATED --detail "Pipeline principal"
python system_code_register.py --fichier .gitlab-ci.yml --action UPDATED --detail "Ajout stage audit"
python system_code_register.py --list

---

## Entrées / Sorties

**Entrées :**

`—`

**Sorties :**

`—`

---

## Fonctions publiques

### `lire_log() → list`

—

---

### `ecrire_log(entrees: list)`

—

---

### `ajouter_entree(fichier: str, action: str, detail: str, auteur: str) → dict`

—

---

### `afficher_log(n: int)`

—

---

## Point d'entrée — `main()`

—

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `CODE_REGISTER` |
| DOC_ID | `DOC_0008` |
| Révision doc | `2` |
| SHA-256 source | `f9e3b415` |
| Fichier source | `system_code_register.py` |
| Généré le | 2026-02-23 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*