# ERGO_ID: INGEST_KOS
"""
ingest_kos.py
=============
ERGO KOS_COMPTA — Module RAG ChromaDB
Hackathon GitLab AI 2026

Ingestion vectorielle des normes E1/E2 dans ChromaDB.
Parse, chunk, encode (multilingual-e5-base) et stocke les documents légaux.

ERGO_REGISTRY:
    role         : RAG Ingestion — parse E1/E2, chunk, embed, stocke dans ChromaDB
    version      : 1.0.0
    auteur       : ERGO Capital / Adam
    dependances  : chromadb, sentence-transformers, langchain-text-splitters, python-frontmatter
    entrees      : E1_CORPUS_LEGAL_ETAT/*.md, E2_SOP_INTERNE_ET_ERP/*.md
    sorties      : KOS_DB/ (ChromaDB persistant)
"""

import logging
import time
from pathlib import Path

import frontmatter
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).parent.parent
E1_LEGAL = BASE_DIR / "E1_CORPUS_LEGAL_ETAT"
E2_SOP   = BASE_DIR / "E2_SOP_INTERNE_ET_ERP"
KOS_DB   = BASE_DIR / "KOS_DB"


def initialiser_embedding_model() -> SentenceTransformer:
    """Charge le modèle d'embedding multilingue intfloat/multilingual-e5-base.

    Détecte automatiquement CUDA ; bascule sur CPU avec avertissement si absent.

    Returns:
        Instance SentenceTransformer prête à l'inférence.
    """
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        logging.warning("CUDA non disponible — embedding sur CPU (plus lent).")
    model = SentenceTransformer("intfloat/multilingual-e5-base", device=device)
    logging.info("Modèle multilingual-e5-base chargé sur %s.", device)
    return model


def scanner_documents(repertoires: list[Path]) -> list[dict]:
    """Scanne les répertoires E1/E2 et extrait le frontmatter YAML de chaque .md.

    Un répertoire inexistant est ignoré avec un avertissement (cas E2 vide).

    Args:
        repertoires: Liste de chemins vers les répertoires à parcourir.

    Returns:
        Liste de dicts, chacun contenant :
            - chemin   (str)  : chemin absolu du fichier
            - metadata (dict) : frontmatter extrait (type, source, version, tags, applicable_a, fichier)
            - contenu  (str)  : corps Markdown hors frontmatter
    """
    documents: list[dict] = []
    for repertoire in repertoires:
        if not repertoire.exists():
            logging.warning("Répertoire introuvable, ignoré : %s", repertoire)
            continue
        for fichier in sorted(repertoire.glob("**/*.md")):
            try:
                post = frontmatter.load(str(fichier))
                metadata = {
                    "type":         str(post.metadata.get("type", "")),
                    "source":       str(post.metadata.get("source", "")),
                    "version":      str(post.metadata.get("version", "")),
                    "tags":         str(post.metadata.get("tags", [])),
                    "applicable_a": str(post.metadata.get("applicable_a", [])),
                    "fichier":      fichier.name,
                }
                documents.append(
                    {"chemin": str(fichier), "metadata": metadata, "contenu": post.content}
                )
                logging.info("  Scanné : %s", fichier.name)
            except Exception as exc:
                logging.warning("  Échec lecture %s : %s", fichier.name, exc)
    return documents


def chunker_document(contenu: str, metadata: dict, nom: str) -> list[dict]:
    """Découpe un document en chunks avec recouvrement (chunk_size=700, overlap=100).

    Chaque chunk hérite des métadonnées du document parent. L'ID est construit
    à partir du stem du fichier source et de l'index du chunk.

    Args:
        contenu:  Corps textuel du document (hors frontmatter).
        metadata: Métadonnées du document parent, héritées par chaque chunk.
        nom:      Chemin ou nom du fichier source (utilisé pour le stem de l'ID).

    Returns:
        Liste de dicts, chacun contenant :
            - id       (str)  : identifiant unique "{stem}_chunk_{i}"
            - texte    (str)  : texte brut du chunk
            - metadata (dict) : métadonnées héritées
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    morceaux = splitter.split_text(contenu)
    stem = Path(nom).stem
    return [
        {"id": f"{stem}_chunk_{i}", "texte": morceau, "metadata": metadata}
        for i, morceau in enumerate(morceaux)
    ]


def initialiser_chromadb(chemin: Path) -> chromadb.Collection:
    """Crée ou charge la collection ChromaDB "kos_knowledge_base" avec distance cosinus.

    Le répertoire de stockage est créé si absent. La collection est récupérée
    si elle existe déjà (idempotence garantie via upsert dans ingerer()).

    Args:
        chemin: Chemin du répertoire de stockage ChromaDB (ex: ./KOS_DB).

    Returns:
        Collection ChromaDB configurée avec hnsw:space = cosine.
    """
    chemin.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chemin))
    collection = client.get_or_create_collection(
        name="kos_knowledge_base",
        metadata={"hnsw:space": "cosine"},
    )
    logging.info(
        "ChromaDB initialisé : %s — %d vecteurs existants.", chemin, collection.count()
    )
    return collection


def ingerer(
    collection: chromadb.Collection,
    chunks: list[dict],
    model: SentenceTransformer,
    batch_size: int = 32,
) -> int:
    """Encode les chunks et les upserte dans ChromaDB par batch.

    Le préfixe "passage: " est ajouté devant chaque texte avant l'embedding,
    conformément à l'entraînement asymétrique du modèle multilingual-e5-base
    (textes ingérés = passages ; requêtes = "query: ").

    Args:
        collection: Collection ChromaDB cible.
        chunks:     Liste de dicts produits par chunker_document().
        model:      SentenceTransformer chargé par initialiser_embedding_model().
        batch_size: Taille des batchs d'embedding (défaut : 32).

    Returns:
        Nombre total de chunks upsertés.
    """
    total = 0
    for debut in range(0, len(chunks), batch_size):
        lot = chunks[debut : debut + batch_size]
        textes_prefixes = [f"passage: {c['texte']}" for c in lot]
        vecteurs = model.encode(textes_prefixes, normalize_embeddings=True).tolist()
        collection.upsert(
            ids=[c["id"] for c in lot],
            embeddings=vecteurs,
            documents=[c["texte"] for c in lot],
            metadatas=[c["metadata"] for c in lot],
        )
        total += len(lot)
        logging.info("  Batch upsert : %d/%d chunks.", total, len(chunks))
    return total


def main() -> None:
    """Orchestration complète du pipeline RAG : scan → chunk → embed → upsert.

    Log final : nombre de documents, chunks ingérés, et durée totale.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s — %(message)s")
    debut = time.time()
    logging.info("=== ERGO KOS_COMPTA — Ingestion RAG ===")

    model      = initialiser_embedding_model()
    documents  = scanner_documents([E1_LEGAL, E2_SOP])
    collection = initialiser_chromadb(KOS_DB)

    tous_chunks: list[dict] = []
    for doc in documents:
        chunks = chunker_document(doc["contenu"], doc["metadata"], doc["chemin"])
        tous_chunks.extend(chunks)

    if not tous_chunks:
        logging.warning("Aucun chunk à ingérer — vérifier E1/E2.")
        return

    total_chunks = ingerer(collection, tous_chunks, model)
    duree = round(time.time() - debut, 2)
    logging.info(
        "=== Ingestion terminée : %d documents, %d chunks, %.2fs — KOS_DB/ peuplé ===",
        len(documents),
        total_chunks,
        duree,
    )


if __name__ == "__main__":
    main()
