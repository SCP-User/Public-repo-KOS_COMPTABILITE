---
ergo_id: DOC_GENERATOR
doc_id: DOC_0003
fichier: doc_generator.py
version: 1.1.0
doc_revision: 1
sha256_source: bae0625c
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-25
---

# DOC_GENERATOR — `doc_generator.py`

## Rôle

Genere la documentation Markdown versionnee des composants ERGO_ID

---

## Description

doc_generator.py
ERGO KOS_COMPTA — Générateur de Documentation Markdown

Lit chaque fichier Python portant un header `# ERGO_ID:` dans E0_MOTEUR_AGENTIQUE,
extrait la structure du code (module docstring, ERGO_REGISTRY, fonctions + docstrings,
signatures typées), et génère un fichier `.md` de documentation par composant
dans le dossier `docs/`.

Les fichiers générés suivent un template fixe lisible par un humain ET par un LLM.
Ils servent de référence documentaire versionnable, indépendante du code source.

Chaque doc reçoit un identifiant unique `DOC_XXXX` tracé dans `DOC_INDEX.json`.
La révision s'incrémente automatiquement quand le SHA-256 de la source change.

---

## Entrées / Sorties

**Entrées :**

`E0_MOTEUR_AGENTIQUE/*.py avec header ERGO_ID`

**Sorties :**

- `E0_MOTEUR_AGENTIQUE/docs/<ergo_id>.md`
- `E0_MOTEUR_AGENTIQUE/docs/DOC_INDEX.json`

**Dépendances :**

- `(stdlib uniquement — ast`
- `re`
- `hashlib`
- `json)`

---

## Fonctions publiques

### `sha256_fichier(chemin: Path) → str`

Calcule un SHA-256 tronqué (8 chars) du contenu d'un fichier.

**Paramètres :**

```
    chemin: Chemin absolu vers le fichier à hasher.
```

**Retourne :**

8 premiers caractères du SHA-256 hexadécimal, ou "ABSENT" si le fichier n'existe pas.

---

### `charger_doc_index(docs_dir: Path) → list[dict]`

Charge le DOC_INDEX.json existant depuis le dossier docs/.

**Paramètres :**

```
    docs_dir: Dossier docs/ contenant DOC_INDEX.json.
```

**Retourne :**

Liste des entrées de l'index, ou liste vide si absent ou corrompu.

---

### `sauvegarder_doc_index(docs_dir: Path, docs: list[dict]) → None`

Persiste le DOC_INDEX.json avec métadonnées globales.

**Paramètres :**

```
    docs_dir: Dossier docs/ cible.
    docs:     Liste complète des entrées de documentation à sauvegarder.
```

---

### `prochain_doc_id(index: list[dict]) → str`

Calcule le prochain identifiant DOC_XXXX séquentiel.

**Paramètres :**

```
    index: Liste actuelle des entrées DOC.
```

**Retourne :**

Identifiant au format "DOC_XXXX" (ex: "DOC_0001").

---

### `mettre_a_jour_index(index: list[dict], ergo_id: str, chemin_source: Path, chemin_doc: Path, sha256: str, source_version: str) → tuple[dict, bool]`

Met à jour ou crée l'entrée DOC pour un composant dans l'index.

**Paramètres :**

```
    index:          Index courant des DOC.
    ergo_id:        ERGO_ID du composant.
    chemin_source:  Chemin vers le fichier .py source.
    chemin_doc:     Chemin vers le fichier .md généré.
    sha256:         SHA-256 tronqué (8 chars) du fichier source.
    source_version: Version extraite de ERGO_REGISTRY.
```

**Retourne :**

Tuple (entree, est_nouvelle) — l'entrée mise à jour et True si elle est nouvelle.

---

### `extraire_ergo_id(contenu: str) → Optional[str]`

Extrait le ERGO_ID depuis le header d'un fichier Python.

**Paramètres :**

```
    contenu: Contenu texte complet du fichier.
```

**Retourne :**

Valeur du ERGO_ID ou None si absent.

---

### `extraire_registry(contenu: str) → dict`

Parse la section ERGO_REGISTRY de la docstring d'un fichier.

**Paramètres :**

```
    contenu: Contenu texte complet du fichier.
```

**Retourne :**

Dictionnaire des métadonnées ERGO_REGISTRY.

---

### `extraire_module_description(contenu: str) → str`

Extrait la description principale du module depuis sa docstring.

**Paramètres :**

```
    contenu: Contenu texte complet du fichier.
```

**Retourne :**

Description lisible du module (texte brut).

---

### `extraire_fonctions(contenu: str, chemin: Path) → list[dict]`

Extrait toutes les fonctions d'un fichier Python via AST.

**Paramètres :**

```
    contenu: Contenu texte complet du fichier Python.
    chemin:  Chemin du fichier (pour les messages d'erreur).
```

**Retourne :**

Liste de dictionnaires décrivant chaque fonction :
        - nom, signature, docstring_titre, docstring_args,
          docstring_returns, docstring_raises, est_privee, ligne

---

### `formater_liste_md(items) → str`

Formate une valeur (str ou list) en liste Markdown.

**Paramètres :**

```
    items: Chaîne simple ou liste de chaînes.
```

**Retourne :**

Bloc Markdown avec items sur des lignes séparées ou valeur brute.

---

### `generer_md(chemin: Path, meta_doc: Optional[dict]) → Optional[tuple[str, str]]`

Génère le contenu Markdown de documentation pour un fichier Python.

**Paramètres :**

```
    chemin:   Chemin absolu vers le fichier .py à documenter.
    meta_doc: Métadonnées DOC (doc_id, doc_revision, sha256_source) ou None.
```

**Retourne :**

Tuple (ergo_id, contenu_markdown) ou None si le fichier n'a pas d'ERGO_ID.

---

## Point d'entrée — `main()`

Point d'entrée CLI du générateur de documentation Markdown versionné.

---

## Fonctions internes

| Fonction | Rôle |
|---|---|
| `_extraire_section_docstring()` | Extrait une section nommée (Args, Returns, Raises) d'une docstring Google-style. |

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `DOC_GENERATOR` |
| DOC_ID | `DOC_0003` |
| Révision doc | `1` |
| SHA-256 source | `bae0625c` |
| Fichier source | `doc_generator.py` |
| Généré le | 2026-02-25 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*