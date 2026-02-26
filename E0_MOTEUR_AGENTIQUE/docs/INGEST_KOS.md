---
ergo_id: INGEST_KOS
doc_id: DOC_0009
fichier: ingest_kos.py
version: 1.0.0
doc_revision: 1
sha256_source: 94b90fa1
auteur: ERGO Capital / Adam
derniere_mise_a_jour: 2026-02-25
---

# INGEST_KOS — `ingest_kos.py`

## Rôle

RAG Ingestion — parse E1/E2, chunk, embed, stocke dans ChromaDB

---

## Description

ingest_kos.py
ERGO KOS_COMPTA — Module RAG ChromaDB
Hackathon GitLab AI 2026

Ingestion vectorielle des normes E1/E2 dans ChromaDB.
Parse, chunk, encode (multilingual-e5-base) et stocke les documents légaux.

---

## Entrées / Sorties

**Entrées :**

- `E1_CORPUS_LEGAL_ETAT/*.md`
- `E2_SOP_INTERNE_ET_ERP/*.md`

**Sorties :**

`KOS_DB/ (ChromaDB persistant)`

**Dépendances :**

- `chromadb`
- `sentence-transformers`
- `langchain-text-splitters`
- `python-frontmatter`

---

## Fonctions publiques

### `initialiser_embedding_model() → SentenceTransformer`

Charge le modèle d'embedding multilingue intfloat/multilingual-e5-base.

**Retourne :**

Instance SentenceTransformer prête à l'inférence.

---

### `scanner_documents(repertoires: list[Path]) → list[dict]`

Scanne les répertoires E1/E2 et extrait le frontmatter YAML de chaque .md.

**Paramètres :**

```
    repertoires: Liste de chemins vers les répertoires à parcourir.
```

**Retourne :**

Liste de dicts, chacun contenant :
        - chemin   (str)  : chemin absolu du fichier
        - metadata (dict) : frontmatter extrait (type, source, version, tags, applicable_a, fichier)
        - contenu  (str)  : corps Markdown hors frontmatter

---

### `chunker_document(contenu: str, metadata: dict, nom: str) → list[dict]`

Découpe un document en chunks avec recouvrement (chunk_size=700, overlap=100).

**Paramètres :**

```
    contenu:  Corps textuel du document (hors frontmatter).
    metadata: Métadonnées du document parent, héritées par chaque chunk.
    nom:      Chemin ou nom du fichier source (utilisé pour le stem de l'ID).
```

**Retourne :**

Liste de dicts, chacun contenant :
        - id       (str)  : identifiant unique "{stem}_chunk_{i}"
        - texte    (str)  : texte brut du chunk
        - metadata (dict) : métadonnées héritées

---

### `initialiser_chromadb(chemin: Path) → chromadb.Collection`

Crée ou charge la collection ChromaDB "kos_knowledge_base" avec distance cosinus.

**Paramètres :**

```
    chemin: Chemin du répertoire de stockage ChromaDB (ex: ./KOS_DB).
```

**Retourne :**

Collection ChromaDB configurée avec hnsw:space = cosine.

---

### `ingerer(collection: chromadb.Collection, chunks: list[dict], model: SentenceTransformer, batch_size: int) → int`

Encode les chunks et les upserte dans ChromaDB par batch.

**Paramètres :**

```
    collection: Collection ChromaDB cible.
    chunks:     Liste de dicts produits par chunker_document().
    model:      SentenceTransformer chargé par initialiser_embedding_model().
    batch_size: Taille des batchs d'embedding (défaut : 32).
```

**Retourne :**

Nombre total de chunks upsertés.

---

## Point d'entrée — `main()`

Orchestration complète du pipeline RAG : scan → chunk → embed → upsert.

---

## Traçabilité

| Champ | Valeur |
|---|---|
| ERGO_ID | `INGEST_KOS` |
| DOC_ID | `DOC_0009` |
| Révision doc | `1` |
| SHA-256 source | `94b90fa1` |
| Fichier source | `ingest_kos.py` |
| Généré le | 2026-02-25 |
| Générateur | `doc_generator.py` (ERGO_ID: DOC_GENERATOR) |

*Documentation auto-générée par ERGO KOS_COMPTA — ne pas éditer manuellement.*
*Pour mettre à jour : `python E0_MOTEUR_AGENTIQUE/doc_generator.py`*