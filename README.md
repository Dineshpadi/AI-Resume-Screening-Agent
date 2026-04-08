# Resume Matcher – RAG-Powered ATS Assistant

## Overview

Resume Matcher is an AI-driven assistant that screens resumes against job descriptions using a Retrieval-Augmented Generation (RAG) workflow. It parses PDF/DOCX files, extracts relevant text, builds vector embeddings, retrieves supporting context, and generates explainable match summaries through Groq LLMs. The project provides both command-line and FastAPI interfaces for automation and integration.

## Key Features

- **Document parsing** for resumes and job descriptions (PDF/DOCX).
- **Skill extraction and ATS scoring** to highlight matched/missing skills.
- **RAG pipeline** that stores embeddings and retrieves context via ChromaDB.
- **LLM reasoning** (Groq) for concise bullet-point explanations.
- **CLI, Streamlit, and FastAPI** entry points to suit different workflows.

## Project Structure

```
RM Bot/
├─ config/
│  └─ settings.py           # Paths, environment variables, model configuration
├─ data/
│  ├─ resumes/              # Source resume files (PDF/DOCX)
│  ├─ job_desc/             # Source job descriptions (PDF/DOCX)
│  └─ processed/
│     ├─ text/              # Parsed plain-text exports produced by the pipeline
│     └─ chroma/            # Persisted ChromaDB embeddings
├─ hr_a/
│  └─ hr.py                 # Core evaluator combining skills, ATS score, and reasoning
├─ modules/
│  ├─ embeddings/           # SentenceTransformer wrapper
│  ├─ job_matching/         # Skill extractor, ATS scoring, and RAG-enabled reasoning
│  ├─ pipelines/            # RAG preprocessing/embedding and analysis pipelines
│  ├─ vectordb/             # ChromaDB persistence layer
│  └─ api/                  # FastAPI application exposing analysis endpoints
├─ rm.py                    # CLI agent for local screening
├─ rmapp.py                 # Streamlit UI (optional front-end)
└─ requirements.txt         # Python dependencies
```

## Prerequisites

- Python 3.10+
- pip / virtualenv (recommended)
- Groq API key (`GROQ_API_KEY`)
- Optional: Hugging Face token (`HF_TOKEN`) for faster model downloads

## Installation & Setup

1. **Create and activate a virtual environment** (recommended):

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment variables** in a `.env` file placed at the project root:

   ```dotenv
   GROQ_API_KEY=your_groq_api_key
   # Optional overrides
   EXPLAIN_MATCH_JOB_SAMPLE="Example job description"
   EXPLAIN_MATCH_RESUME_SAMPLE="Example resume"
   HF_TOKEN=your_hf_token
   ```

4. **Place your documents**:

   - Add resume files (PDF/DOCX) to `data/resumes/`.
   - Add job description files (PDF/DOCX) to `data/job_desc/`.

## Running the RAG Pipeline

Execute the preprocessing + embedding pipeline (parses documents, writes text copies, stores embeddings):

```powershell
python -m modules.pipelines.rag_pipeline
```

Outputs are stored under `data/processed/` (plain text and ChromaDB data).

## CLI Analysis

Run the end-to-end analysis and print ATS scores, matched/missing skills, and RAG explanations:

```powershell
python -m modules.pipelines.rag_analysis
```

Pass `--` arguments if you need to reprocess embeddings every run by editing the script invocation (`analyze_candidates(reprocess_embeddings=True)`).

For the legacy loop-based CLI agent:

```powershell
python rm.py
```

## Streamlit Dashboard (Optional)

Launch the interactive UI provided by `rmapp.py`:

```powershell
streamlit run rmapp.py
``` 

Visit the local URL shown in the terminal to interact with the dashboard.

## FastAPI Service

Start the REST API for integration scenarios:

```powershell
uvicorn modules.api.app:app --reload
``` 

- `GET /health` → readiness probe.
- `POST /analyze` → triggers the RAG workflow and returns structured results.

Example request: 

```http 
POST /analyze HTTP/1.1
Content-Type: application/json

{
  "reprocess_embeddings": false
}
```

Sample response:

```json
{
  "jobs": [
    {
      "job_name": "data_science_ai_job_descriptions.pdf",
      "candidates": [
        {
          "candidate": "Dhanushkumar K Resume.pdf",
          "score": 83.33,
          "matched": ["python", "sql", "machine learning", "power bi"],
          "missing": ["docker", "pytorch"],
          "reason": "• Strong Python skills ..."
        }
      ]
    }
  ]
}
```

## Components in Detail

- `modules.pipelines.rag_pipeline` – orchestrates directory setup, parsing via `utils.file_loader`, embedding generation with `SentenceTransformer`, and persistence to ChromaDB.
- `modules.pipelines.rag_analysis` – wraps preprocessing, optional embedding regeneration, and candidate evaluation to produce structured results.
- `modules.job_matching.reasoning` – performs RAG retrieval from ChromaDB and prompts the Groq LLM for explainable bullet-point analyses.
- `modules.job_matching.skill_extractor` – extracts skills (regex/NLP based) from text bodies.
- `modules.job_matching.ats_score` – computes ATS alignment metrics and surfaces matched/missing skills.
- `modules.api.app` – FastAPI app exposing `/analyze` endpoint built atop the RAG pipeline.
- `hr_a.hr.evaluate_candidate` – combines skill extraction, ATS scoring, and reasoning for a single job/resume pair.

## Troubleshooting

- **Missing Groq key**: ensure `GROQ_API_KEY` is set in `.env` before running reasoning.
- **Slow model downloads**: set `HF_TOKEN` to benefit from authenticated Hugging Face downloads.
- **Chroma store reset**: delete `data/processed/chroma/` if you need a clean embedding database, then rerun the pipeline.
- **Document parsing errors**: confirm PDFs/DOCX files are not encrypted and are placed in the correct directories.

## Roadmap Ideas

- Support additional document parsers (TXT, HTML, LinkedIn exports).
- Implement batch API endpoints for multi-job analysis.
- Add persistence for ATS results in a relational/database storage layer.
- Extend Streamlit UI with upload capability and filtering.


