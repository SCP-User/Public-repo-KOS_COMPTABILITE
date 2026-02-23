---
ergo_id: SHADOW_CLONE
doc_id: DOC_0007
fichier: shadow_clone.py
version: 1.0.0
doc_revision: 1
sha256_source: 99a1fa4d
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-23
---

# SHADOW_CLONE — `shadow_clone.py`

## Rôle

Snapshots immuables et versionnés du code a chaque run CI/CD

---

## Description

shadow_clone.py
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

---

## Entrées / Sorties

**Entrées :**

`fichiers listés dans FICHIERS_CIBLES`

**Sorties :**

`.shadow_clone/SHADOW_INDEX.json`

**Dépendances :**

`(aucune — stdlib uniquement)`

---

## Fonctions publiques

### `sha256_fichier(chemin: Path) → str`

Calcule un SHA-256 tronqué (16 chars) d'un fichier pour détecter les changements.

**Paramètres :**

```
    chemin: Chemin absolu vers le fichier à hasher.
```

**Retourne :**

16 premiers caractères du SHA-256 hexadécimal, ou "ABSENT" si le fichier n'existe pas.

---

### `generer_clone_id() → str`

Génère un identifiant unique pour le clone basé sur l'horodatage.

**Retourne :**

Identifiant au format "SHADOW_YYYYMMDD_HHMMSS_xxxx".

---

### `lire_index() → list[dict]`

Charge l'index global des shadow clones.

**Retourne :**

Liste des entrées d'index, ou liste vide si absent ou corrompu.

---

### `ecrire_index(index: list[dict]) → None`

Écrit l'index global dans SHADOW_INDEX.json.

**Paramètres :**

```
    index: Liste complète des entrées d'index à persister.
```

---

### `creer_clone(label: str, auteur: str, pipeline_id: str) → str`

Crée un snapshot immuable de tous les fichiers cibles.

**Paramètres :**

```
    label:       Label descriptif du clone (ex: "pre-audit A102").
    auteur:      Identité de l'émetteur (ex: "gitlab-ci", "Adam").
    pipeline_id: Identifiant du pipeline CI/CD si disponible.
```

**Retourne :**

Identifiant unique du clone créé (clone_id).

---

### `lister_clones(n: Optional[int]) → None`

Affiche l'index des shadow clones du plus récent au plus ancien.

**Paramètres :**

```
    n: Nombre maximum de clones à afficher. None = tous.
```

---

### `diff_clone(clone_id: str) → None`

Compare un clone avec l'état actuel des fichiers cibles.

**Paramètres :**

```
    clone_id: Identifiant du clone à comparer (format SHADOW_YYYYMMDD_HHMMSS_xxxx).
```

---

### `restaurer_clone(clone_id: str, dry_run: bool) → None`

Restaure l'état des fichiers depuis un clone shadow.

**Paramètres :**

```
    clone_id: Identifiant du clone à restaurer.
    dry_run:  Si True (défaut), simule sans écrire. Si False, écrase les fichiers actuels.
```

---

## Point d'entrée — `main()`

Point d'entrée CLI du système de shadow cloning.

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `SHADOW_CLONE` |
| DOC_ID | `DOC_0007` |
| Révision doc | `1` |
| SHA-256 source | `99a1fa4d` |
| Fichier source | `shadow_clone.py` |
| Généré le | 2026-02-23 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*