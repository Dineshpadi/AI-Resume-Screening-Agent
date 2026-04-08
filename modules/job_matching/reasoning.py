from groq import Groq
from dotenv import load_dotenv
import os
import logging
from typing import List

from config.settings import VECTOR_DB_DIR, EMBEDDING_MODEL
from modules.embeddings.embedding_model import EmbeddingModel
from modules.vectordb.chroma_store import ChromaStore


logger = logging.getLogger("rag.reasoning")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False

CHROMA_DIR = os.path.join(VECTOR_DB_DIR, "chroma")
RETRIEVAL_TOP_K = 4
MAX_CONTEXT_CHARS = 800

_embedder: EmbeddingModel | None = None
_store: ChromaStore | None = None


def _get_embedder() -> EmbeddingModel:
    global _embedder

    if _embedder is None:
        logger.info("Initialising embedding model for RAG reasoning")
        _embedder = EmbeddingModel(EMBEDDING_MODEL)

    return _embedder


def _get_store() -> ChromaStore:
    global _store

    if _store is None:
        os.makedirs(CHROMA_DIR, exist_ok=True)
        logger.info("Connecting to Chroma vector store at %s", CHROMA_DIR)
        _store = ChromaStore(CHROMA_DIR)

    return _store


def _retrieve_context(job_text: str, resume_text: str) -> List[str]:
    try:
        embedder = _get_embedder()
        store = _get_store()
    except Exception:
        logger.exception("Failed to initialise RAG components")
        return []

    query = (
        "Job Requirements:\n"
        f"{job_text[:600]}\n\n"
        "Candidate Summary:\n"
        f"{resume_text[:600]}"
    )

    try:
        embedding = embedder.embed(query)
        results = store.search(embedding, n_results=RETRIEVAL_TOP_K)
    except Exception:
        logger.exception("Vector search failed for explain_match")
        return []

    documents = results.get("documents") if results else None
    metadatas = results.get("metadatas") if results else None

    if not documents or not documents[0]:
        logger.warning("No context documents retrieved for explain_match")
        return []

    contexts: List[str] = []

    for idx, doc in enumerate(documents[0]):
        meta = {}

        if metadatas and metadatas[0] and idx < len(metadatas[0]):
            meta = metadatas[0][idx] or {}

        doc_type = meta.get("type", "document").upper()
        snippet = doc[:MAX_CONTEXT_CHARS]
        contexts.append(f"{doc_type} CONTEXT:\n{snippet}")

    logger.info("Retrieved %d context chunks for explain_match", len(contexts))

    return contexts


# Load environment variables from .env
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def explain_match(job_text, resume_text):
    """
    Uses an LLM to generate a short explanation of why a resume matches
    a given job description.
    """

    contexts = _retrieve_context(job_text, resume_text)

    context_block = "\n\nRAG CONTEXT:\n" + "\n\n".join(contexts) if contexts else ""

    prompt = f"""
You are an AI hiring assistant.

Analyze the job description and candidate resume.

Return ONLY 5 short bullet points explaining the candidate-job match.

STRICT RULES:
- DO NOT write any introduction
- DO NOT write headings
- DO NOT write explanations
- ONLY return bullet points
- Each bullet must be one line
- Maximum 5 bullets

Example Output:

• Strong Python and SQL skills match job requirements
• Good experience with machine learning models
• Familiar with data visualization tools like Power BI
• Missing cloud technologies like AWS or Docker
• Overall a strong candidate for interview

JOB DESCRIPTION:
{job_text[:1200]}

RESUME:
{resume_text[:1200]}
RAG Context Follows (if any):
{context_block}
"""

    try:
        logger.info(
            "explain_match request | job_chars=%d resume_chars=%d",
            len(job_text),
            len(resume_text),
        )
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()
        logger.info("explain_match response | %s", content)

        return content

    except Exception as e:
        logger.exception("explain_match failed")
        return f"AI reasoning unavailable: {str(e)}"


def main():
    job_sample = os.getenv(
        "EXPLAIN_MATCH_JOB_SAMPLE",
        "Sample job description placeholder.",
    )
    resume_sample = os.getenv(
        "EXPLAIN_MATCH_RESUME_SAMPLE",
        "Sample resume placeholder.",
    )

    logger.info("Running explain_match from CLI with sample data")
    result = explain_match(job_sample, resume_sample)
    print("Explanation:\n")
    print(result)


if __name__ == "__main__":
    main()