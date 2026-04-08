import streamlit as st
from hr_a.hr import evaluate_candidate
from utils.file_loader import load_file
from groq import Groq
from dotenv import load_dotenv
import tempfile
import os

# Load environment variables
load_dotenv()

# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="AI Resume Screening Agent",
    page_icon="LB",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Home", "Resume Analysis", "Interview Preparation"]
)

# =============================
# HOME PAGE
# =============================

if page == "Home":

    st.title("AI Resume Screening Agent")

    st.markdown(
    """
    Welcome to the **AI Hiring Assistant**.

    This system helps recruiters evaluate candidates quickly.

    ### Features

    ✔ Resume ATS Score  
    ✔ Skill Matching  
    ✔ AI Resume Analysis  
    ✔ Interview Question Generator  
    """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Upload job description")

    with col2:
        st.success("AI analyzes resume")

    with col3:
        st.warning("Generate interview questions")

    st.divider()

    st.subheader("How It Works")

    st.markdown(
    """
    1. Upload Job Description  
    2. Upload Resume  
    3. AI calculates ATS score  
    4. AI analyzes candidate fit  
    5. Prepare interview questions
    """
    )


# =============================
# RESUME ANALYSIS PAGE
# =============================

elif page == "Resume Analysis":

    st.title("Resume Analysis")

    st.write("Upload Job Description and Resume")

    job_file = st.file_uploader(
        "Upload Job Description",
        type=["pdf","docx"]
    )

    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf","docx"]
    )

    if st.button("Analyze Candidate"):

        if job_file and resume_file:

            # Save job description
            with tempfile.NamedTemporaryFile(delete=False) as tmp_job:
                tmp_job.write(job_file.read())
                job_path = tmp_job.name

            # Save resume
            with tempfile.NamedTemporaryFile(delete=False) as tmp_resume:
                tmp_resume.write(resume_file.read())
                resume_path = tmp_resume.name

            # Load files using correct filename
            job_text = load_file(job_path, job_file.name)
            resume_text = load_file(resume_path, resume_file.name)

            # Evaluate candidate
            result = evaluate_candidate(job_text, resume_text, resume_file.name)

            st.divider()

            st.subheader("ATS Score")
            st.metric("Match Score", f"{result['score']}%")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Matched Skills")

                for skill in result["matched"]:
                    st.write(f"✔ {skill}")

            with col2:
                st.subheader("❌ Missing Skills")

                for skill in result["missing"]:
                    st.write(f"✘ {skill}")

            st.divider()

            st.subheader("AI Analysis")

            st.success(result["reason"])

        else:
            st.warning("Please upload both files")


# =============================
# INTERVIEW PREPARATION PAGE
# =============================

elif page == "Interview Preparation":

    st.title("Interview Preparation")

    st.write("Upload Job Description")

    jd_file = st.file_uploader(
        "Upload Job Description",
        type=["pdf","docx"]
    )

    if st.button("Generate Interview Questions"):

        if jd_file:

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(jd_file.read())
                jd_path = tmp.name

            jd_text = load_file(jd_path, jd_file.name)

            prompt = f"""
You are a technical interviewer.

Generate:

• 5 technical interview questions  
• 3 behavioral interview questions  

Based on this job description:

{jd_text[:1500]}
"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"user","content":prompt}],
                max_tokens=200,
                temperature=0.3
            )

            st.subheader("Interview Questions")

            st.write(response.choices[0].message.content)

        else:
            st.warning("Upload a job description first")