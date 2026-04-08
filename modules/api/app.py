import logging
from typing import List, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel

from modules.pipelines.rag_analysis import collect_analysis

logger = logging.getLogger("rag.api")

app = FastAPI(
    title="Resume Matcher RAG API",
    description="Endpoints for running RAG-powered resume analyses",
    version="1.0.0",
)


class CandidateResponse(BaseModel):
    candidate: str
    score: float
    matched: List[str]
    missing: List[str]
    reason: str


class JobAnalysisResponse(BaseModel):
    job_name: str
    candidates: List[CandidateResponse]


class AnalyzeResponse(BaseModel):
    jobs: List[JobAnalysisResponse]


class AnalyzeRequest(BaseModel):
    reprocess_embeddings: bool = False


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Simple readiness probe."""

    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the RAG pipeline and return job/candidate analyses."""

    logger.info(
        "Received analysis request | reprocess_embeddings=%s",
        request.reprocess_embeddings,
    )

    analyses: List[Dict[str, Any]] = collect_analysis(
        reprocess_embeddings=request.reprocess_embeddings
    )

    logger.info("Returning analysis response with %d job(s)", len(analyses))

    return AnalyzeResponse(jobs=analyses)
