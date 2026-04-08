def calculate_ats_score(job_skills, resume_skills):

    matched = set(job_skills) & set(resume_skills)
    missing = set(job_skills) - set(resume_skills)

    if len(job_skills) == 0:
        return 0, [], []

    score = (len(matched)/len(job_skills))*100

    return round(score,2), list(matched), list(missing)