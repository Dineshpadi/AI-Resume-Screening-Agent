import os
import logging
from typing import List, Tuple

from config.settings import (
    RESUME_PATH,
    JOB_DESC_PATH,
    VECTOR_DB_DIR,
    EMBEDDING_MODEL,
)
from utils.file_loader import load_file
from modules.embeddings.embedding_model import EmbeddingModel
from modules.vectordb.chroma_store import ChromaStore

logger = logging.getLogger("rag.pipeline")

TEXT_BASE_DIR = os.path.join(VECTOR_DB_DIR, "text")
RESUME_TEXT_DIR = os.path.join(TEXT_BASE_DIR, "resumes")
JOB_TEXT_DIR = os.path.join(TEXT_BASE_DIR, "job_desc")
CHROMA_DIR = os.path.join(VECTOR_DB_DIR, "chroma")


def _ensure_directories() -> None:
    for path in (VECTOR_DB_DIR, TEXT_BASE_DIR, RESUME_TEXT_DIR, JOB_TEXT_DIR, CHROMA_DIR):
        os.makedirs(path, exist_ok=True)


def _extract_and_save(src_dir: str, dest_dir: str, doc_type: str) -> List[Tuple[str, str]]:
    documents: List[Tuple[str, str]] = []

    for filename in os.listdir(src_dir):
        file_path = os.path.join(src_dir, filename)

        if not os.path.isfile(file_path):
            continue

        try:
            text = load_file(file_path, filename)
        except Exception:
            logger.exception("Failed to load %s '%s'", doc_type, filename)
            continue

        output_name = os.path.splitext(filename)[0] + ".txt"
        dest_path = os.path.join(dest_dir, output_name)

        with open(dest_path, "w", encoding="utf-8") as out_file:
            out_file.write(text)

        logger.info("Saved %s text to %s", doc_type, dest_path)
        documents.append((filename, text))

    return documents


def preprocess_documents() -> List[Tuple[str, str, str]]:
    """Parse source documents and persist plain-text versions.

    Returns a list of tuples containing (doc_id, text, doc_type).
    """

    _ensure_directories()

    resume_docs = _extract_and_save(RESUME_PATH, RESUME_TEXT_DIR, "resume")
    job_docs = _extract_and_save(JOB_DESC_PATH, JOB_TEXT_DIR, "job")

    processed: List[Tuple[str, str, str]] = []

    for filename, text in resume_docs:
        doc_id = f"resume::{filename}"
        processed.append((doc_id, text, "resume"))

    for filename, text in job_docs:
        doc_id = f"job::{filename}"
        processed.append((doc_id, text, "job"))

    logger.info("Preprocessed %d documents", len(processed))

    return processed


def generate_embeddings(documents: List[Tuple[str, str, str]]) -> None:
    """Create embeddings for supplied documents and store them in ChromaDB."""

    if not documents:
        logger.warning("No documents provided for embedding generation")
        return

    _ensure_directories()

    embedder = EmbeddingModel(EMBEDDING_MODEL)
    store = ChromaStore(CHROMA_DIR)

    for doc_id, text, doc_type in documents:
        embedding = embedder.embed(text)
        metadata = {"type": doc_type}

        store.add(doc_id, embedding, metadata, text)
        logger.info("Stored embedding for %s", doc_id)


def run_pipeline() -> None:
    documents = preprocess_documents()
    generate_embeddings(documents)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
