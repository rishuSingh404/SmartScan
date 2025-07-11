import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import os
import tempfile
from pathlib import Path
from scoring import ResumeScorer
from extract_txt import extract_text_from_pdf, extract_text_from_docx
import re
import logging
from config import Config

# Add logger
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Resume Parser & Shortlister",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar with branding and info
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/000000/resume.png", width=80)
    st.markdown("# ATS Resume Shortlister")
    st.markdown("**By Rishu Kumar Singh**")
    st.markdown("---")
    st.markdown("### Quick Links")
    st.markdown("- [GitHub](https://github.com/yourusername/your-repo-name)")
    st.markdown("- [Contact](mailto:your@email.com)")
    st.markdown("---")
    st.markdown("**Tip:** Use clear, well-formatted resumes for best results.")
    dark_mode = st.checkbox("🌙 Dark Mode (Streamlit theme)")

# Initialize session state
if 'resume_scorer' not in st.session_state:
    st.session_state.resume_scorer = ResumeScorer()
if 'processed_resumes' not in st.session_state:
    st.session_state.processed_resumes = []

st.markdown("""
<style>
.big-title { font-size: 2.5rem; font-weight: bold; color: #2c3e50; }
.section-header { font-size: 1.5rem; font-weight: 600; color: #2980b9; margin-top: 2em; }
.card { background: #f8f9fa; border-radius: 12px; padding: 1.5em 2em; margin-bottom: 1.5em; box-shadow: 0 2px 8px rgba(44,62,80,0.07); }
.ats-badge { background: #2980b9; color: white; border-radius: 8px; padding: 0.3em 1em; font-weight: bold; font-size: 1.2em; }
.progress-bar { height: 24px; border-radius: 12px; background: #e0e0e0; }
.progress-fill { height: 24px; border-radius: 12px; background: linear-gradient(90deg, #27ae60, #2980b9); color: white; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">📄 ATS Resume Parser & Shortlister</div>', unsafe_allow_html=True)
st.markdown("---")

# Step 1: Upload resumes
st.markdown('<div class="section-header">Step 1: Upload Resumes</div>', unsafe_allow_html=True)
with st.container():
    uploaded_files = st.file_uploader(
        "Choose resume files (PDF or DOCX)",
        type=['pdf', 'docx'],
        accept_multiple_files=True,
        help="Upload multiple PDF or DOCX resume files"
    )
    if uploaded_files:
        oversized = [f for f in uploaded_files if f.size > Config.MAX_FILE_SIZE]
        if oversized:
            st.error(f"Some files exceed the max size of {Config.MAX_FILE_SIZE // (1024*1024)}MB: {[f.name for f in oversized]}")
            st.stop()
        st.success(f"Uploaded {len(uploaded_files)} files")
        st.session_state.uploaded_files = uploaded_files
        for i, file in enumerate(uploaded_files):
            st.markdown(f"<div class='card'><b>📄 {file.name}</b> <span style='color:gray;'>({file.size / 1024:.1f} KB)</span></div>", unsafe_allow_html=True)
    else:
        st.info("Please upload resume files to continue.")
        st.stop()

# Step 2: Enter job description
st.markdown('<div class="section-header">Step 2: Enter Job Description</div>', unsafe_allow_html=True)
with st.container():
    job_description = st.text_area(
        "Paste the job description here (include requirements, skills, experience level, etc.)",
        height=200,
        help="Enter the complete job description including requirements, skills, and experience level"
    )
    skills_input = st.text_input(
        "Key Skills (Optional)",
        placeholder="python, machine learning, flask, sql (comma-separated)",
        help="Enter key skills separated by commas for better matching"
    )

# Step 3: Process resumes and show results
if st.button("🚀 Process Resumes", type="primary"):
    if not job_description.strip():
        st.error("Please enter a job description!")
    else:
        with st.spinner("Processing resumes..."):
            results = []
            skills_list = [skill.strip().lower() for skill in skills_input.split(',') if skill.strip()] if skills_input else None
            for file in st.session_state.uploaded_files:
                try:
                    if file.type == "application/pdf":
                        text = extract_text_from_pdf(file)
                    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        text = extract_text_from_docx(file)
                    else:
                        continue
                    score_result = st.session_state.resume_scorer.score_resume(
                        text, job_description, skills_list
                    )
                    result = {
                        'filename': file.name,
                        'file_size': file.size,
                        'final_score': score_result['final_score'],
                        'score_description': score_result['score_description'],
                        'skills_match': score_result['breakdown'].get('skills_match', 0),
                        'skills_missing': score_result['breakdown'].get('skills_missing', 0),
                        'experience_level': score_result['breakdown'].get('experience_level', 0),
                        'education': score_result['breakdown'].get('education', 0),
                        'contact_info': score_result['breakdown'].get('contact_info', 0),
                        'overall_quality': score_result['breakdown'].get('overall_quality', 0),
                        'similarity_score': score_result['breakdown'].get('similarity_score', 0),
                        'recommendations': '; '.join(score_result.get('recommendations', [])),
                        'resume_text': text[:500] + "..." if len(text) > 500 else text,
                        'skills_matched': score_result.get('skills_matched', 0),
                        'skills_missing': score_result.get('skills_missing', 0)
                    }
                    results.append(result)
                except Exception as e:
                    st.error(f"Error processing {file.name}: {str(e)}")
            results.sort(key=lambda x: x['final_score'], reverse=True)
            st.session_state.processed_resumes = results
        st.success("Resumes processed successfully!")
        st.balloons()

# Show results if available
if st.session_state.processed_resumes:
    st.markdown('<div class="section-header">Step 3: Results</div>', unsafe_allow_html=True)
    skipped_count = 0
    for result in st.session_state.processed_resumes:
        if 'breakdown' not in result:
            skipped_count += 1
            continue
        with st.container():
            st.markdown(f"<div class='card'><b>📄 {result['filename']}</b> <span class='ats-badge'>ATS Score: {result['final_score']}/100</span></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='progress-bar'>
                <div class='progress-fill' style='width: {result['final_score']}%;'>
                    {result['final_score']} / 100
                </div>
            </div>
            """, unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Match Breakdown:**")
                st.write(f"- Skills Matched: {result['skills_matched']}")
                st.write(f"- Skills Missing: {result['skills_missing']}")
                st.write(f"- Experience Score: {result['breakdown'].get('exp_score', 0)}/15")
                st.write(f"- Education Score: {result['breakdown'].get('edu_score', 0)}/10")
                st.write(f"- Contact Info Score: {result['breakdown'].get('contact_score', 0)}/10")
                st.write(f"- Keyword Score: {result['breakdown'].get('keyword_score', 0)}/15")
                st.write(f"- Semantic Similarity: {result['breakdown'].get('semantic_similarity', 0):.2f}")
                st.write(f"- Contextual Match Score: {result['breakdown'].get('semantic_score', 0)}/15")
            with col2:
                st.markdown("**Recommendations:**")
                for rec in result['recommendations']:
                    if rec.strip():
                        st.write(f"• {rec.strip()}")
            with st.expander("Resume Preview & Debug (first 500 chars)"):
                st.text(result['resume_text'][:500])
    if skipped_count > 0:
        st.warning(f"{skipped_count} result(s) were skipped due to missing data or errors during processing.") 