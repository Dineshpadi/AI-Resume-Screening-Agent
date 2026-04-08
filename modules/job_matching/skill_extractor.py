import re

SKILLS_DB = [
    "python","machine learning","deep learning","sql",
    "pandas","numpy","tensorflow","pytorch","nlp",
    "docker","aws","spark","power bi","tableau"
]

def extract_skills(text):

    text = text.lower()

    skills_found = []

    for skill in SKILLS_DB:
        if re.search(r'\b'+skill+r'\b', text):
            skills_found.append(skill)

    return list(set(skills_found))