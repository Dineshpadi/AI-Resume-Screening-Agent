from modules.job_matching.skill_extractor import extract_skills
from modules.job_matching.ats_score import calculate_ats_score
from modules.job_matching.reasoning import explain_match


def evaluate_candidate(job_text, resume_text, resume_name):

    job_skills = extract_skills(job_text)

    resume_skills = extract_skills(resume_text)

    score, matched, missing = calculate_ats_score(job_skills, resume_skills)

    reasoning = explain_match(job_text, resume_text)

    return {
        "candidate": resume_name,
        "score": score,
        "matched": matched,
        "missing": missing,
        "reason": reasoning
    }