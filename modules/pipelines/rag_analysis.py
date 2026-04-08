import logging
from typing import Dict, Tuple, List, Any

from hr_a.hr import evaluate_candidate
from modules.pipelines.rag_pipeline import preprocess_documents, generate_embeddings

logger = logging.getLogger("rag.analysis")


def _split_documents(documents: List[Tuple[str, str, str]]) -> Tuple[Dict[str, str], Dict[str, str]]:
    resumes: Dict[str, str] = {}
    jobs: Dict[str, str] = {}

    for doc_id, text, doc_type in documents:
        if doc_type == "resume" and doc_id.startswith("resume::"):
            resumes[doc_id.split("::", 1)[1]] = text
        elif doc_type == "job" and doc_id.startswith("job::"):
            jobs[doc_id.split("::", 1)[1]] = text

    return resumes, jobs


def collect_analysis(reprocess_embeddings: bool = True) -> List[Dict[str, Any]]:
    """Run preprocessing (and optionally embeddings) returning structured results."""

    logger.info("Starting RAG preprocessing")
    documents = preprocess_documents()

    if reprocess_embeddings:
        logger.info("Generating embeddings for %d documents", len(documents))
        generate_embeddings(documents)

    resumes, jobs = _split_documents(documents)

    if not resumes:
        logger.warning("No resumes found for analysis")
        return []

    if not jobs:
        logger.warning("No job descriptions found for analysis")
        return []

    analyses: List[Dict[str, Any]] = []

    for job_name, job_text in jobs.items():
        logger.info("Evaluating candidates for job '%s'", job_name)
        candidates = []

        for resume_name, resume_text in resumes.items():
            result = evaluate_candidate(job_text, resume_text, resume_name)
            candidates.append(result)

        analyses.append({
            "job_name": job_name,
            "candidates": candidates,
        })

    logger.info("Completed analysis for %d job(s)", len(analyses))

    return analyses


def analyze_candidates(reprocess_embeddings: bool = True) -> None:
    """Run the full RAG flow and print ATS analysis for every job/resume pair."""

    results = collect_analysis(reprocess_embeddings=reprocess_embeddings)

    if not results:
        print("No analysis results available.")
        return

    for job_result in results:
        job_name = job_result["job_name"]
        print("\n================================================")
        print("Job Description:", job_name)
        print("================================================")

        for candidate in job_result["candidates"]:
            print("\nCandidate:", candidate["candidate"])
            print("ATS Score:", candidate["score"], "%")

            print("\nMatched Skills")
            for skill in candidate["matched"]:
                print("✓", skill)

            print("\nMissing Skills")
            for skill in candidate["missing"]:
                print("✗", skill)

            print("\nAI Analysis")
            print(candidate["reason"])
            print("\n--------------------------------------")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyze_candidates()
