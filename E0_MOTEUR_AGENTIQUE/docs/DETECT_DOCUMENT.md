---
ergo_id: DETECT_DOCUMENT
doc_id: DOC_0002
fichier: detect_document_type.py
version: 1.0.0
doc_revision: 1
sha256_source: cf510afe
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-25
---

# DETECT_DOCUMENT — `detect_document_type.py`

## Rôle

Stage DETECT - identifie le type de document entrant dans E3.1

---

## Description

detect_document_type.py
ERGO KOS_COMPTA — Stage DETECT

Identifie le type de chaque document déposé dans E3.1_Dropzone_Factures
en lisant le frontmatter YAML, puis produit un fichier dotenv pour transmettre
les variables au stage suivant via GitLab CI/CD artifacts:reports:dotenv.

---

## Entrées / Sorties

**Entrées :**

`E3_INTERFACES_ACTEURS/E3.1_Dropzone_Factures/*.md`

**Sorties :**

`document_type.env (dotenv GitLab CI/CD)`

**Dépendances :**

`(aucune — lecture seule)`

---

## Fonctions publiques

### `lire_frontmatter(chemin: Path) → dict`

Extrait les paires clé/valeur du bloc frontmatter YAML d'un fichier Markdown.

**Paramètres :**

```
    chemin: Chemin absolu vers le fichier .md.
```

**Retourne :**

Dictionnaire des champs YAML extraits (valeurs en chaîne brute).

---

### `detecter_type(fm: dict) → str`

Mappe le champ 'type' du frontmatter vers un type de document normalisé.

**Paramètres :**

```
    fm: Dictionnaire frontmatter produit par lire_frontmatter().
```

**Retourne :**

Type normalisé (str) selon TYPES_VALIDES, ou "inconnu" si absent.

---

### `scanner_dropzone(dropzone: Path) → list[dict]`

Scanne tous les fichiers .md dans la dropzone et retourne leurs métadonnées.

**Paramètres :**

```
    dropzone: Chemin vers E3.1_Dropzone_Factures.
```

**Retourne :**

Liste de dictionnaires, un par fichier trouvé, contenant :
        - fichier (str)  : nom du fichier
        - type (str)     : type normalisé
        - tags (str)     : tags bruts du frontmatter
        - statut (str)   : valeur du champ 'statut' du frontmatter
        - id (str)       : valeur du champ 'id' ou nom du fichier

---

### `ecrire_dotenv(documents: list[dict], output: Path) → None`

Produit le fichier dotenv pour GitLab CI/CD artifacts:reports:dotenv.

**Paramètres :**

```
    documents: Liste produite par scanner_dropzone().
    output:    Chemin du fichier .env à écrire.
```

---

## Point d'entrée — `main()`

Point d'entrée CLI du stage DETECT.

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `DETECT_DOCUMENT` |
| DOC_ID | `DOC_0002` |
| Révision doc | `1` |
| SHA-256 source | `cf510afe` |
| Fichier source | `detect_document_type.py` |
| Généré le | 2026-02-25 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*