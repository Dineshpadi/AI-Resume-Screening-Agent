from hr_a.hr import evaluate_candidate
import os

from config.settings import JOB_DESC_PATH, RESUME_PATH
from utils.file_loader import load_file


def load_resumes():

    resumes = {}

    for file in os.listdir(RESUME_PATH):
        path = os.path.join(RESUME_PATH, file)
        resumes[file] = load_file(path, file)

    return resumes


def load_jobs():

    jobs = {}

    for file in os.listdir(JOB_DESC_PATH):
        path = os.path.join(JOB_DESC_PATH, file)
        jobs[file] = load_file(path, file)

    return jobs


def main():

    resumes = load_resumes()
    jobs = load_jobs()

    for job, job_text in jobs.items():

        print("\n================================================")
        print("AI Resume Screening Agent")
        print("================================================")

        print("\nJob Description:", job)

        for resume, resume_text in resumes.items():

            result = evaluate_candidate(job_text, resume_text, resume)

            print("\nCandidate:", result["candidate"])
            print("ATS Score:", result["score"], "%")

            print("\nMatched Skills")
            for s in result["matched"]:
                print("✓", s)

            print("\nMissing Skills")
            for s in result["missing"]:
                print("✗", s)

            print("\nAI Analysis")
            print(result["reason"])

            print("\n--------------------------------------")


if __name__ == "__main__":
    main()