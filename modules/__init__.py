"""Core modules package for the Resume Matcher project.

Subpackages
-----------
embeddings
    Wrappers around embedding models (SentenceTransformers).
job_matching
    Candidate evaluation utilities (skills extraction, ATS scoring, LLM reasoning).
pipelines
    Preprocessing, embedding, and analysis pipelines for the RAG workflow.
vectordb
    Vector database connectors (currently ChromaDB).
api
    FastAPI application exposing the RAG analysis endpoints.
"""
