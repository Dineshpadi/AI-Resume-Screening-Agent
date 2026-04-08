import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.getcwd()

RESUME_PATH = os.path.join(BASE_DIR, "data/resumes")
JOB_DESC_PATH = os.path.join(BASE_DIR, "data/job_desc")

VECTOR_DB_DIR = os.path.join(BASE_DIR, "data/processed")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"